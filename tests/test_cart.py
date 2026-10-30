from unittest.mock import Mock

import pytest

from shop.cart import Cart, RateProvider


def test_add_item(empty_cart: Cart) -> None:
    empty_cart.add("Книга", price=200.0, qty=2)
    assert empty_cart.items_count() == 2


def test_add_duplicate_item_keeps_original_price(empty_cart: Cart) -> None:
    """Перевірка поведінки: повторне додавання збільшує кількість."""
    empty_cart.add("Ручка", price=50.0, qty=1)
    empty_cart.add("Ручка", price=100.0, qty=2)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 150.0  # (50 * 1) + (50 * 2) = 150


def test_remove_item(sample_cart: Cart) -> None:
    sample_cart.remove("Мишка")
    assert sample_cart.items_count() == 2


def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price must be non-negative"):
        empty_cart.add("Товар", price=-10.0)


def test_add_zero_or_negative_qty_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty must be positive"):
        empty_cart.add("Товар", price=100.0, qty=0)


def test_remove_nonexistent_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("Неіснуючий товар")


@pytest.mark.parametrize("invalid_discount", [-1.0, 100.1, 150.0])
def test_invalid_discount_raises(sample_cart: Cart, invalid_discount: float) -> None:
    with pytest.raises(ValueError, match="discount_percent must be in"):
        sample_cart.total(discount_percent=invalid_discount)


def test_invalid_exchange_rate_raises(sample_cart: Cart) -> None:
    rates = Mock(spec=RateProvider)
    rates.get_rate.return_value = 0.0
    with pytest.raises(ValueError, match="rate must be positive"):
        sample_cart.total_in("USD", rates)


@pytest.mark.parametrize(
    ("discount", "expected_total"),
    [
        (0.0, 28100.0),  # Граничне значення: без знижки
        (10.0, 25290.0),  # Звичайна знижка 10%
        (50.0, 14050.0),  # Знижка 50%
        (100.0, 0.0),  # Граничне значення: безкоштовно
    ],
)
def test_total_with_discounts(sample_cart: Cart, discount: float, expected_total: float) -> None:
    assert sample_cart.total(discount_percent=discount) == expected_total


def test_total_in_usd_with_mock(sample_cart: Cart) -> None:
    rates = Mock(spec=RateProvider)
    rates.get_rate.return_value = 40.0  # 1 USD = 40 UAH

    total_usd = sample_cart.total_in("USD", rates)

    assert total_usd == 702.5
    rates.get_rate.assert_called_once_with("USD")


def test_most_expensive_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_sample_cart(sample_cart: Cart) -> None:
    item = sample_cart.most_expensive()
    assert item is not None
    assert item.name == "Ноутбук"
    assert item.price == 25000.0


def test_checkout_price_applies_discount_once(sample_cart: Cart) -> None:
    assert sample_cart.checkout_price(10.0) == 25290.0
