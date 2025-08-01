# orders.py - Orders API router
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from models import Order as OrderModel, OrderItem as OrderItemModel
from database import get_db
import schemas
from schemas import Order as OrderSchema
from simple_notifications import SimpleNotificationManager

router = APIRouter()


@router.get("/", response_model=List[OrderSchema])
async def get_orders(db: Session = Depends(get_db)):
    """Get all orders"""
    orders = db.query(OrderModel).all()
    return orders


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=schemas.Order)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    db_order = OrderModel(
        table_number=order.table_number,
        customer_name=order.customer_name,
        status=order.status,
        created_at=datetime.utcnow(),
        total_amount=order.total_amount,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items
    for item in order.items:
        db_order_item = OrderItemModel(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            special_instructions=item.special_instructions
        )
        db.add(db_order_item)
    
    db.commit()
    db.refresh(db_order)
    
    # Create notification for new order using simple notification manager
    SimpleNotificationManager.create_order_notification(db_order, "created")
    
    return db_order


@router.put("/{order_id}", response_model=schemas.Order)
async def update_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)):
    """Update an existing order"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = order.dict(exclude_unset=True)
    old_status = db_order.status
    
    for field, value in update_data.items():
        setattr(db_order, field, value)
    
    db.commit()
    db.refresh(db_order)
    
    # Create notifications for status changes using simple notification manager
    if old_status != db_order.status:
        if db_order.status == "ready":
            SimpleNotificationManager.create_order_notification(db_order, "ready")
        elif db_order.status == "delayed":
            SimpleNotificationManager.create_order_notification(db_order, "delayed")
    
    return db_order


@router.delete("/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted successfully"}


@router.patch("/{order_id}/status")
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    """Update order status"""
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order
