from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    emoji: str = Field(min_length=1, max_length=16)
    category: str = Field(min_length=1, max_length=50)
    price: int = Field(ge=0)
