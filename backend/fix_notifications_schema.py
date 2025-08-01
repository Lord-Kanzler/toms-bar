# fix_notifications_schema.py - Fix notifications table schema
from sqlalchemy import create_engine, text
from database import DATABASE_URL

def fix_notifications_schema():
    """Fix the notifications table schema to match the model"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if notifications table exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'"))
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                print("Creating notifications table...")
                # Create the notifications table with correct schema
                create_table_sql = """
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    title VARCHAR,
                    message TEXT,
                    notification_type VARCHAR DEFAULT 'info',
                    priority VARCHAR DEFAULT 'normal',
                    category VARCHAR DEFAULT 'general',
                    is_read BOOLEAN DEFAULT 0,
                    is_dismissed BOOLEAN DEFAULT 0,
                    created_at DATETIME,
                    read_at DATETIME,
                    expires_at DATETIME,
                    action_url VARCHAR,
                    action_label VARCHAR,
                    extra_data TEXT,
                    FOREIGN KEY(user_id) REFERENCES staff_members(id)
                )
                """
                conn.execute(text(create_table_sql))
                conn.commit()
                print("Notifications table created successfully!")
            else:
                print("Notifications table already exists")
                
                # Check current columns
                result = conn.execute(text("PRAGMA table_info(notifications)"))
                existing_columns = [row[1] for row in result.fetchall()]
                print(f"Existing columns: {existing_columns}")
                
                # Check if we need to rename recipient_id to user_id
                if 'recipient_id' in existing_columns and 'user_id' not in existing_columns:
                    print("Renaming recipient_id to user_id...")
                    conn.execute(text("ALTER TABLE notifications RENAME COLUMN recipient_id TO user_id"))
                    conn.commit()
                    print("Column renamed successfully!")
                
                # Add missing columns
                required_columns = [
                    ('user_id', 'INTEGER'),
                    ('title', 'VARCHAR'),
                    ('message', 'TEXT'),
                    ('notification_type', 'VARCHAR DEFAULT "info"'),
                    ('priority', 'VARCHAR DEFAULT "normal"'),
                    ('category', 'VARCHAR DEFAULT "general"'),
                    ('is_read', 'BOOLEAN DEFAULT 0'),
                    ('is_dismissed', 'BOOLEAN DEFAULT 0'),
                    ('created_at', 'DATETIME'),
                    ('read_at', 'DATETIME'),
                    ('expires_at', 'DATETIME'),
                    ('action_url', 'VARCHAR'),
                    ('action_label', 'VARCHAR'),
                    ('extra_data', 'TEXT')
                ]
                
                for column_name, column_type in required_columns:
                    if column_name not in existing_columns:
                        try:
                            conn.execute(text(f"ALTER TABLE notifications ADD COLUMN {column_name} {column_type}"))
                            conn.commit()
                            print(f"Added column: {column_name}")
                        except Exception as e:
                            print(f"Error adding column {column_name}: {e}")
                
        except Exception as e:
            print(f"Error fixing schema: {e}")

if __name__ == "__main__":
    print("Fixing notifications table schema...")
    fix_notifications_schema()
    print("Schema fix completed!")
