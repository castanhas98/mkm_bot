import pytest

from mkm_bot.cardmarket_client import is_last_page

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
