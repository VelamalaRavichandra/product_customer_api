from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    sku: str = Field(min_length=1, max_length=50)
    category: str = Field(min_length=1, max_length=100)
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    sku: str | None = Field(default=None, min_length=1, max_length=50)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock_quantity: int
    sku: str
    category: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    address: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    pincode: str = Field(min_length=4, max_length=10)
    is_active: bool = True


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=20)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    pincode: str | None = Field(default=None, min_length=4, max_length=10)
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    state: str
    pincode: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
