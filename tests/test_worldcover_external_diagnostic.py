import numpy as np

from benchmarks.abu_dhabi_land_use_v1.run_worldcover_external_diagnostic import (
    _binary_metrics,
    _worldcover_count_allocation,
)


def test_binary_metrics_marks_precision_undefined_without_predictions():
    predicted = np.zeros((2, 2), dtype=bool)
    observed = np.array([[True, False], [False, False]])
    result = _binary_metrics(predicted, observed, np.ones((2, 2), dtype=bool))

    assert result["precision"] is None
    assert result["recall"] == 0.0
    assert result["f1"] == 0.0
    assert result["intersection_over_union"] == 0.0


def test_binary_metrics_treats_two_empty_sets_as_exact_agreement():
    empty = np.zeros((2, 2), dtype=bool)
    result = _binary_metrics(empty, empty, np.ones((2, 2), dtype=bool))

    assert result["precision"] is None
    assert result["recall"] is None
    assert result["f1"] == 1.0
    assert result["intersection_over_union"] == 1.0


def test_worldcover_count_action_respects_count_and_hard_mask():
    probability = np.zeros((6, 2, 3), dtype=float)
    probability[4] = np.array(
        [[0.1, 0.9, 0.2], [0.8, 0.3, 0.7]], dtype=float
    )
    origin = np.array([[2, 5, 3], [2, 1, 4]], dtype=np.int16)
    valid = np.ones(origin.shape, dtype=bool)
    hard = np.array([[False, False, False], [False, False, True]])

    kernel, random = _worldcover_count_allocation(
        probability=probability,
        origin=origin,
        valid=valid,
        hard=hard,
        gain_count=2,
        seed=31,
    )

    assert int(kernel.sum()) == 2
    assert int(random.sum()) == 2
    assert not kernel[0, 1]
    assert not random[0, 1]
    assert not kernel[1, 2]
    assert not random[1, 2]
    assert kernel[1, 0] and kernel[1, 1]  # highest eligible scores
