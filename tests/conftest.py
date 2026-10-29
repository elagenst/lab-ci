import pytest
from shop.cart import Cart

@pytest.fixture
def empty_cart() -> Cart:
    """Фікстура для порожнього кошика."""
    return Cart()

@pytest.fixture
def sample_cart() -> Cart:
    """Фікстура для кошика з кількома товарами."""
    cart = Cart()
    cart.add("Ноутбук", price=25000.0, qty=1)
    cart.add("Мишка", price=800.0, qty=2)
    cart.add("Клавіатура", price=1500.0, qty=1)
    return cart