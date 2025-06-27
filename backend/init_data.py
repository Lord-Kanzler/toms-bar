# init_data.py - Initialize database with sample data
from datetime import datetime, timedelta, date
from sqlalchemy.orm import sessionmaker
from database import engine
from models import (
    Base, MenuItem, InventoryItem, StaffMember, Order, OrderItem,
    Timesheet, SalaryRecord, WorkSchedule, StockMovement, Sale,
    DailyReport, SystemSettings, Notification
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Clear existing data
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(MenuItem).delete()
    db.query(InventoryItem).delete()
    db.query(StaffMember).delete()
    db.commit()

    # Sample Menu Items
    menu_items = [
        MenuItem(
            name="Classic Burger",
            description="Beef patty with lettuce, tomato, and special sauce",
            price=12.99,
            category="Main Course",
            tags="Popular, Beef",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        MenuItem(
            name="Margherita Pizza",
            description="Classic pizza with tomato sauce, mozzarella, and basil",
            price=14.50,
            category="Main Course",
            tags="Vegetarian, Pizza",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        MenuItem(
            name="Caesar Salad",
            description="Fresh romaine lettuce with caesar dressing and croutons",
            price=9.99,
            category="Starters",
            tags="Vegetarian, Healthy",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        MenuItem(
            name="Mojito",
            description="Traditional Cuban cocktail with rum, mint, lime, and soda",
            price=9.99,
            category="Cocktails",
            tags="Alcoholic, Rum, Refreshing",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        MenuItem(
            name="Chocolate Sundae",
            description="Vanilla ice cream with hot chocolate sauce and nuts",
            price=6.50,
            category="Desserts",
            tags="Vegetarian, Sweet",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        MenuItem(
            name="House Red Wine",
            description="Our carefully selected house red wine",
            price=8.50,
            category="Wine",
            tags="Alcoholic, Wine",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        MenuItem(
            name="Grilled Salmon",
            description="Fresh Atlantic salmon with herbs and lemon",
            price=18.99,
            category="Main Course",
            tags="Fish, Healthy, Gluten-Free",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        MenuItem(
            name="Chicken Wings",
            description="Spicy buffalo wings with blue cheese dip",
            price=11.99,
            category="Starters",
            tags="Spicy, Chicken",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]

    # Sample Inventory Items
    inventory_items = [
        InventoryItem(
            name="Chicken Breast",
            category="Meat",
            current_stock=8.5,
            unit="kg",
            threshold=5.0,
            supplier="Fresh Meat Co.",
            last_updated=datetime.utcnow(),
            is_alcohol=False
        ),
        InventoryItem(
            name="Mozzarella Cheese",
            category="Dairy",
            current_stock=2.0,
            unit="kg",
            threshold=5.0,
            supplier="Dairy Fresh",
            last_updated=datetime.utcnow(),
            is_alcohol=False
        ),
        InventoryItem(
            name="White Rum",
            category="Alcohol",
            current_stock=1.0,
            unit="bottles",
            threshold=3.0,
            supplier="Spirits Wholesale",
            last_updated=datetime.utcnow(),
            is_alcohol=True,
            alcohol_type="Rum",
            alcohol_volume=40.0,
            bottle_size=750.0,
            par_level=6.0
        ),
        InventoryItem(
            name="Fresh Mint",
            category="Produce",
            current_stock=0.1,
            unit="kg",
            threshold=0.3,
            supplier="Green Gardens",
            last_updated=datetime.utcnow(),
            is_alcohol=False
        ),
        InventoryItem(
            name="Beef Patties",
            category="Meat",
            current_stock=15.0,
            unit="pieces",
            threshold=30.0,
            supplier="Premium Meat",
            last_updated=datetime.utcnow(),
            is_alcohol=False
        ),
        InventoryItem(
            name="Tomatoes",
            category="Produce",
            current_stock=5.2,
            unit="kg",
            threshold=3.0,
            supplier="Local Farm",
            last_updated=datetime.utcnow(),
            is_alcohol=False
        ),
        InventoryItem(
            name="Olive Oil",
            category="Pantry",
            current_stock=1.5,
            unit="L",
            threshold=2.0,
            supplier="Mediterranean Imports",
            last_updated=datetime.utcnow(),
            is_alcohol=False
        ),
        InventoryItem(
            name="Red Wine",
            category="Alcohol",
            current_stock=12.0,
            unit="bottles",
            threshold=8.0,
            supplier="Wine Distributors",
            last_updated=datetime.utcnow(),
            is_alcohol=True,
            alcohol_type="Wine",
            alcohol_volume=12.5,
            bottle_size=750.0,
            par_level=20.0
        )
    ]

    # Sample Staff Members
    staff_members = [
        StaffMember(
            name="Sarah Johnson",
            position="Manager",
            email="sarah@gastropro.com",
            phone="(555) 123-4567",
            hire_date=datetime(2020, 1, 15),
            is_active=True,
            profile_image="https://randomuser.me/api/portraits/women/44.jpg"
        ),
        StaffMember(
            name="Michael Brown",
            position="Head Chef",
            email="michael@gastropro.com",
            phone="(555) 234-5678",
            hire_date=datetime(2020, 3, 22),
            is_active=True,
            profile_image="https://randomuser.me/api/portraits/men/32.jpg"
        ),
        StaffMember(
            name="Emma Wilson",
            position="Waitress",
            email="emma@gastropro.com",
            phone="(555) 345-6789",
            hire_date=datetime(2021, 6, 10),
            is_active=True,
            profile_image="https://randomuser.me/api/portraits/women/68.jpg"
        ),
        StaffMember(
            name="David Martinez",
            position="Bartender",
            email="david@gastropro.com",
            phone="(555) 456-7890",
            hire_date=datetime(2021, 9, 5),
            is_active=True,
            profile_image="https://randomuser.me/api/portraits/men/45.jpg"
        ),
        StaffMember(
            name="Lisa Chen",
            position="Waitress",
            email="lisa@gastropro.com",
            phone="(555) 567-8901",
            hire_date=datetime(2022, 2, 14),
            is_active=True,
            profile_image="https://randomuser.me/api/portraits/women/85.jpg"
        ),
        StaffMember(
            name="James Thompson",
            position="Sous Chef",
            email="james@gastropro.com",
            phone="(555) 678-9012",
            hire_date=datetime(2022, 5, 20),
            is_active=True,
            profile_image="https://randomuser.me/api/portraits/men/67.jpg"
        )
    ]

    # Add all items to database
    db.add_all(menu_items)
    db.add_all(inventory_items)
    db.add_all(staff_members)
    db.commit()

    # Get IDs for creating sample orders
    menu_items_in_db = db.query(MenuItem).all()
    
    # Sample Orders
    orders = [
        Order(
            table_number=3,
            customer_name="John Smith",
            status="preparing",
            created_at=datetime.utcnow() - timedelta(minutes=30),
            total_amount=42.50
        ),
        Order(
            table_number=5,
            customer_name="Emma Johnson",
            status="ready",
            created_at=datetime.utcnow() - timedelta(minutes=15),
            total_amount=78.25
        ),
        Order(
            table_number=1,
            customer_name="Mike Davis",
            status="completed",
            created_at=datetime.utcnow() - timedelta(hours=2),
            total_amount=35.40
        ),
        Order(
            table_number=7,
            customer_name="Sarah Wilson",
            status="pending",
            created_at=datetime.utcnow() - timedelta(minutes=5),
            total_amount=24.90
        )
    ]

    db.add_all(orders)
    db.commit()

    # Sample Order Items
    orders_in_db = db.query(Order).all()
    order_items = []

    if len(orders_in_db) >= 4 and len(menu_items_in_db) >= 8:
        order_items = [
            # Order 1 items
            OrderItem(order_id=orders_in_db[0].id, menu_item_id=menu_items_in_db[0].id, quantity=1, special_instructions="No onions"),
            OrderItem(order_id=orders_in_db[0].id, menu_item_id=menu_items_in_db[3].id, quantity=2),
            
            # Order 2 items
            OrderItem(order_id=orders_in_db[1].id, menu_item_id=menu_items_in_db[1].id, quantity=1),
            OrderItem(order_id=orders_in_db[1].id, menu_item_id=menu_items_in_db[2].id, quantity=1),
            OrderItem(order_id=orders_in_db[1].id, menu_item_id=menu_items_in_db[5].id, quantity=2),
            
            # Order 3 items
            OrderItem(order_id=orders_in_db[2].id, menu_item_id=menu_items_in_db[6].id, quantity=1),
            OrderItem(order_id=orders_in_db[2].id, menu_item_id=menu_items_in_db[4].id, quantity=1),
            
            # Order 4 items
            OrderItem(order_id=orders_in_db[3].id, menu_item_id=menu_items_in_db[7].id, quantity=1),
            OrderItem(order_id=orders_in_db[3].id, menu_item_id=menu_items_in_db[3].id, quantity=1)
        ]

        db.add_all(order_items)
        db.commit()

    print("✅ Database initialized successfully!")
    print(f"   📋 {len(menu_items)} menu items added")
    print(f"   📦 {len(inventory_items)} inventory items added")
    print(f"   👥 {len(staff_members)} staff members added")
    print(f"   🍽️ {len(orders)} orders added")
    print(f"   📝 {len(order_items)} order items added")

except Exception as e:
    print(f"❌ Error initializing database: {e}")
    db.rollback()
finally:
    db.close()
