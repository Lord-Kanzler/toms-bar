# inventory.py - Inventory Management API router
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models import InventoryItem as InventoryItemModel
from database import get_db
import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.InventoryItem])
async def get_inventory_items(
    category: Optional[str] = None,
    low_stock_only: bool = False,
    alcohol_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get all inventory items with optional filtering"""
    query = db.query(InventoryItemModel)
    
    if category:
        query = query.filter(InventoryItemModel.category == category)
    
    if low_stock_only:
        query = query.filter(InventoryItemModel.current_stock <= InventoryItemModel.threshold)
    
    if alcohol_only:
        query = query.filter(InventoryItemModel.is_alcohol == True)
    
    inventory_items = query.all()
    return inventory_items


@router.get("/low-stock", response_model=List[schemas.InventoryItem])
async def get_low_stock_items(db: Session = Depends(get_db)):
    """Get items that are below threshold"""
    low_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= InventoryItemModel.threshold
    ).all()
    return low_stock_items


@router.get("/out-of-stock", response_model=List[schemas.InventoryItem])
async def get_out_of_stock_items(db: Session = Depends(get_db)):
    """Get items that are out of stock"""
    out_of_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= 0
    ).all()
    return out_of_stock_items


@router.get("/{item_id}", response_model=schemas.InventoryItem)
async def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific inventory item by ID"""
    inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory_item


@router.post("/", response_model=schemas.InventoryItem)
async def create_inventory_item(inventory_item: schemas.InventoryItemCreate, db: Session = Depends(get_db)):
    """Create a new inventory item"""
    db_inventory_item = InventoryItemModel(
        name=inventory_item.name,
        category=inventory_item.category,
        current_stock=inventory_item.current_stock,
        unit=inventory_item.unit,
        threshold=inventory_item.threshold,
        supplier=inventory_item.supplier,
        is_alcohol=inventory_item.is_alcohol,
        alcohol_type=inventory_item.alcohol_type,
        alcohol_volume=inventory_item.alcohol_volume,
        bottle_size=inventory_item.bottle_size,
        par_level=inventory_item.par_level,
        last_updated=datetime.utcnow()
    )
    db.add(db_inventory_item)
    db.commit()
    db.refresh(db_inventory_item)
    return db_inventory_item


@router.put("/{item_id}", response_model=schemas.InventoryItem)
async def update_inventory_item(item_id: int, inventory_item: schemas.InventoryItemUpdate, db: Session = Depends(get_db)):
    """Update an existing inventory item"""
    db_inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = inventory_item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_inventory_item, field, value)
    
    db_inventory_item.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_inventory_item)
    return db_inventory_item


@router.delete("/{item_id}")
async def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an inventory item"""
    db_inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    db.delete(db_inventory_item)
    db.commit()
    return {"message": "Inventory item deleted successfully"}


@router.patch("/{item_id}/stock")
async def update_stock(item_id: int, stock_change: float, db: Session = Depends(get_db)):
    """Update stock quantity (positive to add, negative to subtract)"""
    db_inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    new_stock = db_inventory_item.current_stock + stock_change
    if new_stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    
    db_inventory_item.current_stock = new_stock
    db_inventory_item.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_inventory_item)
    return db_inventory_item


@router.get("/categories/list")
async def get_inventory_categories(db: Session = Depends(get_db)):
    """Get all unique inventory categories"""
    categories = db.query(InventoryItemModel.category).distinct().all()
    return [category[0] for category in categories if category[0]]


@router.get("/summary/stats")
async def get_inventory_summary(db: Session = Depends(get_db)):
    """Get inventory summary statistics"""
    total_items = db.query(InventoryItemModel).count()
    low_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= InventoryItemModel.threshold
    ).count()
    out_of_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= 0
    ).count()
    
    return {
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items
    }
