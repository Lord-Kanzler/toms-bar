# models.py - SQLAlchemy ORM models

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    image_path = Column(String)
    tags = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    current_stock = Column(Float)
    unit = Column(String)
    threshold = Column(Float)
    supplier = Column(String)
    last_updated = Column(DateTime)
    is_alcohol = Column(Boolean, default=False)
    alcohol_type = Column(String, nullable=True)
    alcohol_volume = Column(Float, nullable=True)
    bottle_size = Column(Float, nullable=True)
    par_level = Column(Float, nullable=True)


class StaffMember(Base):
    __tablename__ = "staff_members"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    position = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    hire_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    profile_image = Column(String)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer)
    customer_name = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime)
    total_amount = Column(Float)
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    special_instructions = Column(String)
    order = relationship("Order", back_populates="items")
