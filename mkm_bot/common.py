from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PricingParameters:
    min_price: Decimal
    trend_price: Decimal
    thirty_price: Decimal
    seven_price: Decimal
    one_price: Decimal
    min_price_same_language: Decimal
