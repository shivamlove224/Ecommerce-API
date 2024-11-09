from pydantic import BaseModel, EmailStr
from typing import List, TYPE_CHECKING

# Import to avoid circular import issues
if TYPE_CHECKING:
    from models import Product


class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    category: str
    user_id: int


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    products: List["Product"] = []  # Forward reference to Product model

    class Config:
        orm_mode = True
