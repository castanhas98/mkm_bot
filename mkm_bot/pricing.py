from decimal import Decimal

from .common import PricingParameters


def compute_price(parameters: PricingParameters) -> Decimal:
    return Decimal(100)
