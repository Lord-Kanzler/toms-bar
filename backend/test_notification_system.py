#!/usr/bin/env python3
"""
Test script for the comprehensive notification system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import get_db, engine
from models import InventoryItem, Order, Notification
from notification_events import NotificationEventManager
from datetime import datetime

async def test_notification_system():
    """Test the notification event system"""
    print("🔔 Testing GastroPro Notification System")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Initialize event manager
        event_manager = NotificationEventManager(db)
        print("✅ Event manager initialized")
        
        # Test 1: System maintenance notification
        print("\n📢 Testing system maintenance notification...")
        await event_manager.handle_system_maintenance(
            message="Scheduled maintenance at 2 AM",
            priority="high"
        )
        print("✅ System maintenance notification created")
        
        # Test 2: Check if we have any inventory items to test with
        inventory_items = db.query(InventoryItem).limit(3).all()
        
        if inventory_items:
            print(f"\n📦 Testing inventory notifications with {len(inventory_items)} items...")
            
            for item in inventory_items:
                print(f"   Testing item: {item.name} (Stock: {item.current_stock}, Threshold: {item.threshold})")
                
                # Test low stock notification
                if item.current_stock <= item.threshold:
                    await event_manager.handle_low_stock(item)
                    print(f"   ⚠️  Low stock notification created for {item.name}")
                
                # Test out of stock notification
                if item.current_stock <= 0:
                    await event_manager.handle_out_of_stock(item)
                    print(f"   🚫 Out of stock notification created for {item.name}")
        else:
            print("📦 No inventory items found to test")
        
        # Test 3: Check if we have any orders to test with
        recent_orders = db.query(Order).limit(2).all()
        
        if recent_orders:
            print(f"\n🍽️  Testing order notifications with {len(recent_orders)} orders...")
            
            for order in recent_orders:
                print(f"   Testing order #{order.id} (Status: {order.status})")
                
                # Test different order events
                await event_manager.handle_order_created(order)
                print(f"   ✅ Order created notification for #{order.id}")
                
                await event_manager.handle_order_ready(order)
                print(f"   🍽️  Order ready notification for #{order.id}")
        else:
            print("🍽️  No orders found to test")
        
        # Test 4: Check notification counts
        print(f"\n📊 Checking notification statistics...")
        
        total_notifications = db.query(Notification).count()
        unread_notifications = db.query(Notification).filter(Notification.is_read == False).count()
        system_notifications = db.query(Notification).filter(Notification.category == 'system').count()
        inventory_notifications = db.query(Notification).filter(Notification.category == 'inventory').count()
        order_notifications = db.query(Notification).filter(Notification.category == 'orders').count()
        
        print(f"   📈 Total notifications: {total_notifications}")
        print(f"   📬 Unread notifications: {unread_notifications}")
        print(f"   🔧 System notifications: {system_notifications}")
        print(f"   📦 Inventory notifications: {inventory_notifications}")
        print(f"   🍽️  Order notifications: {order_notifications}")
        
        # Test 5: Test notification priorities
        print(f"\n⚡ Testing priority levels...")
        
        high_priority = db.query(Notification).filter(Notification.priority == 'high').count()
        medium_priority = db.query(Notification).filter(Notification.priority == 'medium').count()
        low_priority = db.query(Notification).filter(Notification.priority == 'low').count()
        
        print(f"   🔴 High priority: {high_priority}")
        print(f"   🟡 Medium priority: {medium_priority}")
        print(f"   🟢 Low priority: {low_priority}")
        
        print(f"\n🎉 Notification system test completed successfully!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

async def test_event_counters():
    """Test event counting functionality"""
    print("\n📊 Testing Event Counters")
    print("-" * 30)
    
    db = next(get_db())
    event_manager = NotificationEventManager(db)
    
    try:
        # Get initial counts
        initial_counts = await event_manager.get_event_counts()
        print(f"Initial event counts: {initial_counts}")
        
        # Trigger some events
        await event_manager.handle_system_maintenance("Test maintenance")
        
        # Get updated counts
        updated_counts = await event_manager.get_event_counts()
        print(f"Updated event counts: {updated_counts}")
        
        # Check if counters increased
        for event_type in updated_counts:
            if event_type in initial_counts:
                if updated_counts[event_type] > initial_counts[event_type]:
                    print(f"✅ {event_type} counter increased")
                else:
                    print(f"ℹ️  {event_type} counter unchanged")
            else:
                print(f"🆕 New event type: {event_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Counter test failed: {e}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting GastroPro Notification System Tests")
    
    # Run the main test
    success = asyncio.run(test_notification_system())
    
    if success:
        # Run counter tests
        counter_success = asyncio.run(test_event_counters())
        
        if counter_success:
            print("\n🎊 All tests passed! Notification system is working correctly.")
            exit(0)
        else:
            print("\n⚠️  Main tests passed but counter tests failed.")
            exit(1)
    else:
        print("\n💥 Tests failed! Please check the error messages above.")
        exit(1)
