import pytest

from benchmarks.abu_dhabi_land_use_v1.run_rolling_backtest import (
    fit_transitions_for_origin,
)


@pytest.mark.parametrize("origin_year", [2020, 2021, 2022, 2023])
def test_rolling_training_stops_before_prediction_target(origin_year):
    transitions = fit_transitions_for_origin(origin_year)
    prediction_target = origin_year + 1

    assert max(target for _, target in transitions) == origin_year
    assert all(target < prediction_target for _, target in transitions)
    assert (origin_year, prediction_target) not in transitions


@pytest.mark.parametrize("origin_year", [2017, 2024])
def test_unsupported_rolling_origins_are_rejected(origin_year):
    with pytest.raises(ValueError, match="unsupported_origin_year"):
        fit_transitions_for_origin(origin_year)
