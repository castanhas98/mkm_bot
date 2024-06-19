import logging

from decimal import Decimal
from .common import PricingParameters

logger = logging.getLogger(__name__)

MIN_PRICE = Decimal(0.15)
MULTIPLIER = Decimal(1.10)
MULTIPLER_15_PLUS = Decimal(1.08)


def compute_price(parameters: PricingParameters) -> Decimal:
    price = max(
        parameters.from_price,
        parameters.trend_price,
        parameters.thirty_price,
        parameters.seven_price,
        parameters.one_price
    )

    if price < MIN_PRICE:
        price = MIN_PRICE
        logger.info(
            f"Computed MIN_PRICE ({price}) for "
            f"pricing parameters: {parameters}"
        )

        return price

    if price < Decimal(15.00):
        price *= MULTIPLIER
    else:
        price *= MULTIPLER_15_PLUS

    logger.info(
        f"Computed price ({price}) for pricing parameters: {parameters}"
    )

    return price
