import pytest

from demo_project.calculator import (
    calculate_average,
    calculate_discount,
    get_last_item,
)


def test_average():
    assert calculate_average([10, 20, 30]) == pytest.approx(20)


def test_average_empty_list():
    with pytest.raises(ValueError, match="empty"):
        calculate_average([])


@pytest.mark.parametrize(
    "price, discount, expected",
    [
        (200, 10, 180),
        (500, 20, 400),
        (200, 0, 200),
        (200, 100, 0),
    ],
)
def test_discount(price, discount, expected):
    assert calculate_discount(price, discount) == pytest.approx(expected)


def test_last_item():
    assert get_last_item(["apple", "banana"]) == "banana"


def test_last_item_single_element():
    assert get_last_item(["apple"]) == "apple"


def test_last_item_empty_list():
    with pytest.raises(ValueError, match="empty"):
        get_last_item([])