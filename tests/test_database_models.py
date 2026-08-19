import unittest

import db.models  # noqa: F401
from db.database import Base


class DatabaseModelTests(unittest.TestCase):
    def test_expected_tables_are_registered(self) -> None:
        self.assertEqual(
            set(Base.metadata.tables),
            {"products", "orders", "order_items"},
        )

    def test_order_items_preserve_product_snapshot(self) -> None:
        columns = Base.metadata.tables["order_items"].columns

        self.assertIn("product_name", columns)
        self.assertIn("unit_price", columns)
        self.assertIn("quantity", columns)


if __name__ == "__main__":
    unittest.main()
