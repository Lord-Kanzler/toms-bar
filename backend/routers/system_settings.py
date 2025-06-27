# routers/system_settings.py - System settings and notifications
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import SystemSettings, Notification, StaffMember
from schemas import (
    SystemSetting as SystemSettingSchema,
    SystemSettingCreate,
    SystemSettingUpdate,
    Notification as NotificationSchema,
    NotificationCreate,
    NotificationUpdate
)

router = APIRouter(prefix="/api/system", tags=["system"])

# System Settings
@router.get("/settings/", response_model=List[SystemSettingSchema])
def get_system_settings(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SystemSettings)
    if category:
        query = query.filter(SystemSettings.category == category)
    return query.all()

@router.get("/settings/{setting_key}", response_model=SystemSettingSchema)
def get_setting(setting_key: str, db: Session = Depends(get_db)):
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == setting_key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.post("/settings/", response_model=SystemSettingSchema)
def create_setting(setting: SystemSettingCreate, db: Session = Depends(get_db)):
    # Check if setting already exists
    existing = db.query(SystemSettings).filter(SystemSettings.setting_key == setting.setting_key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Setting already exists")
    
    db_setting = SystemSettings(**setting.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.put("/settings/{setting_key}", response_model=SystemSettingSchema)
def update_setting(setting_key: str, setting: SystemSettingUpdate, db: Session = Depends(get_db)):
    db_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == setting_key).first()
    if not db_setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    for field, value in setting.dict(exclude_unset=True).items():
        setattr(db_setting, field, value)
    
    db.commit()
    db.refresh(db_setting)
    return db_setting

@router.delete("/settings/{setting_key}")
def delete_setting(setting_key: str, db: Session = Depends(get_db)):
    db_setting = db.query(SystemSettings).filter(SystemSettings.setting_key == setting_key).first()
    if not db_setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(db_setting)
    db.commit()
    return {"message": "Setting deleted successfully"}

# Initialize default settings
@router.post("/settings/initialize-defaults")
def initialize_default_settings(db: Session = Depends(get_db)):
    default_settings = [
        {
            "setting_key": "restaurant_name",
            "setting_value": "GastroPro Restaurant",
            "description": "Name of the restaurant",
            "category": "general"
        },
        {
            "setting_key": "tax_rate",
            "setting_value": "0.08",
            "description": "Tax rate percentage (8%)",
            "category": "tax"
        },
        {
            "setting_key": "overtime_rate",
            "setting_value": "1.5",
            "description": "Overtime pay multiplier",
            "category": "payroll"
        },
        {
            "setting_key": "low_stock_threshold",
            "setting_value": "10",
            "description": "Default low stock threshold percentage",
            "category": "inventory"
        },
        {
            "setting_key": "notification_email",
            "setting_value": "admin@gastropro.com",
            "description": "Admin email for notifications",
            "category": "notification"
        },
        {
            "setting_key": "currency",
            "setting_value": "USD",
            "description": "Currency code",
            "category": "general"
        },
        {
            "setting_key": "working_hours_per_day",
            "setting_value": "8",
            "description": "Standard working hours per day",
            "category": "payroll"
        },
        {
            "setting_key": "alcohol_license_number",
            "setting_value": "",
            "description": "Alcohol license number",
            "category": "legal"
        }
    ]
    
    created_count = 0
    for setting_data in default_settings:
        existing = db.query(SystemSettings).filter(
            SystemSettings.setting_key == setting_data["setting_key"]
        ).first()
        
        if not existing:
            db_setting = SystemSettings(**setting_data)
            db.add(db_setting)
            created_count += 1
    
    db.commit()
    return {"message": f"Initialized {created_count} default settings"}

# Notifications
@router.get("/notifications/", response_model=List[NotificationSchema])
def get_notifications(
    recipient_id: Optional[int] = None,
    is_read: Optional[bool] = None,
    notification_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Notification)
    
    if recipient_id:
        query = query.filter(Notification.recipient_id == recipient_id)
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    return query.order_by(Notification.created_at.desc()).all()

@router.post("/notifications/", response_model=NotificationSchema)
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.put("/notifications/{notification_id}", response_model=NotificationSchema)
def update_notification(notification_id: int, notification: NotificationUpdate, db: Session = Depends(get_db)):
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    for field, value in notification.dict(exclude_unset=True).items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.post("/notifications/{notification_id}/mark-read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db_notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.post("/notifications/mark-all-read")
def mark_all_notifications_read(recipient_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Notification).filter(Notification.is_read == False)
    
    if recipient_id:
        query = query.filter(Notification.recipient_id == recipient_id)
    
    count = query.update({"is_read": True})
    db.commit()
    return {"message": f"Marked {count} notifications as read"}

@router.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    db_notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(db_notification)
    db.commit()
    return {"message": "Notification deleted successfully"}

# System notification triggers
@router.post("/notifications/check-low-stock")
def check_low_stock_notifications(db: Session = Depends(get_db)):
    from models import InventoryItem
    
    # Get low stock threshold setting
    threshold_setting = db.query(SystemSettings).filter(
        SystemSettings.setting_key == "low_stock_threshold"
    ).first()
    
    threshold_percentage = float(threshold_setting.setting_value) if threshold_setting else 10
    
    # Find low stock items
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.current_stock <= (InventoryItem.threshold * threshold_percentage / 100)
    ).all()
    
    created_notifications = 0
    for item in low_stock_items:
        # Check if notification already exists for this item
        existing = db.query(Notification).filter(
            Notification.title.like(f"%{item.name}%"),
            Notification.notification_type == "warning",
            Notification.is_read == False
        ).first()
        
        if not existing:
            notification = Notification(
                title=f"Low Stock Alert: {item.name}",
                message=f"{item.name} is running low. Current stock: {item.current_stock} {item.unit}, Minimum: {item.threshold} {item.unit}",
                notification_type="warning",
                priority="high"
            )
            db.add(notification)
            created_notifications += 1
    
    db.commit()
    return {"message": f"Created {created_notifications} low stock notifications"}

@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get summary data for the admin dashboard"""
    from models import InventoryItem, Order
    from datetime import date, timedelta
    
    today = date.today()
    
    # Unread notifications count
    unread_notifications = db.query(Notification).filter(Notification.is_read == False).count()
    
    # Low stock items count
    low_stock_count = db.query(InventoryItem).filter(
        InventoryItem.current_stock <= InventoryItem.threshold
    ).count()
    
    # Today's orders count
    today_orders = db.query(Order).filter(
        func.date(Order.created_at) == today
    ).count()
    
    # Active staff count
    active_staff = db.query(StaffMember).filter(StaffMember.is_active == True).count()
    
    return {
        "unread_notifications": unread_notifications,
        "low_stock_items": low_stock_count,
        "today_orders": today_orders,
        "active_staff": active_staff,
        "system_status": "operational"
    }
