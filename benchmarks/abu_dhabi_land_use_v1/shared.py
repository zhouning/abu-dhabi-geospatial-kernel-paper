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
    """Create a reproducible random categorical map with exact feasible totals.

    The random control is deliberately independent of model scores.  Pixels in
    the hard mask retain their origin class; all mutable valid pixels are
    uniformly permuted and assigned the requested residual class totals.
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
    residual = desired - fixed_counts
    if np.any(residual < 0) or int(residual.sum()) != int(mutable.sum()):
        raise BenchmarkContractError("random_allocation_infeasible_target")
    result = origin.copy()
    mutable_indices = np.flatnonzero(mutable.ravel())
    permutation = np.random.default_rng(seed).permutation(mutable_indices)
    cursor = 0
    for value, count in zip(normalized_classes, residual, strict=True):
        next_cursor = cursor + int(count)
        result.ravel()[permutation[cursor:next_cursor]] = value
        cursor = next_cursor
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


def paired_pixel_bootstrap_ci(
    prediction: np.ndarray,
    *,
    origin_state: np.ndarray,
    observed_target: np.ndarray,
    valid_mask: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
    classes: Sequence[int] = CLASSES,
) -> dict[str, Any]:
    """Bootstrap pixel triplets jointly for strict FoM, OA and macro-F1.

    Each resample is equivalent to drawing valid pixel indices with
    replacement while carrying ``(origin, prediction, target)`` together.
    The implementation samples the joint contingency table, which is the
    count-equivalent form of paired pixel resampling and avoids materialising
    an ``n_resamples × n_pixels`` index matrix.  The result is an uncertainty
    interval for computational agreement, not an independent-sample interval
    for a geographic population.
    """

    predicted = np.asarray(prediction)
    origin = np.asarray(origin_state)
    target = np.asarray(observed_target)
    valid = np.asarray(valid_mask, dtype=bool)
    if not (predicted.shape == origin.shape == target.shape == valid.shape):
        raise BenchmarkContractError("bootstrap_shape_mismatch")
    if n_resamples < 100 or not 0 < alpha < 1:
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
    class_count = len(normalized_classes)
    class_lookup = {value: index for index, value in enumerate(normalized_classes)}
    confusion_codes = np.array(
        [class_lookup[int(t)] * class_count + class_lookup[int(p)] for t, p in zip(target_values, pred_values)],
        dtype=np.int64,
    )
    # A single joint table preserves the pairing between the change
    # categories and the target/prediction confusion cells.  Sampling the two
    # marginal tables independently would no longer be a paired bootstrap.
    confusion_size = class_count * class_count
    joint_codes = change_codes.astype(np.int64) * confusion_size + confusion_codes
    joint_probabilities = np.bincount(
        joint_codes, minlength=5 * confusion_size
    ).astype(np.float64) / count
    rng = np.random.default_rng(seed)
    fom_values = np.empty(n_resamples, dtype=np.float64)
    oa_values = np.empty(n_resamples, dtype=np.float64)
    macro_values = np.empty(n_resamples, dtype=np.float64)
    for index in range(n_resamples):
        joint_counts = rng.multinomial(count, joint_probabilities).reshape(
            5, class_count, class_count
        )
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
        oa_values[index] = float(np.trace(confusion) / count)
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
        "method": "paired_pixel_bootstrap",
        "sampling_unit": "pixel_triplet_origin_prediction_target",
        "n_resamples": int(n_resamples),
        "seed": int(seed),
        "alpha": float(alpha),
        "pixel_count": count,
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
