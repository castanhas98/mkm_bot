from dataclasses import dataclass
from decimal import Decimal


@dataclass
class PricingParameters:
    from_price: Decimal
    trend_price: Decimal
    thirty_price: Decimal
    seven_price: Decimal
    one_price: Decimal
