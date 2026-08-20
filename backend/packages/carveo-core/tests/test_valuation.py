from carveo_core.contracts import DealPosition
from carveo_core.valuation import calculate_deal_position


def test_deal_position_requires_three_comparables() -> None:
    result = calculate_deal_position(100_000, [95_000, 105_000])

    assert result == DealPosition(label="Limited data", sample_size=2)


def test_deal_position_reports_below_typical_price() -> None:
    result = calculate_deal_position(90_000, [100_000, 105_000, 110_000])

    assert result.label == "Below typical"
    assert result.typical_price == 105_000
    assert result.difference_amount == -15_000
    assert result.difference_percent == -14.29
