# notifications.py - Notification Management API router
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from models import Notification as NotificationModel, InventoryItem, Order, StaffMember
from database import get_db
from schemas import (
    Notification as NotificationSchema, 
    NotificationCreate, 
    NotificationUpdate,
    NotificationStats
)
import json

router = APIRouter()


@router.get("/", response_model=List[NotificationSchema])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get notifications with optional filtering"""
    query = db.query(NotificationModel)
    
    if unread_only:
        query = query.filter(NotificationModel.is_read == False)
    
    if category:
        query = query.filter(NotificationModel.category == category)
    
    if priority:
        query = query.filter(NotificationModel.priority == priority)
    
    if user_id:
        query = query.filter(NotificationModel.user_id == user_id)
    
    # Filter out expired notifications
    query = query.filter(
        (NotificationModel.expires_at.is_(None)) | 
        (NotificationModel.expires_at > datetime.now())
    )
    
    # Filter out dismissed notifications unless specifically requested
    query = query.filter(NotificationModel.is_dismissed == False)
    
    notifications = query.order_by(desc(NotificationModel.created_at)).offset(skip).limit(limit).all()
    return [NotificationSchema.from_orm(notification) for notification in notifications]


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get notification statistics"""
    query = db.query(NotificationModel)
    
    if user_id:
        query = query.filter(NotificationModel.user_id == user_id)
    
    # Filter out expired and dismissed notifications
    query = query.filter(
        and_(
            (NotificationModel.expires_at.is_(None)) | 
            (NotificationModel.expires_at > datetime.now()),
            NotificationModel.is_dismissed == False
        )
    )
    
    notifications = query.all()
    
    total_count = len(notifications)
    unread_count = len([n for n in notifications if not n.is_read])
    
    # Count by category
    by_category = {}
    for notification in notifications:
        category = notification.category
        by_category[category] = by_category.get(category, 0) + 1
    
    # Count by priority
    by_priority = {}
    for notification in notifications:
        priority = notification.priority
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    # Count by type
    by_type = {}
    for notification in notifications:
        notification_type = notification.notification_type
        by_type[notification_type] = by_type.get(notification_type, 0) + 1
    
    return NotificationStats(
        total_notifications=total_count,
        unread_count=unread_count,
        by_category=by_category,
        by_priority=by_priority,
        by_type=by_type
    )


@router.get("/unread-count")
async def get_unread_count(
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    query = db.query(NotificationModel).filter(
        and_(
            NotificationModel.is_read == False,
            NotificationModel.is_dismissed == False,
            (NotificationModel.expires_at.is_(None)) | 
            (NotificationModel.expires_at > datetime.now())
        )
    )
    
    if user_id:
        query = query.filter(NotificationModel.user_id == user_id)
    
    count = query.count()
    return {"unread_count": count}


@router.post("/", response_model=NotificationSchema)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    db_notification = NotificationModel(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return NotificationSchema.from_orm(db_notification)


@router.put("/{notification_id}", response_model=NotificationSchema)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    db: Session = Depends(get_db)
):
    """Update a notification (mark as read, dismissed, etc.)"""
    db_notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id
    ).first()
    
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    update_data = notification_update.dict(exclude_unset=True)
    
    # Set read_at timestamp if marking as read
    if update_data.get("is_read") and not db_notification.read_at:
        update_data["read_at"] = datetime.now()
    
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return NotificationSchema.from_orm(db_notification)


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    user_id: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    query = db.query(NotificationModel).filter(NotificationModel.is_read == False)
    
    if user_id:
        query = query.filter(NotificationModel.user_id == user_id)
    
    if category:
        query = query.filter(NotificationModel.category == category)
    
    notifications = query.all()
    current_time = datetime.now()
    
    for notification in notifications:
        notification.is_read = True
        notification.read_at = current_time
    
    db.commit()
    
    return {"message": f"Marked {len(notifications)} notifications as read"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    db_notification = db.query(NotificationModel).filter(
        NotificationModel.id == notification_id
    ).first()
    
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(db_notification)
    db.commit()
    
    return {"message": "Notification deleted successfully"}


@router.post("/cleanup-expired")
async def cleanup_expired_notifications(db: Session = Depends(get_db)):
    """Remove expired notifications"""
    expired_notifications = db.query(NotificationModel).filter(
        and_(
            NotificationModel.expires_at.isnot(None),
            NotificationModel.expires_at < datetime.now()
        )
    ).all()
    
    for notification in expired_notifications:
        db.delete(notification)
    
    db.commit()
    
    return {"message": f"Cleaned up {len(expired_notifications)} expired notifications"}


# Event-triggered notification functions
async def create_low_stock_notification(item: InventoryItem, db: Session):
    """Create notification for low stock items"""
    existing = db.query(NotificationModel).filter(
        and_(
            NotificationModel.category == "inventory",
            NotificationModel.extra_data.contains(f'"item_id": {item.id}'),
            NotificationModel.is_dismissed == False
        )
    ).first()
    
    # Don't create duplicate low stock notifications
    if existing:
        return existing
    
    metadata = json.dumps({
        "item_id": item.id,
        "item_name": item.name,
        "current_stock": item.current_stock,
        "threshold": item.threshold
    })
    
    notification = NotificationModel(
        title="Low Stock Alert",
        message=f"{item.name} is running low (Current: {item.current_stock} {item.unit}, Threshold: {item.threshold} {item.unit})",
        notification_type="warning",
        priority="high" if item.current_stock <= 0 else "normal",
        category="inventory",
        action_url=f"/inventory#{item.id}",
        action_label="Restock Item",
        extra_data=metadata,
        expires_at=datetime.now() + timedelta(days=7)
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


async def create_order_notification(order_id: int, event_type: str, db: Session):
    """Create notification for order events"""
    metadata = json.dumps({
        "order_id": order_id,
        "event_type": event_type
    })
    
    if event_type == "new_order":
        title = "New Order Received"
        message = f"Order #{order_id} has been placed and requires attention"
        priority = "normal"
        notification_type = "info"
    elif event_type == "order_ready":
        title = "Order Ready"
        message = f"Order #{order_id} is ready for pickup/delivery"
        priority = "normal"
        notification_type = "success"
    elif event_type == "order_delayed":
        title = "Order Delayed"
        message = f"Order #{order_id} is taking longer than expected"
        priority = "high"
        notification_type = "warning"
    else:
        return None
    
    notification = NotificationModel(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        category="orders",
        action_url=f"/orders#{order_id}",
        action_label="View Order",
        extra_data=metadata,
        expires_at=datetime.now() + timedelta(hours=24)
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


async def create_system_notification(title: str, message: str, priority: str = "normal", notification_type: str = "info", db: Session = None):
    """Create a system notification"""
    notification = NotificationModel(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        category="system",
        expires_at=datetime.now() + timedelta(days=3)
    )
    
    if db:
        db.add(notification)
        db.commit()
        db.refresh(notification)
    
    return notification
