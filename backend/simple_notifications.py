#!/usr/bin/env python3
"""
Simple, working notification system for GastroPro
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models import Notification, InventoryItem, Order
import json

class SimpleNotificationManager:
    """Simple notification manager that actually works"""
    
    @staticmethod
    def create_notification(
        title: str,
        message: str,
        category: str = "system",
        priority: str = "normal",
        notification_type: str = "info",
        user_id: int = None,
        action_url: str = None,
        action_label: str = None,
        extra_data: dict = None,
        expires_hours: int = 24
    ) -> Notification:
        """Create a notification in the database"""
        db = next(get_db())
        try:
            notification = Notification(
                title=title,
                message=message,
                category=category,
                priority=priority,
                notification_type=notification_type,
                user_id=user_id,
                action_url=action_url,
                action_label=action_label,
                extra_data=json.dumps(extra_data) if extra_data else None,
                expires_at=datetime.now() + timedelta(hours=expires_hours),
                is_read=False,
                is_dismissed=False,
                created_at=datetime.now(),
                read_at=None
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            return notification
        finally:
            db.close()
    
    @staticmethod
    def create_inventory_low_stock_alert(item: InventoryItem) -> Notification:
        """Create low stock alert for inventory item"""
        return SimpleNotificationManager.create_notification(
            title=f"Low Stock: {item.name}",
            message=f"{item.name} is running low (Current: {item.current_stock} {item.unit}, Threshold: {item.threshold} {item.unit})",
            category="inventory",
            priority="medium",
            notification_type="warning",
            action_url=f"/inventory#{item.id}",
            action_label="Restock Item",
            extra_data={
                "item_id": item.id,
                "current_stock": item.current_stock,
                "threshold": item.threshold,
                "supplier": item.supplier
            },
            expires_hours=48
        )
    
    @staticmethod
    def create_inventory_out_of_stock_alert(item: InventoryItem) -> Notification:
        """Create out of stock alert for inventory item"""
        return SimpleNotificationManager.create_notification(
            title=f"OUT OF STOCK: {item.name}",
            message=f"{item.name} is completely out of stock! Immediate restocking required.",
            category="inventory",
            priority="high",
            notification_type="error",
            action_url=f"/inventory#{item.id}",
            action_label="Emergency Restock",
            extra_data={
                "item_id": item.id,
                "current_stock": item.current_stock,
                "supplier": item.supplier,
                "emergency": True
            },
            expires_hours=24
        )
    
    @staticmethod
    def create_order_notification(order: Order, event_type: str) -> Notification:
        """Create order-related notification"""
        
        if event_type == "created":
            title = "New Order Received"
            message = f"Order #{order.id} has been placed" + (f" for table {order.table_number}" if order.table_number else "")
            priority = "normal"
            notification_type = "info"
        elif event_type == "ready":
            title = "Order Ready"
            message = f"Order #{order.id} is ready for pickup/delivery" + (f" (Table {order.table_number})" if order.table_number else "")
            priority = "normal"
            notification_type = "success"
        elif event_type == "delayed":
            title = "Order Delayed"
            message = f"Order #{order.id} is experiencing delays" + (f" (Table {order.table_number})" if order.table_number else "")
            priority = "high"
            notification_type = "warning"
        else:
            title = f"Order Update"
            message = f"Order #{order.id} status: {event_type}"
            priority = "normal"
            notification_type = "info"
        
        return SimpleNotificationManager.create_notification(
            title=title,
            message=message,
            category="orders",
            priority=priority,
            notification_type=notification_type,
            action_url=f"/orders#{order.id}",
            action_label="View Order",
            extra_data={
                "order_id": order.id,
                "table_number": order.table_number,
                "customer_name": order.customer_name,
                "event_type": event_type
            },
            expires_hours=12
        )
    
    @staticmethod
    def create_system_notification(message: str, priority: str = "normal") -> Notification:
        """Create system notification"""
        return SimpleNotificationManager.create_notification(
            title="System Notification",
            message=message,
            category="system",
            priority=priority,
            notification_type="info",
            extra_data={"timestamp": datetime.now().isoformat()},
            expires_hours=72
        )
    
    @staticmethod
    def check_inventory_and_create_alerts():
        """Check all inventory items and create alerts as needed"""
        db = next(get_db())
        alerts_created = 0
        
        try:
            items = db.query(InventoryItem).all()
            
            for item in items:
                # Check if we already have recent alerts for this item
                recent_alert = db.query(Notification).filter(
                    Notification.category == "inventory",
                    Notification.extra_data.like(f'%"item_id": {item.id}%'),
                    Notification.created_at > datetime.now() - timedelta(hours=6),
                    Notification.is_dismissed == False
                ).first()
                
                if recent_alert:
                    continue  # Skip if recent alert exists
                
                if item.current_stock <= 0:
                    SimpleNotificationManager.create_inventory_out_of_stock_alert(item)
                    alerts_created += 1
                elif item.current_stock <= item.threshold:
                    SimpleNotificationManager.create_inventory_low_stock_alert(item)
                    alerts_created += 1
            
            return alerts_created
        finally:
            db.close()
    
    @staticmethod
    def get_notification_stats():
        """Get notification statistics"""
        db = next(get_db())
        try:
            total = db.query(Notification).count()
            unread = db.query(Notification).filter(Notification.is_read == False).count()
            high_priority = db.query(Notification).filter(Notification.priority == "high").count()
            
            by_category = {}
            for category in ["inventory", "orders", "system", "staff"]:
                count = db.query(Notification).filter(Notification.category == category).count()
                by_category[category] = count
            
            return {
                "total_notifications": total,
                "unread_notifications": unread,
                "high_priority_notifications": high_priority,
                "by_category": by_category
            }
        finally:
            db.close()


# Test function
def test_simple_notifications():
    """Test the simple notification system"""
    print("Testing Simple Notification System...")
    
    # Test system notification
    notif = SimpleNotificationManager.create_system_notification("Test notification system")
    print(f"Created system notification: {notif.id}")
    
    # Check inventory alerts
    alerts = SimpleNotificationManager.check_inventory_and_create_alerts()
    print(f"Created {alerts} inventory alerts")
    
    # Get stats
    stats = SimpleNotificationManager.get_notification_stats()
    print(f"Notification stats: {stats}")
    
    return True

if __name__ == "__main__":
    test_simple_notifications()
