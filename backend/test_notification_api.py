#!/usr/bin/env python3
"""
Test API endpoints for the notification system
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"

def test_notification_endpoints():
    """Test the notification API endpoints"""
    print("🌐 Testing GastroPro Notification API Endpoints")
    print("=" * 50)
    
    try:
        # Test 1: Get all notifications
        print("\n📬 Testing GET /api/notifications")
        response = requests.get(f"{BASE_URL}/notifications")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            notifications = response.json()
            print(f"   ✅ Found {len(notifications)} notifications")
            if notifications:
                latest = notifications[0]
                print(f"   📋 Latest: {latest.get('title', 'No title')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            
        # Test 2: Get unread notifications only
        print("\n📬 Testing GET /api/notifications?unread_only=true")
        response = requests.get(f"{BASE_URL}/notifications?unread_only=true")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            unread = response.json()
            print(f"   ✅ Found {len(unread)} unread notifications")
        
        # Test 3: Get notification statistics
        print("\n📊 Testing GET /api/notifications/stats")
        response = requests.get(f"{BASE_URL}/notifications/stats")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Stats: {json.dumps(stats, indent=2)}")
        
        # Test 4: Test system maintenance notification trigger
        print("\n🔧 Testing POST /api/notifications/trigger-system-maintenance")
        response = requests.post(
            f"{BASE_URL}/notifications/trigger-system-maintenance",
            params={
                "message": "Test maintenance notification from API",
                "priority": "high"
            }
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Result: {result}")
        
        # Test 5: Test inventory alerts check
        print("\n📦 Testing POST /api/notifications/check-inventory-alerts")
        response = requests.post(f"{BASE_URL}/notifications/check-inventory-alerts")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Result: {result}")
        
        # Test 6: Create a test notification
        print("\n➕ Testing POST /api/notifications")
        test_notification = {
            "title": "API Test Notification",
            "message": "This is a test notification created via API",
            "notification_type": "info",
            "priority": "normal",
            "category": "system"
        }
        response = requests.post(
            f"{BASE_URL}/notifications",
            json=test_notification
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            notification = response.json()
            print(f"   ✅ Created notification ID: {notification.get('id')}")
            notification_id = notification.get('id')
            
            # Test 7: Mark notification as read
            if notification_id:
                print(f"\n✅ Testing PATCH /api/notifications/{notification_id}/mark-read")
                response = requests.patch(f"{BASE_URL}/notifications/{notification_id}/mark-read")
                print(f"   Status Code: {response.status_code}")
                if response.status_code == 200:
                    updated = response.json()
                    print(f"   ✅ Marked as read: {updated.get('is_read')}")
        
        print("\n🎉 All API endpoint tests completed!")
        print("=" * 50)
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_notification_endpoints()
    if success:
        print("\n🎊 All API tests passed!")
        sys.exit(0)
    else:
        print("\n💥 API tests failed!")
        sys.exit(1)
