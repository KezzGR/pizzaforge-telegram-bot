from pydantic import BaseModel, Field


class CartItem(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    price: int = Field(ge=0)
    quantity: int = Field(default=1, gt=0)

    @property
    def total_price(self) -> int:
        """Общая стоимость этой позиции."""
        return self.price * self.quantity
