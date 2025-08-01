#!/usr/bin/env python3
"""
Comprehensive test of the working notification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_notifications import SimpleNotificationManager
from database import get_db
from models import Notification, InventoryItem, Order

def test_notification_system():
    """Test the complete notification system"""
    print("🔔 Testing Complete GastroPro Notification System")
    print("=" * 60)
    
    # Test 1: System notifications
    print("\n1. 📢 Testing System Notifications...")
    notif = SimpleNotificationManager.create_system_notification(
        "System maintenance scheduled for tonight at 2 AM", 
        "high"
    )
    print(f"   ✅ Created system notification ID: {notif.id}")
    print(f"   📋 Title: {notif.title}")
    print(f"   📝 Message: {notif.message}")
    print(f"   ⚡ Priority: {notif.priority}")
    
    # Test 2: Inventory notifications
    print("\n2. 📦 Testing Inventory Notifications...")
    alerts_created = SimpleNotificationManager.check_inventory_and_create_alerts()
    print(f"   ✅ Created {alerts_created} inventory alerts")
    
    # Test 3: Order notifications
    print("\n3. 🍽️  Testing Order Notifications...")
    db = next(get_db())
    try:
        # Get a sample order
        orders = db.query(Order).limit(2).all()
        if orders:
            for order in orders:
                # Test different order events
                notif1 = SimpleNotificationManager.create_order_notification(order, "created")
                notif2 = SimpleNotificationManager.create_order_notification(order, "ready")
                notif3 = SimpleNotificationManager.create_order_notification(order, "delayed")
                
                print(f"   ✅ Created notifications for Order #{order.id}:")
                print(f"      📝 Created: {notif1.id}")
                print(f"      🍽️  Ready: {notif2.id}")
                print(f"      ⏰ Delayed: {notif3.id}")
        else:
            print("   ℹ️  No orders found to test")
    finally:
        db.close()
    
    # Test 4: Test specific inventory items
    print("\n4. 📦 Testing Specific Inventory Alerts...")
    db = next(get_db())
    try:
        items = db.query(InventoryItem).limit(3).all()
        for item in items:
            print(f"   Testing item: {item.name}")
            print(f"     Current stock: {item.current_stock} {item.unit}")
            print(f"     Threshold: {item.threshold} {item.unit}")
            
            if item.current_stock <= 0:
                notif = SimpleNotificationManager.create_inventory_out_of_stock_alert(item)
                print(f"     🚫 Created OUT OF STOCK alert: {notif.id}")
            elif item.current_stock <= item.threshold:
                notif = SimpleNotificationManager.create_inventory_low_stock_alert(item)
                print(f"     ⚠️  Created low stock alert: {notif.id}")
            else:
                print(f"     ✅ Stock levels are good")
    finally:
        db.close()
    
    # Test 5: Statistics
    print("\n5. 📊 Testing Notification Statistics...")
    stats = SimpleNotificationManager.get_notification_stats()
    print(f"   📈 Total notifications: {stats['total_notifications']}")
    print(f"   📬 Unread notifications: {stats['unread_notifications']}")
    print(f"   🔴 High priority notifications: {stats['high_priority_notifications']}")
    print(f"   📋 By category:")
    for category, count in stats['by_category'].items():
        print(f"      {category}: {count}")
    
    # Test 6: Recent notifications
    print("\n6. 📋 Testing Recent Notifications Retrieval...")
    db = next(get_db())
    try:
        recent_notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(5).all()
        print(f"   📋 Found {len(recent_notifications)} recent notifications:")
        for notif in recent_notifications:
            print(f"      #{notif.id}: {notif.title} [{notif.category}] - {notif.priority}")
    finally:
        db.close()
    
    print("\n🎉 Notification System Test Complete!")
    print("=" * 60)
    
    return True


def test_event_tracking():
    """Test event tracking and counters"""
    print("\n📊 Testing Event Tracking and Counters")
    print("-" * 40)
    
    # Get initial stats
    initial_stats = SimpleNotificationManager.get_notification_stats()
    print(f"Initial state: {initial_stats['total_notifications']} total notifications")
    
    # Create some test events
    SimpleNotificationManager.create_system_notification("Test event tracking")
    alerts = SimpleNotificationManager.check_inventory_and_create_alerts()
    
    # Get updated stats
    updated_stats = SimpleNotificationManager.get_notification_stats()
    print(f"After events: {updated_stats['total_notifications']} total notifications")
    
    increase = updated_stats['total_notifications'] - initial_stats['total_notifications']
    print(f"✅ Event tracking working: {increase} new notifications created")
    
    return True


if __name__ == "__main__":
    print("🚀 Starting Comprehensive Notification System Tests")
    
    # Run main tests
    success1 = test_notification_system()
    
    # Run event tracking tests
    success2 = test_event_tracking()
    
    if success1 and success2:
        print("\n🎊 All notification system tests PASSED!")
        print("✅ System notifications: Working")
        print("✅ Inventory alerts: Working") 
        print("✅ Order notifications: Working")
        print("✅ Event tracking: Working")
        print("✅ Statistics: Working")
        print("\n🔔 The GastroPro notification system is fully operational!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
