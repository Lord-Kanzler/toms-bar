# models.py - SQLAlchemy ORM models

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Date, Time, Numeric
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


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
    # Relationships - these will be created in the database during migration
    timesheets = relationship("Timesheet", back_populates="staff_member", cascade="all, delete-orphan")
    salary_records = relationship("SalaryRecord", back_populates="staff_member", cascade="all, delete-orphan")
    schedules = relationship("WorkSchedule", back_populates="staff_member", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer)
    customer_name = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime)
    total_amount = Column(Float)
    items = relationship("OrderItem", back_populates="order")
    # Add relationship to Sale
    sale = relationship("Sale", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer)
    special_instructions = Column(String)
    order = relationship("Order", back_populates="items")


# New models for staff management
class Timesheet(Base):
    __tablename__ = "timesheets"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_members.id"))
    date = Column(Date)
    clock_in = Column(Time)
    clock_out = Column(Time)
    break_duration = Column(Integer)  # in minutes
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # Relationships
    staff_member = relationship("StaffMember", back_populates="timesheets")


class SalaryRecord(Base):
    __tablename__ = "salary_records"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_members.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    regular_hours = Column(Float)
    overtime_hours = Column(Float, default=0)
    regular_pay = Column(Float)
    overtime_pay = Column(Float, default=0)
    bonuses = Column(Float, default=0)
    deductions = Column(Float, default=0)
    total_pay = Column(Float)
    paid_on = Column(Date, nullable=True)
    is_paid = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    # Relationships
    staff_member = relationship("StaffMember", back_populates="salary_records")


class WorkSchedule(Base):
    __tablename__ = "work_schedules"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff_members.id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    position = Column(String)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # Relationships
    staff_member = relationship("StaffMember", back_populates="schedules")


# New models for sales analytics
class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    sale_date = Column(Date)
    total_amount = Column(Float)
    payment_method = Column(String)
    payment_status = Column(String, default="completed")
    receipt_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # Relationships
    order = relationship("Order", back_populates="sale")


class DailyReport(Base):
    __tablename__ = "daily_reports"
    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, unique=True)
    total_sales = Column(Float)
    total_orders = Column(Integer)
    average_order_value = Column(Float)
    most_sold_item = Column(String, nullable=True)
    total_inventory_cost = Column(Float, nullable=True)
    gross_profit = Column(Float)
    staff_cost = Column(Float, nullable=True)
    other_expenses = Column(Float, default=0)
    net_profit = Column(Float)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# New models for system settings
class SystemSettings(Base):
    __tablename__ = "system_settings"
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True)
    setting_value = Column(Text)
    description = Column(String, nullable=True)
    category = Column(String, default="general")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("staff_members.id"), nullable=True)
    title = Column(String)
    message = Column(Text)
    notification_type = Column(String, default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    read_at = Column(DateTime, nullable=True)
    # Relationships
    user = relationship("StaffMember")
