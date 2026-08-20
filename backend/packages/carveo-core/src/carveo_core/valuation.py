from statistics import median
from typing import Literal

from carveo_core.contracts import DealPosition


def calculate_deal_position(price: int, comparable_prices: list[int]) -> DealPosition:
    if len(comparable_prices) < 3:
        return DealPosition(label="Limited data", sample_size=len(comparable_prices))

    typical_price = int(median(comparable_prices))
    difference_amount = price - typical_price
    difference_percent = round((difference_amount / typical_price) * 100, 2)
    if difference_percent <= -5:
        label: Literal["Below typical", "Near typical", "Above typical"] = "Below typical"
    elif difference_percent >= 5:
        label = "Above typical"
    else:
        label = "Near typical"
    return DealPosition(
        label=label,
        typical_price=typical_price,
        difference_amount=difference_amount,
        difference_percent=difference_percent,
        sample_size=len(comparable_prices),
    )
