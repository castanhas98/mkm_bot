import pytest

from decimal import Decimal

from mkm_bot.cardmarket_client import is_last_page, get_price_from_string

PAGE_X_OF_Y_SUCCESS_PARAM = [
    ("Page 1 of 1", True),
    ("Page 2 of 2", True),
    ("Page 1 of 2", False),
    ("Page 2 of 7", False),
    ("Page 1000 of 1000", True),
]


@pytest.mark.parametrize("page_x_of_y,expected", PAGE_X_OF_Y_SUCCESS_PARAM)
def test_is_last_page_success(
    page_x_of_y: str,
    expected: bool
) -> None:
    assert is_last_page(page_x_of_y) == expected


PAGE_X_OF_Y_NO_MATCH_PARAM = [
    ("Page 1 of 1."), ("1 of 7"), ("2/7"), ("page 1 of 7"), ("Page -1 of 2")
]


@pytest.mark.parametrize("page_x_of_y", PAGE_X_OF_Y_NO_MATCH_PARAM)
def test_is_last_page_no_match(page_x_of_y: str) -> None:
    with pytest.raises(RuntimeError) as e:
        is_last_page(page_x_of_y)

    assert str(e.value) == f"No match for '{page_x_of_y}'"


PAGE_X_OF_Y_INVALID_PARAM = [
    ("Page 1 of 0", 1, 0),
    ("Page 2 of 1", 2, 1),
    ("Page 0 of 0", 0, 0),
    ("Page 7 of 1", 7, 1),
    ("Page 1000 of 999", 1000, 999),
]


@pytest.mark.parametrize("page_x_of_y,x,y", PAGE_X_OF_Y_INVALID_PARAM)
def test_is_last_page_invalid_page_nubmers(
    page_x_of_y: str, x: int, y: int
) -> None:
    with pytest.raises(RuntimeError) as e:
        is_last_page(page_x_of_y)

    assert str(e.value) == f"Invalid page numbers: current={x}, total={y}"


PRICE_STR_SUCCESS_PAR = [
    ("0,07 €", Decimal(0.07)),
    ("10,07 €", Decimal(10.07)),
    ("0,01 €", Decimal(0.01)),
    ("999999999,99 €", Decimal(999999999.99)),
    ("1,50 €", Decimal(1.50)),
]


@pytest.mark.parametrize("price_str,expected", PRICE_STR_SUCCESS_PAR)
def test_get_price_from_string_success(
    price_str: str,
    expected: Decimal
) -> None:
    price = get_price_from_string(price_str)
    assert round(price, 2) == round(expected, 2)


PRICE_STR_NO_MATCH_PAR = [
    ("0,07€"),
    ("10.07 €"),
    ("0,1 €"),
    ("1,50 €."),
    (" 1,50 €.")
]


@pytest.mark.parametrize("price_str", PRICE_STR_NO_MATCH_PAR)
def test_get_price_from_string_no_match(
    price_str: str
) -> None:
    with pytest.raises(RuntimeError) as e:
        get_price_from_string(price_str)

    assert str(e.value) == f"No match for '{price_str}'"


def test_get_price_from_string_read_zero() -> None:
    price_str = "0,00 €"
    price = Decimal("0,00".replace(',', '.'))

    with pytest.raises(RuntimeError) as e:
        get_price_from_string(price_str)

    assert str(e.value) == f"Price ({price}) is Zero!: {price_str}"
