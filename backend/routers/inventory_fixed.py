# inventory.py - Inventory Management API router
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models import InventoryItem as InventoryItemModel
from database import get_db
from schemas import InventoryItem as InventoryItemSchema, InventoryItemCreate, InventoryItemUpdate

router = APIRouter()


@router.get("/", response_model=List[InventoryItemSchema])
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
    return [InventoryItemSchema.from_orm(item) for item in inventory_items]


@router.get("/low-stock", response_model=List[InventoryItemSchema])
async def get_low_stock_items(db: Session = Depends(get_db)):
    """Get all inventory items with stock below threshold"""
    low_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= InventoryItemModel.threshold
    ).all()
    return [InventoryItemSchema.from_orm(item) for item in low_stock_items]


@router.get("/out-of-stock", response_model=List[InventoryItemSchema])
async def get_out_of_stock_items(db: Session = Depends(get_db)):
    """Get all inventory items with zero stock"""
    out_of_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= 0
    ).all()
    return [InventoryItemSchema.from_orm(item) for item in out_of_stock_items]


@router.get("/{item_id}", response_model=InventoryItemSchema)
async def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific inventory item by ID"""
    inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return InventoryItemSchema.from_orm(inventory_item)


@router.post("/", response_model=InventoryItemSchema)
async def create_inventory_item(inventory_item: InventoryItemCreate, db: Session = Depends(get_db)):
    """Create a new inventory item"""
    db_inventory_item = InventoryItemModel(
        name=inventory_item.name,
        category=inventory_item.category,
        current_stock=inventory_item.current_stock,
        unit=inventory_item.unit,
        threshold=inventory_item.minimum_stock,
        supplier=inventory_item.supplier,
        last_updated=datetime.utcnow(),
        is_alcohol=False  # Default value, can be updated later
    )
    db.add(db_inventory_item)
    db.commit()
    db.refresh(db_inventory_item)
    return InventoryItemSchema.from_orm(db_inventory_item)


@router.put("/{item_id}", response_model=InventoryItemSchema)
async def update_inventory_item(item_id: int, inventory_item: InventoryItemUpdate, db: Session = Depends(get_db)):
    """Update an existing inventory item"""
    db_inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = inventory_item.dict(exclude_unset=True)
    
    # Map minimum_stock to threshold if it exists in the update data
    if "minimum_stock" in update_data:
        update_data["threshold"] = update_data.pop("minimum_stock")
    
    for field, value in update_data.items():
        if hasattr(db_inventory_item, field):
            setattr(db_inventory_item, field, value)
    
    db_inventory_item.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_inventory_item)
    return InventoryItemSchema.from_orm(db_inventory_item)


@router.delete("/{item_id}")
async def delete_inventory_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an inventory item"""
    db_inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    db.delete(db_inventory_item)
    db.commit()
    return {"message": "Inventory item deleted successfully"}


@router.get("/categories/list")
async def get_inventory_categories(db: Session = Depends(get_db)):
    """Get all unique inventory categories"""
    categories = db.query(InventoryItemModel.category).distinct().all()
    return [category[0] for category in categories if category[0]]


@router.patch("/{item_id}/stock", response_model=InventoryItemSchema)
async def update_stock_level(
    item_id: int, 
    new_stock: float,
    db: Session = Depends(get_db)
):
    """Update the stock level of an inventory item"""
    db_inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    db_inventory_item.current_stock = new_stock
    db_inventory_item.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_inventory_item)
    return InventoryItemSchema.from_orm(db_inventory_item)


@router.get("/alcohol", response_model=List[InventoryItemSchema])
async def get_alcohol_inventory(db: Session = Depends(get_db)):
    """Get all alcohol inventory items"""
    alcohol_items = db.query(InventoryItemModel).filter(InventoryItemModel.is_alcohol == True).all()
    return [InventoryItemSchema.from_orm(item) for item in alcohol_items]


@router.get("/alcohol/by-type")
async def get_alcohol_by_type(db: Session = Depends(get_db)):
    """Get all alcohol inventory items grouped by type"""
    alcohol_items = db.query(InventoryItemModel).filter(InventoryItemModel.is_alcohol == True).all()
    
    # Group by alcohol type
    grouped = {}
    for item in alcohol_items:
        alcohol_type = item.alcohol_type or "Other"
        if alcohol_type not in grouped:
            grouped[alcohol_type] = []
        grouped[alcohol_type].append(InventoryItemSchema.from_orm(item))
    
    return grouped
