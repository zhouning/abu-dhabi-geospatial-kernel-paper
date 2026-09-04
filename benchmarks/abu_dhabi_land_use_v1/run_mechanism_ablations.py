#!/usr/bin/env python3
"""Run mechanism-focused controls for the Abu Dhabi public-data benchmark.

The controls are deliberately bounded: they test proposal features and
runtime allocation semantics on the same public-data benchmark. They do not
establish causal effects or validate official Abu Dhabi land-use forecasts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import rasterio

try:
    from .run_geospatial_kernel import (
        AbuDhabiInputs,
        CLASSES,
        FIT_TRANSITIONS,
        SEEDS,
        _load_actions,
        allocate_action,
        probability_cube,
        train_kernel,
    )
    from .planning import planning_metrics
    from .shared import class_counts, evaluate_prediction, feasible_target_counts
except ImportError:
    from run_geospatial_kernel import (
        AbuDhabiInputs,
        CLASSES,
        FIT_TRANSITIONS,
        SEEDS,
        _load_actions,
        allocate_action,
        probability_cube,
        train_kernel,
    )
    from planning import planning_metrics
    from shared import class_counts, evaluate_prediction, feasible_target_counts

from sklearn.ensemble import HistGradientBoostingClassifier

HERE = Path(__file__).resolve().parent
BUNDLE_ROOT = HERE / "artifacts/bundle"
DEFAULT_OUTPUT = HERE / "artifacts/mechanism_ablations"
_MODEL_CACHE: dict[tuple[int, str], tuple[HistGradientBoostingClassifier, dict[str, Any]]] = {}


PROPOSAL_VARIANTS = (
    "full",
    "no_neighborhood_features",
    "no_spatial_drivers",
    "state_only",
    "shuffle_spatial_drivers",
    "markov",
    "random",
)


def _features(
    inputs: AbuDhabiInputs,
    state: np.ndarray,
    *,
    driver_year: int,
    variant: str,
    permutation: np.ndarray | None = None,
) -> np.ndarray:
    """Return feature matrix with a declared proposal ablation."""

    full = inputs.features(state, driver_year=driver_year)
    if variant == "full":
        return full
    if variant == "no_neighborhood_features":
        return np.concatenate([full[:6], full[18:]], axis=0)
    if variant == "no_spatial_drivers":
        return full[:18]
    if variant == "state_only":
        return full[:6]
    if variant == "shuffle_spatial_drivers":
        if permutation is None:
            raise ValueError("shuffle_spatial_drivers_requires_permutation")
        result = full.copy()
        continuous = full[18:].reshape(7, -1)
        result_continuous = continuous.copy()
        valid_indices = np.flatnonzero(inputs.valid.ravel())
        result_continuous[:, valid_indices] = continuous[:, permutation]
        result[18:] = result_continuous.reshape(7, *state.shape)
        result[18:, ~inputs.valid] = 0.0
        return result
    raise ValueError(f"unknown_proposal_variant:{variant}")


def _train_variant(
    inputs: AbuDhabiInputs,
    *,
    seed: int,
    variant: str,
    permutation: np.ndarray | None = None,
) -> tuple[HistGradientBoostingClassifier, dict[str, Any]]:
    """Train the same learner with a controlled feature block."""

    rng = np.random.default_rng(seed)
    feature_rows: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    weights: list[np.ndarray] = []
    transition_rows: list[dict[str, Any]] = []
    for start_year, target_year in FIT_TRANSITIONS:
        start = inputs.states[start_year]
        target = inputs.states[target_year]
        features = _features(
            inputs,
            start,
            driver_year=start_year,
            variant=variant,
            permutation=permutation,
        )
        changed = inputs.valid & (start != target)
        selected = inputs.valid & (changed | (rng.random(start.shape) < 0.20))
        feature_rows.append(features[:, selected].T)
        labels.append(target[selected].astype(np.int64))
        confidence = np.minimum(
            inputs.quality[start_year][selected],
            inputs.quality[target_year][selected]
        )
        weights.append((1.0 + 5.0 * changed[selected]) * (0.5 + np.clip(confidence, 0, 1)))
        transition_rows.append(
            {
                "start_year": start_year,
                "target_year": target_year,
                "selected_pixels": int(selected.sum()),
                "selected_changed_pixels": int(changed[selected].sum()),
            }
        )
    x = np.concatenate(feature_rows)
    y = np.concatenate(labels)
    sample_weight = np.concatenate(weights)
    model = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=120,
        max_leaf_nodes=31,
        min_samples_leaf=40,
        l2_regularization=1.0,
        random_state=seed,
    )
    model.fit(x, y, sample_weight=sample_weight)
    return model, {
        "seed": seed,
        "variant": variant,
        "training_pixel_rows": int(len(x)),
        "feature_count": int(x.shape[1]),
        "fit_transitions": transition_rows,
    }


def _probability_cube_variant(
    model: HistGradientBoostingClassifier,
    inputs: AbuDhabiInputs,
    state: np.ndarray,
    *,
    driver_year: int,
    variant: str,
    permutation: np.ndarray | None = None,
    rng: np.random.Generator | None = None,
    markov_matrix: np.ndarray | None = None,
) -> np.ndarray:
    if variant == "markov":
        if markov_matrix is None:
            raise ValueError("markov_requires_matrix")
        cube = np.full((len(CLASSES), *state.shape), 1e-9, dtype=np.float32)
        for source in CLASSES:
            mask = inputs.valid & (state == source)
            cube[:, mask] = markov_matrix[source - 1][:, None]
        return cube / cube.sum(axis=0, keepdims=True)
    if variant == "random":
        if rng is None:
            raise ValueError("random_requires_rng")
        cube = rng.random((len(CLASSES), *state.shape), dtype=np.float32) + 1e-3
        cube[:, ~inputs.valid] = 1e-9
        return cube / cube.sum(axis=0, keepdims=True)
    features = _features(
        inputs,
        state,
        driver_year=driver_year,
        variant=variant,
        permutation=permutation,
    )
    probability = model.predict_proba(features[:, inputs.valid].T)
    cube = np.full((len(CLASSES), *state.shape), 1e-9, dtype=np.float32)
    for column, value in enumerate(model.classes_):
        cube[int(value) - 1][inputs.valid] = probability[:, column]
    return cube / cube.sum(axis=0, keepdims=True)


def _markov_matrix(inputs: AbuDhabiInputs) -> np.ndarray:
    counts = np.ones((len(CLASSES), len(CLASSES)), dtype=np.float64)
    for start_year, target_year in FIT_TRANSITIONS:
        start = inputs.states[start_year]
        target = inputs.states[target_year]
        mask = inputs.valid
        for source in CLASSES:
            for destination in CLASSES:
                counts[source - 1, destination - 1] += np.count_nonzero(
                    mask & (start == source) & (target == destination)
                )
    return counts / counts.sum(axis=1, keepdims=True)


def _cached_model(
    inputs: AbuDhabiInputs,
    *,
    seed: int,
    variant: str,
    permutation: np.ndarray | None,
) -> HistGradientBoostingClassifier:
    key = (seed, variant)
    if key not in _MODEL_CACHE:
        _MODEL_CACHE[key] = _train_variant(
            inputs,
            seed=seed,
            variant=variant,
            permutation=permutation,
        )
    return _MODEL_CACHE[key][0]


def _action_with_counts(action: dict[str, Any], counts: dict[int, int]) -> dict[str, Any]:
    result = dict(action)
    result["feasible_target_counts"] = {str(key): int(value) for key, value in counts.items()}
    return result


def _run_historical_seed(
    inputs: AbuDhabiInputs,
    *,
    seed: int,
    proposal_variant: str,
    runtime_variant: str,
    action_mode: str,
    writeback: bool,
    neighborhood_weight: float,
    hard_constraints: bool,
) -> list[dict[str, Any]]:
    valid_flat = np.flatnonzero(inputs.valid.ravel())
    permutation = None
    if proposal_variant == "shuffle_spatial_drivers":
        permutation = np.random.default_rng(seed + 1000).permutation(valid_flat)
    markov = _markov_matrix(inputs)
    model = None
    if proposal_variant not in {"markov", "random"}:
        model = _cached_model(
            inputs,
            seed=seed,
            variant=proposal_variant,
            permutation=permutation,
        )
    rng = np.random.default_rng(seed + 2000)
    actions = _load_actions()
    origin = inputs.states[2022].copy()
    current = origin.copy()
    results: list[dict[str, Any]] = []
    for index, action in enumerate(actions):
        source_state = current if writeback else origin
        if action_mode == "shuffled":
            action_used = actions[1 - index]
        else:
            action_used = action
        if model is not None:
            probability = _probability_cube_variant(
                model,
                inputs,
                source_state,
                driver_year=2022,
                variant=proposal_variant,
                permutation=permutation,
            )
        else:
            probability = _probability_cube_variant(
                model,  # type: ignore[arg-type]
                inputs,
                source_state,
                driver_year=2022,
                variant=proposal_variant,
                rng=rng,
                markov_matrix=markov,
            )
        if action_mode == "deleted":
            argmax_state = np.argmax(probability, axis=0).astype(np.uint8) + 1
            target_counts = class_counts(argmax_state, inputs.valid)
            target_counts = feasible_target_counts(
                target_counts,
                origin_state=source_state,
                valid_mask=inputs.valid,
                hard_exclusion_mask=inputs.hard[2022] if hard_constraints else np.zeros_like(inputs.valid),
            )
            action_used = _action_with_counts(action_used, target_counts)
        target_counts = {int(key): int(value) for key, value in action_used["feasible_target_counts"].items()}
        hard = inputs.hard[2022] if hard_constraints else np.zeros_like(inputs.valid)
        try:
            prediction, allocation = allocate_action(
                source_state,
                probability,
                valid=inputs.valid,
                hard=hard,
                target_counts=target_counts,
                neighborhood_weight=neighborhood_weight,
            )
            status = "complete"
            error = None
        except Exception as exc:  # record infeasible controls instead of hiding them
            prediction = source_state.copy()
            allocation = {}
            status = "infeasible"
            error = f"{type(exc).__name__}:{exc}"
        if writeback:
            current = prediction
        if status == "complete":
            with rasterio.open(HERE / action["reliability_mask"]) as dataset:
                reliability = dataset.read(1)
            evaluation = evaluate_prediction(
                prediction,
                origin_state=origin,
                observed_target=inputs.states[int(action["target_year"])],
                valid_mask=inputs.valid,
                hard_exclusion_mask=inputs.hard[2022],
                requested_counts=target_counts,
                # Reliability subsets can be empty for deleted/shuffled-action
                # controls; the mechanism table uses the full-grid metrics.
                reliability_mask=None,
            )
        else:
            evaluation = {
                "change_figure_of_merit": float("nan"),
                "change_f1": float("nan"),
                "overall_accuracy": float("nan"),
                "macro_f1": float("nan"),
                "demand_total_variation": float("nan"),
                "constraint_violation_rate": float("nan"),
            }
        results.append(
            {
                "seed": seed,
                "proposal_variant": proposal_variant,
                "runtime_variant": runtime_variant,
                "action_mode": action_mode,
                "writeback": writeback,
                "neighborhood_weight": neighborhood_weight,
                "hard_constraints": hard_constraints,
                "target_year": int(action["target_year"]),
                "status": status,
                "error": error,
                "allocation": allocation,
                "evaluation": evaluation,
            }
        )
    return results


def _planning_seed(
    inputs: AbuDhabiInputs,
    *,
    seed: int,
    proposal_variant: str,
    runtime_variant: str,
    writeback: bool,
    neighborhood_weight: float,
    hard_constraints: bool,
) -> list[dict[str, Any]]:
    scenario_set = json.loads(
        (BUNDLE_ROOT / "planning_scenarios_public_2025_2031.json").read_text()
    )
    scenarios = scenario_set["scenarios"]
    valid_flat = np.flatnonzero(inputs.valid.ravel())
    permutation = None
    if proposal_variant == "shuffle_spatial_drivers":
        permutation = np.random.default_rng(seed + 3000).permutation(valid_flat)
    markov = _markov_matrix(inputs)
    model = None
    if proposal_variant not in {"markov", "random"}:
        model = _cached_model(
            inputs,
            seed=seed,
            variant=proposal_variant,
            permutation=permutation,
        )
    rng = np.random.default_rng(seed + 4000)
    outputs: list[dict[str, Any]] = []
    for scenario in scenarios:
        origin = inputs.states[2024].copy()
        current = origin.copy()
        for year_text, counts_raw in scenario["target_counts_by_year"].items():
            year = int(year_text)
            source = current if writeback else origin
            if model is not None:
                probability = _probability_cube_variant(
                    model,
                    inputs,
                    source,
                    driver_year=2024,
                    variant=proposal_variant,
                    permutation=permutation,
                )
            else:
                probability = _probability_cube_variant(
                    model,  # type: ignore[arg-type]
                    inputs,
                    source,
                    driver_year=2024,
                    variant=proposal_variant,
                    rng=rng,
                    markov_matrix=markov,
                )
            hard = inputs.hard[2024] if hard_constraints else np.zeros_like(inputs.valid)
            target_counts = {int(key): int(value) for key, value in counts_raw.items()}
            try:
                next_state, _ = allocate_action(
                    source,
                    probability,
                    valid=inputs.valid,
                    hard=hard,
                    target_counts=target_counts,
                    neighborhood_weight=neighborhood_weight,
                )
                status = "complete"
                error = None
            except Exception as exc:
                next_state = source.copy()
                status = "infeasible"
                error = f"{type(exc).__name__}:{exc}"
            if writeback:
                current = next_state
            if year == 2031:
                metrics = planning_metrics(
                    next_state,
                    origin_state=origin,
                    valid_mask=inputs.valid,
                    hard_exclusion_mask=inputs.hard[2024],
                    target_counts=target_counts,
                    road_distance_m=inputs.road_distance,
                    major_road_distance_m=inputs.major_road_distance,
                )
                outputs.append(
                    {
                        "seed": seed,
                        "proposal_variant": proposal_variant,
                        "runtime_variant": runtime_variant,
                        "writeback": writeback,
                        "neighborhood_weight": neighborhood_weight,
                        "hard_constraints": hard_constraints,
                        "scenario_id": scenario["scenario_id"],
                        "target_year": year,
                        "status": status,
                        "error": error,
                        "metrics": metrics,
                    }
                )
    return outputs


def run(*, output_root: Path, seeds: tuple[int, ...]) -> dict[str, Any]:
    inputs = AbuDhabiInputs()
    historical: list[dict[str, Any]] = []
    planning: list[dict[str, Any]] = []
    # Proposal controls use the same exact allocator and hard constraints.
    for variant in PROPOSAL_VARIANTS:
        for seed in seeds:
            historical.extend(
                _run_historical_seed(
                    inputs,
                    seed=seed,
                    proposal_variant=variant,
                    runtime_variant="shared_allocator",
                    action_mode="observed",
                    writeback=True,
                    neighborhood_weight=0.35,
                    hard_constraints=True,
                )
            )
    # Runtime controls use the full proposal unless the control explicitly changes it.
    runtime_controls = (
        {"name": "full", "action_mode": "observed", "writeback": True, "neighborhood_weight": 0.35, "hard_constraints": True},
        {"name": "action_deleted", "action_mode": "deleted", "writeback": True, "neighborhood_weight": 0.35, "hard_constraints": True},
        {"name": "action_shuffled", "action_mode": "shuffled", "writeback": True, "neighborhood_weight": 0.35, "hard_constraints": True},
        {"name": "constraint_deleted", "action_mode": "observed", "writeback": True, "neighborhood_weight": 0.35, "hard_constraints": False},
        {"name": "allocation_neighborhood_deleted", "action_mode": "observed", "writeback": True, "neighborhood_weight": 0.0, "hard_constraints": True},
        {"name": "state_writeback_deleted", "action_mode": "observed", "writeback": False, "neighborhood_weight": 0.35, "hard_constraints": True},
    )
    for control in runtime_controls:
        for seed in seeds:
            historical.extend(
                _run_historical_seed(
                    inputs,
                    seed=seed,
                    proposal_variant="full",
                    runtime_variant=control["name"],
                    action_mode=control["action_mode"],
                    writeback=control["writeback"],
                    neighborhood_weight=control["neighborhood_weight"],
                    hard_constraints=control["hard_constraints"],
                )
            )
    planning_controls = (
        {"name": "full", "proposal_variant": "full", "writeback": True, "neighborhood_weight": 0.35, "hard_constraints": True},
        {"name": "markov_proposal", "proposal_variant": "markov", "writeback": True, "neighborhood_weight": 0.35, "hard_constraints": True},
        {"name": "allocation_neighborhood_deleted", "proposal_variant": "full", "writeback": True, "neighborhood_weight": 0.0, "hard_constraints": True},
        {"name": "constraint_deleted", "proposal_variant": "full", "writeback": True, "neighborhood_weight": 0.35, "hard_constraints": False},
        {"name": "state_writeback_deleted", "proposal_variant": "full", "writeback": False, "neighborhood_weight": 0.35, "hard_constraints": True},
    )
    for control in planning_controls:
        for seed in seeds:
            planning.extend(
                _planning_seed(
                    inputs,
                    seed=seed,
                    proposal_variant=control["proposal_variant"],
                    runtime_variant=control["name"],
                    writeback=control["writeback"],
                    neighborhood_weight=control["neighborhood_weight"],
                    hard_constraints=control["hard_constraints"],
                )
            )
    report = {
        "schema": "gwm.abu_dhabi_mechanism_ablations.v1",
        "benchmark_id": "abu-dhabi-land-use-v1",
        "status": "complete",
        "seeds": list(seeds),
        "historical": historical,
        "planning_2031": planning,
        "claim_boundary": [
            "Public-data mechanism controls on a 100-m land-cover benchmark.",
            "Controls do not establish causal policy effects or official forecasts.",
            "Action and demand controls intentionally test the declared execution contract.",
        ],
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default=",".join(str(value) for value in SEEDS))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    seeds = tuple(int(value) for value in args.seeds.split(",") if value.strip())
    report = run(output_root=args.output, seeds=seeds)
    print(
        json.dumps(
            {
                "status": report["status"],
                "historical_rows": len(report["historical"]),
                "planning_rows": len(report["planning_2031"]),
                "output": str(args.output / "report.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
