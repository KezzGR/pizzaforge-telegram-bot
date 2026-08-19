import unittest

from models.product import Product
from services.cart_service import CartService


class CartServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.product = Product(
            id=1,
            name="Маргарита",
            category="pizza",
            price=450,
        )

    def test_same_product_increases_quantity(self) -> None:
        cart = CartService([])

        cart.add_product(self.product)
        item = cart.add_product(self.product)

        self.assertEqual(item.quantity, 2)
        self.assertEqual(cart.get_total_price(), 900)
        self.assertEqual(len(cart.get_items()), 1)

    def test_cart_can_be_restored_from_serialized_state(self) -> None:
        cart = CartService([])
        cart.add_product(self.product)

        restored = CartService.from_state({"cart": cart.get_cart_data()})

        self.assertEqual(restored.get_items()[0].name, "Маргарита")
        self.assertEqual(restored.get_total_price(), 450)

    def test_clear_removes_all_items(self) -> None:
        cart = CartService([])
        cart.add_product(self.product)

        cart.clear()

        self.assertTrue(cart.is_empty())
        self.assertEqual(cart.get_cart_data(), [])

    def test_unavailable_product_is_rejected(self) -> None:
        cart = CartService([])

        with self.assertRaisesRegex(ValueError, "недоступен"):
            cart.add_product(None)


if __name__ == "__main__":
    unittest.main()
