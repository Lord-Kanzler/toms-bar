#!/usr/bin/env python3
"""
Test the notification API endpoints directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

def test_notification_api():
    """Test notification API endpoints"""
    print("🌐 Testing Notification API Endpoints")
    print("=" * 50)
    
    client = TestClient(app)
    
    # Test 1: Get all notifications
    print("\n1. 📬 Testing GET /api/notifications")
    response = client.get("/api/notifications")
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        notifications = response.json()
        print(f"   ✅ Found {len(notifications)} notifications")
        if notifications:
            print(f"   📋 Latest: {notifications[0].get('title', 'No title')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test 2: Get unread notifications
    print("\n2. 📬 Testing GET /api/notifications?unread_only=true")
    response = client.get("/api/notifications?unread_only=true")
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        unread = response.json()
        print(f"   ✅ Found {len(unread)} unread notifications")
    
    # Test 3: Get simple stats
    print("\n3. 📊 Testing GET /api/notifications/simple-stats")
    response = client.get("/api/notifications/simple-stats")
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Stats: Total={stats.get('total_notifications')}, Unread={stats.get('unread_notifications')}")
    
    # Test 4: Create system maintenance notification
    print("\n4. 🔧 Testing POST /api/notifications/trigger-system-maintenance")
    response = client.post(
        "/api/notifications/trigger-system-maintenance",
        params={"message": "API test maintenance", "priority": "normal"}
    )
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Created notification ID: {result.get('notification_id')}")
    
    # Test 5: Check inventory alerts
    print("\n5. 📦 Testing POST /api/notifications/check-inventory-alerts")
    response = client.post("/api/notifications/check-inventory-alerts")
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Result: {result.get('message')}")
    
    # Test 6: Create a notification
    print("\n6. ➕ Testing POST /api/notifications")
    test_notification = {
        "title": "API Test Notification",
        "message": "This notification was created via API test",
        "notification_type": "info",
        "priority": "normal",
        "category": "system"
    }
    response = client.post("/api/notifications", json=test_notification)
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        notification = response.json()
        print(f"   ✅ Created notification ID: {notification.get('id')}")
        
        # Test 7: Mark as read
        notification_id = notification.get('id')
        if notification_id:
            print(f"\n7. ✅ Testing PATCH /api/notifications/{notification_id}/mark-read")
            response = client.patch(f"/api/notifications/{notification_id}/mark-read")
            print(f"   Status Code: {response.status_code}")
            if response.status_code == 200:
                updated = response.json()
                print(f"   ✅ Marked as read: {updated.get('is_read')}")
    
    print("\n🎉 All API endpoint tests completed!")
    return True

if __name__ == "__main__":
    success = test_notification_api()
    if success:
        print("\n🎊 API tests PASSED!")
        print("✅ The notification API endpoints are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ API tests FAILED!")
        sys.exit(1)
