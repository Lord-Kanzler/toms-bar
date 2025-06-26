# schemas.py - Pydantic schemas for request/response validation
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# Menu Item Schemas
class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_path: Optional[str] = None
    tags: Optional[str] = None
    is_active: bool = True


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_path: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class MenuItem(MenuItemBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Inventory Item Schemas
class InventoryItemBase(BaseModel):
    name: str
    category: str
    current_stock: float
    unit: str
    minimum_stock: float
    supplier: Optional[str] = None
    description: Optional[str] = None
    cost_per_unit: Optional[float] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    current_stock: Optional[float] = None
    unit: Optional[str] = None
    minimum_stock: Optional[float] = None
    supplier: Optional[str] = None
    description: Optional[str] = None
    cost_per_unit: Optional[float] = None


class InventoryItem(BaseModel):
    id: int
    name: str
    category: str
    current_stock: float
    unit: str
    minimum_stock: float
    supplier: Optional[str] = None
    description: Optional[str] = None
    cost_per_unit: Optional[float] = None
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Map database fields to schema fields
        return cls(
            id=obj.id,
            name=obj.name,
            category=obj.category,
            current_stock=obj.current_stock,
            unit=obj.unit,
            minimum_stock=obj.threshold,  # Map threshold to minimum_stock
            supplier=obj.supplier,
            description=getattr(obj, 'description', None),
            cost_per_unit=getattr(obj, 'cost_per_unit', None),
            last_updated=obj.last_updated
        )


# Staff Member Schemas
class StaffMemberBase(BaseModel):
    first_name: str
    last_name: str
    position: str
    email: str
    phone: Optional[str] = None
    hourly_rate: Optional[float] = None
    address: Optional[str] = None
    is_active: bool = True


class StaffMemberCreate(StaffMemberBase):
    pass


class StaffMemberUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    hourly_rate: Optional[float] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class StaffMember(BaseModel):
    id: int
    first_name: str
    last_name: str
    position: str
    email: str
    phone: Optional[str] = None
    hourly_rate: Optional[float] = None
    address: Optional[str] = None
    is_active: bool = True
    hire_date: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        # Split name into first_name and last_name
        name_parts = obj.name.split(' ', 1) if obj.name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        return cls(
            id=obj.id,
            first_name=first_name,
            last_name=last_name,
            position=obj.position,
            email=obj.email,
            phone=obj.phone,
            hourly_rate=getattr(obj, 'hourly_rate', None),
            address=getattr(obj, 'address', None),
            is_active=obj.is_active,
            hire_date=obj.hire_date
        )


# Order Item Schemas
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    special_instructions: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True


# Order Schemas
class OrderBase(BaseModel):
    table_number: int
    customer_name: Optional[str] = None
    status: str = "pending"
    total_amount: float


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = []


class OrderUpdate(BaseModel):
    table_number: Optional[int] = None
    customer_name: Optional[str] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None


class Order(OrderBase):
    id: int
    created_at: Optional[datetime] = None
    items: List[OrderItem] = []

    class Config:
        from_attributes = True
