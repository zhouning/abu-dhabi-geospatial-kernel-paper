import numpy as np

from benchmarks.abu_dhabi_land_use_v1.shared import (
    evaluate_prediction,
    paired_pixel_bootstrap_ci,
    random_feasible_allocation,
)
from benchmarks.abu_dhabi_land_use_v1.planning import planning_metrics


def _fixture():
    origin = np.array([[1, 2, 3, 4], [5, 6, 5, 6]], dtype=np.uint8)
    target = np.array([[1, 5, 5, 4], [5, 3, 5, 2]], dtype=np.uint8)
    valid = np.ones_like(origin, dtype=bool)
    hard = np.array([[1, 0, 0, 1], [0, 0, 0, 0]], dtype=bool)
    counts = {value: int(np.count_nonzero(target == value)) for value in range(1, 7)}
    return origin, target, valid, hard, counts


def test_strict_fom_counts_wrong_destination_changes():
    origin, target, valid, hard, counts = _fixture()
    prediction = np.array([[1, 3, 5, 4], [5, 5, 2, 5]], dtype=np.uint8)
    result = evaluate_prediction(
        prediction,
        origin_state=origin,
        observed_target=target,
        valid_mask=valid,
        hard_exclusion_mask=hard,
        requested_counts=counts,
    )
    assert result["change_figure_of_merit"] < result["binary_change_figure_of_merit"]
    assert result["change_wrong_transitions"] == 3


def test_random_feasible_allocation_preserves_counts_and_hard_cells():
    origin, target, valid, hard, counts = _fixture()
    prediction = random_feasible_allocation(
        origin,
        valid_mask=valid,
        hard_exclusion_mask=hard,
        target_counts=counts,
        seed=42,
    )
    assert np.array_equal(prediction[hard], origin[hard])
    assert {value: int(np.count_nonzero(prediction == value)) for value in range(1, 7)} == counts


def test_paired_pixel_bootstrap_is_reproducible():
    origin, target, valid, hard, counts = _fixture()
    prediction = random_feasible_allocation(
        origin,
        valid_mask=valid,
        hard_exclusion_mask=hard,
        target_counts=counts,
        seed=42,
    )
    first = paired_pixel_bootstrap_ci(
        prediction,
        origin_state=origin,
        observed_target=target,
        valid_mask=valid,
        n_resamples=100,
        seed=7,
    )
    second = paired_pixel_bootstrap_ci(
        prediction,
        origin_state=origin,
        observed_target=target,
        valid_mask=valid,
        n_resamples=100,
        seed=7,
    )
    assert first == second
    assert first["method"] == "paired_pixel_bootstrap"
    assert first["sampling_unit"] == "pixel_triplet_origin_prediction_target"


def test_component_density_is_normalized_by_valid_pixels():
    origin = np.full((3, 3), 6, dtype=np.uint8)
    state = origin.copy()
    state[0, 0] = 5
    state[2, 2] = 5
    valid = np.ones_like(origin, dtype=bool)
    hard = np.zeros_like(origin, dtype=bool)
    distances = np.ones_like(origin, dtype=np.float64)
    metrics = planning_metrics(
        state,
        origin_state=origin,
        valid_mask=valid,
        hard_exclusion_mask=hard,
        target_counts={value: int(np.count_nonzero(state == value)) for value in range(1, 7)},
        road_distance_m=distances,
        major_road_distance_m=distances,
    )
    # Two disconnected built components in nine valid cells.
    assert metrics["built_component_count"] == 2
    assert metrics["built_components_per_1000_pixels"] == 2000 / 9
