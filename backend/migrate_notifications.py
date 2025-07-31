# migrate_notifications.py - Database migration for enhanced notifications

from sqlalchemy import create_engine, text
from database import DATABASE_URL

def migrate_notifications():
    """Add new fields to notifications table"""
    engine = create_engine(DATABASE_URL)
    
    # List of columns to add with their SQL types
    new_columns = [
        ("priority", "VARCHAR DEFAULT 'normal'"),
        ("category", "VARCHAR DEFAULT 'general'"),
        ("is_dismissed", "BOOLEAN DEFAULT 0"),
        ("expires_at", "DATETIME"),
        ("action_url", "VARCHAR"),
        ("action_label", "VARCHAR"),
        ("metadata", "TEXT")
    ]
    
    with engine.connect() as conn:
        # Check which columns already exist
        result = conn.execute(text("PRAGMA table_info(notifications)"))
        existing_columns = [row[1] for row in result.fetchall()]
        
        print("Existing columns in notifications table:", existing_columns)
        
        # Add missing columns
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE notifications ADD COLUMN {column_name} {column_type}"
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"Added column: {column_name}")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
            else:
                print(f"Column {column_name} already exists")

def create_sample_notifications():
    """Create some sample notifications for testing"""
    from datetime import datetime, timedelta
    import json
    
    engine = create_engine(DATABASE_URL)
    
    sample_notifications = [
        {
            'title': 'Low Stock Alert',
            'message': 'Mozzarella Cheese is running low (Current: 2.0 kg, Threshold: 5.0 kg)',
            'notification_type': 'warning',
            'priority': 'high',
            'category': 'inventory',
            'action_url': '/inventory#2',
            'action_label': 'Restock Item',
            'metadata': json.dumps({
                'item_id': 2,
                'item_name': 'Mozzarella Cheese',
                'current_stock': 2.0,
                'threshold': 5.0
            }),
            'expires_at': datetime.now() + timedelta(days=7)
        },
        {
            'title': 'New Order Received',
            'message': 'Order #1 has been placed and requires attention',
            'notification_type': 'info',
            'priority': 'normal',
            'category': 'orders',
            'action_url': '/orders#1',
            'action_label': 'View Order',
            'metadata': json.dumps({
                'order_id': 1,
                'event_type': 'new_order'
            }),
            'expires_at': datetime.now() + timedelta(hours=24)
        },
        {
            'title': 'System Maintenance',
            'message': 'System maintenance is scheduled for tonight at 2 AM. Expected downtime: 30 minutes.',
            'notification_type': 'info',
            'priority': 'normal',
            'category': 'system',
            'expires_at': datetime.now() + timedelta(days=1)
        },
        {
            'title': 'Critical Stock Alert',
            'message': 'Fresh Mint is out of stock! Immediate restocking required.',
            'notification_type': 'error',
            'priority': 'urgent',
            'category': 'inventory',
            'action_url': '/inventory#4',
            'action_label': 'Emergency Restock',
            'metadata': json.dumps({
                'item_id': 4,
                'item_name': 'Fresh Mint',
                'current_stock': 0.1,
                'threshold': 0.3
            }),
            'expires_at': datetime.now() + timedelta(days=3)
        }
    ]
    
    with engine.connect() as conn:
        for notification in sample_notifications:
            try:
                # Convert expires_at to string for SQLite
                expires_at_str = notification['expires_at'].isoformat() if notification.get('expires_at') else None
                
                sql = text("""
                    INSERT INTO notifications 
                    (title, message, notification_type, priority, category, action_url, action_label, metadata, expires_at, created_at)
                    VALUES 
                    (:title, :message, :notification_type, :priority, :category, :action_url, :action_label, :metadata, :expires_at, :created_at)
                """)
                
                conn.execute(sql, {
                    'title': notification['title'],
                    'message': notification['message'],
                    'notification_type': notification['notification_type'],
                    'priority': notification['priority'],
                    'category': notification['category'],
                    'action_url': notification.get('action_url'),
                    'action_label': notification.get('action_label'),
                    'metadata': notification.get('metadata'),
                    'expires_at': expires_at_str,
                    'created_at': datetime.now().isoformat()
                })
                conn.commit()
                print(f"Created sample notification: {notification['title']}")
            except Exception as e:
                print(f"Error creating notification '{notification['title']}': {e}")

if __name__ == "__main__":
    print("Starting notification system migration...")
    
    try:
        # Run the migration
        migrate_notifications()
        print("Migration completed successfully!")
        
        # Create sample notifications
        print("\nCreating sample notifications...")
        create_sample_notifications()
        print("Sample notifications created!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
