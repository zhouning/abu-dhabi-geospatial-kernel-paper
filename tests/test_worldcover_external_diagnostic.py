import numpy as np

from benchmarks.abu_dhabi_land_use_v1.run_worldcover_external_diagnostic import (
    _binary_metrics,
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
