# notification_events.py - Event-driven notification system
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import json

from models import Notification as NotificationModel, InventoryItem, Order, StaffMember
from database import get_db


class NotificationEventManager:
    """Manages notification events and triggers"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.event_handlers = {
            'inventory_low_stock': self.handle_low_stock,
            'inventory_out_of_stock': self.handle_out_of_stock,
            'order_created': self.handle_order_created,
            'order_ready': self.handle_order_ready,
            'order_delayed': self.handle_order_delayed,
            'system_maintenance': self.handle_system_maintenance,
            'staff_shift_reminder': self.handle_shift_reminder,
        }
    
    async def trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger a notification event"""
        if event_type in self.event_handlers:
            return await self.event_handlers[event_type](data)
        else:
            raise ValueError(f"Unknown event type: {event_type}")
    
    async def handle_low_stock(self, item: InventoryItem):
        """Handle low stock notification for inventory item"""
        
        # Check if we already have a recent low stock notification for this item
        recent_notification = self.db.query(NotificationModel).filter(
            and_(
                NotificationModel.category == 'inventory',
                NotificationModel.title.contains(item.name),
                NotificationModel.title.contains('Low Stock'),
                NotificationModel.created_at > datetime.now() - timedelta(hours=6),
                NotificationModel.is_dismissed == False,
            )
        ).first()
        
        if recent_notification:
            return recent_notification
        
        notification = NotificationModel(
            title=f"Low Stock Alert: {item.name}",
            message=f"{item.name} is running low. Current stock: {item.current_stock} {item.unit}. Threshold: {item.threshold} {item.unit}.",
            notification_type="warning",
            priority="medium",
            category="inventory",
            action_url=f"/inventory#{item.id}",
            action_label="Restock Item",
            extra_data=json.dumps({
                "item_id": item.id,
                "current_stock": item.current_stock,
                "threshold": item.threshold,
                "unit": item.unit,
                "supplier": item.supplier
            }),
            expires_at=datetime.now() + timedelta(days=2)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    async def handle_out_of_stock(self, item: InventoryItem):
        """Handle out of stock notification for inventory item"""
        
        # Check for recent out of stock notification
        recent_notification = self.db.query(NotificationModel).filter(
            and_(
                NotificationModel.category == 'inventory',
                NotificationModel.title.contains(item.name),
                NotificationModel.title.contains('Out of Stock'),
                NotificationModel.created_at > datetime.now() - timedelta(hours=12),
                NotificationModel.is_dismissed == False,
            )
        ).first()
        
        if recent_notification:
            return recent_notification
        
        notification = NotificationModel(
            title=f"Out of Stock: {item.name}",
            message=f"{item.name} is completely out of stock! Immediate restocking required.",
            notification_type="error",
            priority="high",
            category="inventory",
            action_url=f"/inventory#{item.id}",
            action_label="Emergency Restock",
            extra_data=json.dumps({
                "item_id": item.id,
                "current_stock": item.current_stock,
                "supplier": item.supplier,
                "emergency": True
            }),
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    async def handle_order_created(self, order: Order):
        """Handle new order notification"""
        
        extra_data = json.dumps({
            "order_id": order.id,
            "event_type": "order_created",
            "table_number": order.table_number,
            "customer_name": order.customer_name,
            "total_amount": float(order.total_amount) if order.total_amount else 0.0
        })
        
        table_info = f" for table {order.table_number}" if order.table_number else ""
        customer_info = f" by {order.customer_name}" if order.customer_name else ""
        
        notification = NotificationModel(
            title="New Order Received",
            message=f"Order #{order.id} has been placed{table_info}{customer_info} and requires attention",
            notification_type="info",
            priority="normal",
            category="orders",
            action_url=f"/orders#{order.id}",
            action_label="View Order",
            extra_data=extra_data,
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    async def handle_order_ready(self, order: Order):
        """Handle order ready notification"""
        
        extra_data = json.dumps({
            "order_id": order.id,
            "event_type": "order_ready",
            "table_number": order.table_number,
            "customer_name": order.customer_name
        })
        
        table_info = f" for table {order.table_number}" if order.table_number else ""
        
        notification = NotificationModel(
            title="Order Ready",
            message=f"Order #{order.id}{table_info} is ready for pickup/delivery",
            notification_type="success",
            priority="normal",
            category="orders",
            action_url=f"/orders#{order.id}",
            action_label="View Order",
            extra_data=extra_data,
            expires_at=datetime.now() + timedelta(hours=6)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    async def handle_order_delayed(self, order: Order, delay_minutes: int = 15):
        """Handle order delayed notification"""
        
        extra_data = json.dumps({
            "order_id": order.id,
            "event_type": "order_delayed",
            "delay_minutes": delay_minutes,
            "table_number": order.table_number
        })
        
        table_info = f" for table {order.table_number}" if order.table_number else ""
        
        notification = NotificationModel(
            title="Order Delayed",
            message=f"Order #{order.id}{table_info} is delayed by approximately {delay_minutes} minutes",
            notification_type="warning",
            priority="high",
            category="orders",
            action_url=f"/orders#{order.id}",
            action_label="View Order",
            extra_data=extra_data,
            expires_at=datetime.now() + timedelta(hours=12)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    async def handle_system_maintenance(self, message: str = "System maintenance scheduled", priority: str = "normal"):
        """Handle system maintenance notification"""
        
        extra_data = json.dumps({
            "event_type": "system_maintenance",
            "scheduled_time": datetime.now().isoformat(),
            "priority": priority
        })
        
        notification = NotificationModel(
            title="System Maintenance Scheduled",
            message=message,
            notification_type="info",
            priority=priority,
            category="system",
            extra_data=extra_data,
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    async def handle_shift_reminder(self, staff: StaffMember, shift_time: str):
        """Handle shift reminder notification"""
        
        extra_data = json.dumps({
            "event_type": "shift_reminder",
            "staff_id": staff.id,
            "shift_time": shift_time,
            "staff_name": staff.name
        })
        
        notification = NotificationModel(
            title="Shift Reminder",
            message=f"Reminder: Your shift starts at {shift_time}",
            notification_type="info",
            priority="normal",
            category="staff",
            user_id=staff.id,
            extra_data=extra_data,
            expires_at=datetime.now() + timedelta(hours=12)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    async def get_event_counts(self) -> Dict[str, int]:
        """Get counts of different notification events"""
        counts = {}
        
        # Count by category
        for category in ['inventory', 'orders', 'system', 'staff']:
            count = self.db.query(NotificationModel).filter(
                NotificationModel.category == category
            ).count()
            counts[f"{category}_notifications"] = count
        
        # Count by priority
        for priority in ['high', 'medium', 'low', 'normal']:
            count = self.db.query(NotificationModel).filter(
                NotificationModel.priority == priority
            ).count()
            counts[f"{priority}_priority"] = count
        
        # Count unread notifications
        unread_count = self.db.query(NotificationModel).filter(
            NotificationModel.is_read == False
        ).count()
        counts["unread_notifications"] = unread_count
        
        # Total notifications
        total_count = self.db.query(NotificationModel).count()
        counts["total_notifications"] = total_count
        
        return counts
