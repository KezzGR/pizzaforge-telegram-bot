from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: int = Field(ge=0)
