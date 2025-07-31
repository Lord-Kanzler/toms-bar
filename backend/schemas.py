# schemas.py - Pydantic schemas for request/response validation
from datetime import datetime, date
from typing import Optional, List, Dict, Any
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
            hourly_rate=None,  # This field doesn't exist in the database yet
            address=None,      # This field doesn't exist in the database yet
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


# Sales Schemas
class SaleBase(BaseModel):
    order_id: Optional[int] = None
    sale_date: date
    total_amount: float
    payment_method: str
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    served_by: Optional[int] = None


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    sale_date: Optional[date] = None
    total_amount: Optional[float] = None
    payment_method: Optional[str] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    served_by: Optional[int] = None


class Sale(SaleBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DailyReportBase(BaseModel):
    report_date: date
    total_sales: float
    total_orders: int
    average_order_value: float
    cash_sales: Optional[float] = None
    card_sales: Optional[float] = None
    total_customers: Optional[int] = None
    staff_cost: Optional[float] = None
    inventory_cost: Optional[float] = None
    net_profit: float


class DailyReportCreate(DailyReportBase):
    pass


class DailyReportUpdate(BaseModel):
    total_sales: Optional[float] = None
    total_orders: Optional[int] = None
    average_order_value: Optional[float] = None
    cash_sales: Optional[float] = None
    card_sales: Optional[float] = None
    total_customers: Optional[int] = None
    staff_cost: Optional[float] = None
    inventory_cost: Optional[float] = None
    net_profit: Optional[float] = None


class DailyReport(DailyReportBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Staff Management Schemas
class TimesheetBase(BaseModel):
    staff_id: int
    date: date
    clock_in: str  # Store as string in HH:MM format
    clock_out: str  # Store as string in HH:MM format
    break_duration: int = 0  # in minutes
    notes: Optional[str] = None


class TimesheetCreate(TimesheetBase):
    pass


class TimesheetUpdate(BaseModel):
    date: Optional[date] = None
    clock_in: Optional[str] = None
    clock_out: Optional[str] = None
    break_duration: Optional[int] = None
    notes: Optional[str] = None


class Timesheet(TimesheetBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SalaryRecordBase(BaseModel):
    staff_id: int
    period_start: date
    period_end: date
    regular_hours: float
    overtime_hours: float = 0
    regular_pay: float
    overtime_pay: float = 0
    bonuses: float = 0
    deductions: float = 0
    total_pay: float
    is_paid: bool = False
    notes: Optional[str] = None
    paid_on: Optional[date] = None


class SalaryRecordCreate(SalaryRecordBase):
    pass


class SalaryRecordUpdate(BaseModel):
    regular_hours: Optional[float] = None
    overtime_hours: Optional[float] = None
    regular_pay: Optional[float] = None
    overtime_pay: Optional[float] = None
    bonuses: Optional[float] = None
    deductions: Optional[float] = None
    total_pay: Optional[float] = None
    is_paid: Optional[bool] = None
    notes: Optional[str] = None
    paid_on: Optional[date] = None


class SalaryRecord(SalaryRecordBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkScheduleBase(BaseModel):
    staff_id: int
    date: date
    start_time: str  # Store as string in HH:MM format
    end_time: str  # Store as string in HH:MM format
    position: str
    is_approved: bool = False


class WorkScheduleCreate(WorkScheduleBase):
    pass


class WorkScheduleUpdate(BaseModel):
    date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    position: Optional[str] = None
    is_approved: Optional[bool] = None


class WorkSchedule(WorkScheduleBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# System Settings Schemas
class SystemSettingBase(BaseModel):
    setting_key: str
    setting_value: str
    description: Optional[str] = None
    category: str = "general"


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSettingUpdate(BaseModel):
    setting_value: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class SystemSetting(SystemSettingBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    user_id: Optional[int] = None
    title: str
    message: str
    notification_type: str = "info"  # info, warning, error, success
    priority: str = "normal"  # low, normal, high, urgent
    category: str = "general"  # inventory, orders, staff, system
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    extra_data: Optional[str] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    read_at: Optional[datetime] = None


class Notification(NotificationBase):
    id: int
    is_read: bool = False
    is_dismissed: bool = False
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Notification statistics and summary schemas
class NotificationStats(BaseModel):
    total_notifications: int
    unread_count: int
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    by_type: Dict[str, int]


# Analytics Schemas
class SalesAnalytics(BaseModel):
    total_revenue: float
    total_orders: int
    average_order_value: float
    top_selling_items: List[Dict[str, Any]]
    revenue_by_category: List[Dict[str, Any]]
    daily_sales: List[Dict[str, Any]]
    payment_method_breakdown: List[Dict[str, Any]]


class StaffAnalytics(BaseModel):
    total_staff: int
    active_staff: int
    staff_by_position: List[Dict[str, Any]]
    total_hours_worked: float
    total_salary_paid: float
    top_performers: List[Dict[str, Any]]


# Financial Reporting Schemas
class FinancialTransaction(BaseModel):
    id: int
    date: date
    type: str  # income, expense
    category: str
    amount: float
    description: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FinancialTransactionCreate(BaseModel):
    date: date
    type: str
    category: str
    amount: float
    description: Optional[str] = None
    reference_id: Optional[str] = None


class FinancialOverview(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float
    gross_margin: float
    net_profit_margin: float
    expense_breakdown: List[Dict[str, Any]]
    revenue_breakdown: List[Dict[str, Any]]
    daily_summary: List[Dict[str, Any]]


class ExpenseReport(BaseModel):
    total_expenses: float
    period_start: date
    period_end: date
    categories: List[Dict[str, Any]]
    detailed_expenses: Optional[List[Dict[str, Any]]] = None


class ProfitLossReport(BaseModel):
    start_date: date
    end_date: date
    revenue: Dict[str, Any]
    expenses: Dict[str, Any]
    gross_profit: float
    operating_profit: float
    net_profit: float
    monthly_breakdown: Optional[List[Dict[str, Any]]] = None


class ProfitLossStatement(BaseModel):
    period: str
    revenue: Dict[str, Any]
    expenses: Dict[str, Any]
    profits: Dict[str, Any]


class CashFlow(BaseModel):
    start_date: date
    end_date: date
    total_inflows: float
    total_outflows: float
    net_cash_flow: float
    daily_cash_flow: List[Dict[str, Any]]


class BalanceSheet(BaseModel):
    as_of_date: date
    assets: Dict[str, Any]
    liabilities: Dict[str, Any]
    equity: Dict[str, Any]
    total_assets: float
    total_liabilities: float
    total_equity: float
