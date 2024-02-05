from decimal import Decimal

from .common import PricingParameters


class PricingModel:
    def compute_price(self, parameters: PricingParameters) -> Decimal:
        return Decimal(0.1)
