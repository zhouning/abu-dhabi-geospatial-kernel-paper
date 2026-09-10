"""Shared action, feasibility and evaluation logic for all three candidates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from sklearn.metrics import f1_score

try:
    from .contract import BenchmarkContractError
except ImportError:  # Direct script execution from the benchmark directory.
    from contract import BenchmarkContractError


CLASSES = tuple(range(1, 7))


def apportion(weights: np.ndarray, total: int) -> np.ndarray:
    values = np.asarray(weights, dtype=np.float64)
    if values.ndim != 1 or np.any(values < 0) or not np.all(np.isfinite(values)):
        raise BenchmarkContractError("invalid_apportionment_weights")
    if total < 0:
        raise BenchmarkContractError("apportionment_total_must_be_nonnegative")
    if values.sum() <= 0:
        values = np.ones_like(values)
    raw = values / values.sum() * total
    result = np.floor(raw).astype(np.int64)
    remainder = int(total - result.sum())
    if remainder:
        order = np.argsort(-(raw - result), kind="stable")
        result[order[:remainder]] += 1
    return result


def feasible_target_counts(
    desired_counts: Mapping[int, int],
    *,
    origin_state: np.ndarray,
    valid_mask: np.ndarray,
    hard_exclusion_mask: np.ndarray,
    classes: Sequence[int] = CLASSES,
    locked_classes: Sequence[int] = (1, 4),
) -> dict[int, int]:
    """Project desired totals onto counts compatible with immutable pixels."""

    origin = np.asarray(origin_state)
    valid = np.asarray(valid_mask, dtype=bool)
    hard = np.asarray(hard_exclusion_mask, dtype=bool)
    if origin.shape != valid.shape or origin.shape != hard.shape:
        raise BenchmarkContractError("feasible_demand_shape_mismatch")
    normalized_classes = tuple(int(value) for value in classes)
    locked = {int(value) for value in locked_classes}
    active = valid & np.isin(origin, normalized_classes)
    fixed = active & hard
    mutable = active & ~hard
    fixed_counts = np.array(
        [np.count_nonzero(fixed & (origin == value)) for value in normalized_classes],
        dtype=np.int64,
    )
    desired = np.array(
        [max(0, int(desired_counts.get(value, 0))) for value in normalized_classes],
        dtype=np.int64,
    )
    mutable_preferences = np.maximum(desired - fixed_counts, 0)
    eligible = np.array([value not in locked for value in normalized_classes], dtype=bool)
    mutable_preferences[~eligible] = 0
    mutable_total = int(mutable.sum())
    if mutable_preferences.sum() == 0:
        mutable_preferences = np.array(
            [np.count_nonzero(mutable & (origin == value)) for value in normalized_classes],
            dtype=np.int64,
        )
        mutable_preferences[~eligible] = 0
    mutable_projection = np.zeros(len(normalized_classes), dtype=np.int64)
    mutable_projection[eligible] = apportion(
        mutable_preferences[eligible], mutable_total
    )
    projected = fixed_counts + mutable_projection
    if int(projected.sum()) != int(active.sum()) or np.any(projected < fixed_counts):
        raise AssertionError("feasible_demand_projection_failed")
    return {value: int(projected[index]) for index, value in enumerate(normalized_classes)}


def class_counts(
    state: np.ndarray,
    valid_mask: np.ndarray,
    classes: Sequence[int] = CLASSES,
) -> dict[int, int]:
    values = np.asarray(state)
    valid = np.asarray(valid_mask, dtype=bool)
    return {int(cls): int(np.count_nonzero(valid & (values == cls))) for cls in classes}


def random_feasible_allocation(
    origin_state: np.ndarray,
    *,
    valid_mask: np.ndarray,
    hard_exclusion_mask: np.ndarray,
    target_counts: Mapping[int, int],
    seed: int,
    classes: Sequence[int] = CLASSES,
) -> np.ndarray:
    """Create a random *minimum-change* map with exact feasible totals.

    A global permutation of all mutable cells is not an informative null for
    land-change allocation: it rewrites stable cells that do not need to
    change.  This control first preserves every mutable cell whose class count
    is already compatible with the target, then randomly pairs only source
    excesses with target deficits.  It is therefore independent of model
    scores while using the smallest possible number of changed cells under the
    oracle target counts.
    """

    origin = np.asarray(origin_state)
    valid = np.asarray(valid_mask, dtype=bool)
    hard = np.asarray(hard_exclusion_mask, dtype=bool)
    if origin.shape != valid.shape or origin.shape != hard.shape:
        raise BenchmarkContractError("random_allocation_shape_mismatch")
    normalized_classes = tuple(int(value) for value in classes)
    active = valid & np.isin(origin, normalized_classes)
    fixed = active & hard
    mutable = active & ~hard
    desired = np.array(
        [int(target_counts.get(value, 0)) for value in normalized_classes],
        dtype=np.int64,
    )
    fixed_counts = np.array(
        [np.count_nonzero(fixed & (origin == value)) for value in normalized_classes],
        dtype=np.int64,
    )
    current_mutable_counts = np.array(
        [np.count_nonzero(mutable & (origin == value)) for value in normalized_classes],
        dtype=np.int64,
    )
    residual = desired - fixed_counts
    if np.any(residual < 0) or int(residual.sum()) != int(mutable.sum()):
        raise BenchmarkContractError("random_allocation_infeasible_target")
    result = origin.copy()
    rng = np.random.default_rng(seed)
    source_indices: list[int] = []
    target_values: list[int] = []
    for index, value in enumerate(normalized_classes):
        excess = max(int(current_mutable_counts[index] - residual[index]), 0)
        deficit = max(int(residual[index] - current_mutable_counts[index]), 0)
        if excess:
            candidates = np.flatnonzero(mutable & (origin == value)).tolist()
            source_indices.extend(rng.permutation(candidates)[:excess].tolist())
        if deficit:
            target_values.extend([value] * deficit)
    if len(source_indices) != len(target_values):
        raise BenchmarkContractError("random_allocation_change_balance_failed")
    if source_indices:
        target_values = rng.permutation(np.asarray(target_values, dtype=np.int64)).tolist()
        for flat_index, target_value in zip(source_indices, target_values, strict=True):
            result.ravel()[flat_index] = target_value
    return result


def evaluate_prediction(
    prediction: np.ndarray,
    *,
    origin_state: np.ndarray,
    observed_target: np.ndarray,
    valid_mask: np.ndarray,
    hard_exclusion_mask: np.ndarray,
    requested_counts: Mapping[int, int],
    reliability_mask: np.ndarray | None = None,
    classes: Sequence[int] = CLASSES,
) -> dict[str, Any]:
    predicted = np.asarray(prediction)
    origin = np.asarray(origin_state)
    target = np.asarray(observed_target)
    valid = np.asarray(valid_mask, dtype=bool)
    hard = np.asarray(hard_exclusion_mask, dtype=bool)
    if not (predicted.shape == origin.shape == target.shape == valid.shape == hard.shape):
        raise BenchmarkContractError("evaluation_shape_mismatch")
    normalized_classes = tuple(int(value) for value in classes)
    evaluation_mask = (
        valid
        & np.isin(origin, normalized_classes)
        & np.isin(target, normalized_classes)
        & np.isin(predicted, normalized_classes)
    )
    result = _metrics(
        predicted,
        origin=origin,
        target=target,
        mask=evaluation_mask,
        classes=normalized_classes,
    )
    if reliability_mask is not None:
        reliable = evaluation_mask & np.asarray(reliability_mask, dtype=bool)
        result["reliability_sensitivity"] = _metrics(
            predicted,
            origin=origin,
            target=target,
            mask=reliable,
            classes=normalized_classes,
        )
    actual_counts = class_counts(predicted, evaluation_mask, normalized_classes)
    requested = {int(key): int(value) for key, value in requested_counts.items()}
    total = max(1, int(evaluation_mask.sum()))
    result.update(
        {
            "evaluation_pixel_count": int(evaluation_mask.sum()),
            "constraint_violation_pixels": int(
                np.count_nonzero(evaluation_mask & hard & (predicted != origin))
            ),
            "constraint_violation_rate": float(
                np.count_nonzero(evaluation_mask & hard & (predicted != origin)) / total
            ),
            "actual_class_counts": {str(key): value for key, value in actual_counts.items()},
            "requested_class_counts": {str(key): value for key, value in requested.items()},
            "demand_l1_error_pixels": int(
                sum(
                    abs(actual_counts.get(cls, 0) - requested.get(cls, 0))
                    for cls in normalized_classes
                )
            ),
            "demand_total_variation": float(
                sum(
                    abs(actual_counts.get(cls, 0) - requested.get(cls, 0))
                    for cls in normalized_classes
                )
                / (2 * total)
            ),
        }
    )
    result["demand_target_exact"] = result["demand_l1_error_pixels"] == 0
    return result


def _metrics(
    prediction: np.ndarray,
    *,
    origin: np.ndarray,
    target: np.ndarray,
    mask: np.ndarray,
    classes: tuple[int, ...],
) -> dict[str, Any]:
    count = int(mask.sum())
    if count <= 0:
        raise BenchmarkContractError("evaluation_mask_is_empty")
    predicted_values = prediction[mask]
    origin_values = origin[mask]
    target_values = target[mask]
    predicted_change = predicted_values != origin_values
    observed_change = target_values != origin_values
    transition_hits = observed_change & predicted_change & (predicted_values == target_values)
    wrong_changes = observed_change & predicted_change & (predicted_values != target_values)
    misses = ~predicted_change & observed_change
    false_alarms = predicted_change & ~observed_change
    denominator = int(
        np.count_nonzero(transition_hits)
        + np.count_nonzero(wrong_changes)
        + np.count_nonzero(misses)
        + np.count_nonzero(false_alarms)
    )
    change_fom = float(np.count_nonzero(transition_hits) / denominator) if denominator else 1.0
    binary_hits = int(np.count_nonzero(predicted_change & observed_change))
    binary_denominator = binary_hits + int(np.count_nonzero(misses)) + int(np.count_nonzero(false_alarms))
    binary_change_fom = float(binary_hits / binary_denominator) if binary_denominator else 1.0
    change_f1 = float(
        f1_score(observed_change, predicted_change, zero_division=1)
    )
    return {
        "pixel_count": count,
        "overall_accuracy": float(np.mean(prediction[mask] == target[mask])),
        "macro_f1": float(
            f1_score(
                target[mask],
                prediction[mask],
                labels=list(classes),
                average="macro",
                zero_division=0,
            )
        ),
        "change_figure_of_merit": change_fom,
        "binary_change_figure_of_merit": binary_change_fom,
        "change_f1": change_f1,
        "change_hits": int(np.count_nonzero(transition_hits)),
        "change_wrong_transitions": int(np.count_nonzero(wrong_changes)),
        "change_misses": int(np.count_nonzero(misses)),
        "change_false_alarms": int(np.count_nonzero(false_alarms)),
        "predicted_change_pixels": int(predicted_change.sum()),
        "observed_change_pixels": int(observed_change.sum()),
    }


def spatial_block_bootstrap_ci(
    prediction: np.ndarray,
    *,
    origin_state: np.ndarray,
    observed_target: np.ndarray,
    valid_mask: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
    block_size: int = 8,
    classes: Sequence[int] = CLASSES,
) -> dict[str, Any]:
    """Bootstrap spatial blocks jointly for strict FoM, OA and macro-F1.

    Pixels in the same ``block_size × block_size`` tile are sampled together,
    preserving some spatial autocorrelation.  This is a computational
    uncertainty interval for the mapped domain, not a population interval.
    The block size is recorded in the result and should be prespecified before
    comparing models.
    """

    predicted = np.asarray(prediction)
    origin = np.asarray(origin_state)
    target = np.asarray(observed_target)
    valid = np.asarray(valid_mask, dtype=bool)
    if not (predicted.shape == origin.shape == target.shape == valid.shape):
        raise BenchmarkContractError("bootstrap_shape_mismatch")
    if n_resamples < 100 or not 0 < alpha < 1 or block_size < 1:
        raise BenchmarkContractError("bootstrap_parameters_invalid")
    normalized_classes = tuple(int(value) for value in classes)
    mask = valid & np.isin(origin, normalized_classes) & np.isin(target, normalized_classes)
    mask &= np.isin(predicted, normalized_classes)
    pred_values = predicted[mask]
    origin_values = origin[mask]
    target_values = target[mask]
    count = int(mask.sum())
    if count == 0:
        raise BenchmarkContractError("bootstrap_mask_is_empty")

    block_rows = np.arange(predicted.shape[0])[:, None] // int(block_size)
    block_cols = np.arange(predicted.shape[1])[None, :] // int(block_size)
    block_ids = block_rows * int(block_cols.max() + 1) + block_cols
    selected_blocks = block_ids[mask]
    unique_blocks, inverse = np.unique(selected_blocks, return_inverse=True)
    class_count = len(normalized_classes)
    class_lookup = {value: index for index, value in enumerate(normalized_classes)}
    confusion_size = class_count * class_count
    block_joint_counts = np.zeros(
        (len(unique_blocks), 5 * confusion_size), dtype=np.int64
    )
    observed_change = target_values != origin_values
    predicted_change = pred_values != origin_values
    transition_hits = observed_change & predicted_change & (pred_values == target_values)
    wrong_changes = observed_change & predicted_change & (pred_values != target_values)
    misses = ~predicted_change & observed_change
    false_alarms = predicted_change & ~observed_change
    change_codes = (
        transition_hits.astype(np.int8)
        + 2 * wrong_changes.astype(np.int8)
        + 3 * misses.astype(np.int8)
        + 4 * false_alarms.astype(np.int8)
    )
    confusion_codes = np.array(
        [
            class_lookup[int(t)] * class_count + class_lookup[int(p)]
            for t, p in zip(target_values, pred_values, strict=True)
        ],
        dtype=np.int64,
    )
    joint_codes = change_codes.astype(np.int64) * confusion_size + confusion_codes
    for block_index in range(len(unique_blocks)):
        block_joint_counts[block_index] = np.bincount(
            joint_codes[inverse == block_index], minlength=5 * confusion_size
        )
    rng = np.random.default_rng(seed)
    fom_values = np.empty(n_resamples, dtype=np.float64)
    oa_values = np.empty(n_resamples, dtype=np.float64)
    macro_values = np.empty(n_resamples, dtype=np.float64)
    for index in range(n_resamples):
        block_weights = rng.multinomial(
            len(unique_blocks),
            np.full(len(unique_blocks), 1.0 / len(unique_blocks)),
        )
        joint_counts = (block_weights @ block_joint_counts).reshape(
            5, class_count, class_count
        )
        resampled_count = int(joint_counts.sum())
        change_counts = joint_counts.sum(axis=(1, 2))
        hit, wrong, miss, false_alarm = (
            change_counts[1],
            change_counts[2],
            change_counts[3],
            change_counts[4],
        )
        denominator = int(hit + wrong + miss + false_alarm)
        fom_values[index] = float(hit / denominator) if denominator else 1.0
        confusion = joint_counts.sum(axis=0)
        oa_values[index] = float(np.trace(confusion) / max(1, resampled_count))
        diagonal = np.diag(confusion).astype(np.float64)
        precision_denominator = confusion.sum(axis=0)
        recall_denominator = confusion.sum(axis=1)
        f1 = np.divide(
            2 * diagonal,
            precision_denominator + recall_denominator,
            out=np.zeros(class_count, dtype=np.float64),
            where=(precision_denominator + recall_denominator) > 0,
        )
        macro_values[index] = float(np.mean(f1))

    lower = 100 * alpha / 2
    upper = 100 * (1 - alpha / 2)
    return {
        "method": "spatial_block_bootstrap",
        "sampling_unit": "spatial_block_triplet_origin_prediction_target",
        "n_resamples": int(n_resamples),
        "seed": int(seed),
        "alpha": float(alpha),
        "pixel_count": count,
        "block_size_pixels": int(block_size),
        "block_count": int(len(unique_blocks)),
        "change_figure_of_merit": {
            "lower": float(np.percentile(fom_values, lower)),
            "median": float(np.percentile(fom_values, 50)),
            "upper": float(np.percentile(fom_values, upper)),
        },
        "overall_accuracy": {
            "lower": float(np.percentile(oa_values, lower)),
            "median": float(np.percentile(oa_values, 50)),
            "upper": float(np.percentile(oa_values, upper)),
        },
        "macro_f1": {
            "lower": float(np.percentile(macro_values, lower)),
            "median": float(np.percentile(macro_values, 50)),
            "upper": float(np.percentile(macro_values, upper)),
        },
    }


def paired_pixel_bootstrap_ci(
    prediction: np.ndarray,
    *,
    origin_state: np.ndarray,
    observed_target: np.ndarray,
    valid_mask: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
    block_size: int = 8,
    classes: Sequence[int] = CLASSES,
) -> dict[str, Any]:
    """Backward-compatible alias for :func:`spatial_block_bootstrap_ci`.

    The historical function name is retained for downstream scripts, but it
    now performs spatial-block rather than independent-pixel resampling.
    """

    return spatial_block_bootstrap_ci(
        prediction,
        origin_state=origin_state,
        observed_target=observed_target,
        valid_mask=valid_mask,
        n_resamples=n_resamples,
        seed=seed,
        alpha=alpha,
        block_size=block_size,
        classes=classes,
    )


def paired_model_difference_bootstrap_ci(
    prediction_a: np.ndarray,
    prediction_b: np.ndarray,
    *,
    origin_state: np.ndarray,
    observed_target: np.ndarray,
    valid_mask: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
    block_size: int = 8,
    classes: Sequence[int] = CLASSES,
) -> dict[str, Any]:
    """Estimate paired model differences using the same sampled spatial blocks."""

    first = np.asarray(prediction_a)
    second = np.asarray(prediction_b)
    origin = np.asarray(origin_state)
    target = np.asarray(observed_target)
    valid = np.asarray(valid_mask, dtype=bool)
    if not (first.shape == second.shape == origin.shape == target.shape == valid.shape):
        raise BenchmarkContractError("bootstrap_shape_mismatch")
    if n_resamples < 100 or not 0 < alpha < 1 or block_size < 1:
        raise BenchmarkContractError("bootstrap_parameters_invalid")
    normalized_classes = tuple(int(value) for value in classes)
    mask = (
        valid
        & np.isin(origin, normalized_classes)
        & np.isin(target, normalized_classes)
        & np.isin(first, normalized_classes)
        & np.isin(second, normalized_classes)
    )
    if not np.any(mask):
        raise BenchmarkContractError("bootstrap_mask_is_empty")
    block_rows = np.arange(first.shape[0])[:, None] // int(block_size)
    block_cols = np.arange(first.shape[1])[None, :] // int(block_size)
    block_ids = block_rows * int(block_cols.max() + 1) + block_cols
    selected_blocks = block_ids[mask]
    unique_blocks, inverse = np.unique(selected_blocks, return_inverse=True)
    class_count = len(normalized_classes)
    class_lookup = {value: index for index, value in enumerate(normalized_classes)}
    confusion_size = class_count * class_count

    def block_tables(prediction: np.ndarray) -> np.ndarray:
        pred_values = prediction[mask]
        origin_values = origin[mask]
        target_values = target[mask]
        observed_change = target_values != origin_values
        predicted_change = pred_values != origin_values
        hits = observed_change & predicted_change & (pred_values == target_values)
        wrong = observed_change & predicted_change & (pred_values != target_values)
        misses = ~predicted_change & observed_change
        false_alarms = predicted_change & ~observed_change
        change_codes = (
            hits.astype(np.int8)
            + 2 * wrong.astype(np.int8)
            + 3 * misses.astype(np.int8)
            + 4 * false_alarms.astype(np.int8)
        )
        confusion_codes = np.array(
            [
                class_lookup[int(t)] * class_count + class_lookup[int(p)]
                for t, p in zip(target_values, pred_values, strict=True)
            ],
            dtype=np.int64,
        )
        codes = change_codes.astype(np.int64) * confusion_size + confusion_codes
        tables = np.zeros((len(unique_blocks), 5 * confusion_size), dtype=np.int64)
        for block_index in range(len(unique_blocks)):
            tables[block_index] = np.bincount(
                codes[inverse == block_index], minlength=5 * confusion_size
            )
        return tables

    tables_a = block_tables(first)
    tables_b = block_tables(second)

    def metrics(table: np.ndarray) -> tuple[float, float, float]:
        joint = table.reshape(5, class_count, class_count)
        changes = joint.sum(axis=(1, 2))
        hit, wrong, miss, false_alarm = changes[1:]
        fom_denominator = hit + wrong + miss + false_alarm
        fom = float(hit / fom_denominator) if fom_denominator else 1.0
        confusion = joint.sum(axis=0)
        total = max(1, int(confusion.sum()))
        oa = float(np.trace(confusion) / total)
        diagonal = np.diag(confusion).astype(np.float64)
        precision_denominator = confusion.sum(axis=0)
        recall_denominator = confusion.sum(axis=1)
        f1 = np.divide(
            2 * diagonal,
            precision_denominator + recall_denominator,
            out=np.zeros(class_count, dtype=np.float64),
            where=(precision_denominator + recall_denominator) > 0,
        )
        return fom, oa, float(np.mean(f1))

    rng = np.random.default_rng(seed)
    differences = np.empty((n_resamples, 3), dtype=np.float64)
    for index in range(n_resamples):
        weights = rng.multinomial(
            len(unique_blocks), np.full(len(unique_blocks), 1.0 / len(unique_blocks))
        )
        differences[index] = np.subtract(
            metrics(weights @ tables_a), metrics(weights @ tables_b)
        )
    lower = 100 * alpha / 2
    upper = 100 * (1 - alpha / 2)
    names = ("change_figure_of_merit", "overall_accuracy", "macro_f1")
    return {
        "method": "paired_spatial_block_bootstrap_difference",
        "sampling_unit": "shared_spatial_block_triplets",
        "comparison": "prediction_a_minus_prediction_b",
        "n_resamples": int(n_resamples),
        "seed": int(seed),
        "alpha": float(alpha),
        "pixel_count": int(mask.sum()),
        "block_size_pixels": int(block_size),
        "block_count": int(len(unique_blocks)),
        **{
            name: {
                "lower": float(np.percentile(differences[:, index], lower)),
                "median": float(np.percentile(differences[:, index], 50)),
                "upper": float(np.percentile(differences[:, index], upper)),
            }
            for index, name in enumerate(names)
        },
    }
