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
    return [schemas.InventoryItem.from_orm(item) for item in inventory_items]


@router.get("/low-stock", response_model=List[schemas.InventoryItem])
async def get_low_stock_items(db: Session = Depends(get_db)):
    """Get items that are below threshold"""
    low_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= InventoryItemModel.threshold
    ).all()
    return [schemas.InventoryItem.from_orm(item) for item in low_stock_items]


@router.get("/out-of-stock", response_model=List[schemas.InventoryItem])
async def get_out_of_stock_items(db: Session = Depends(get_db)):
    """Get items that are out of stock"""
    out_of_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= 0
    ).all()
    return [schemas.InventoryItem.from_orm(item) for item in out_of_stock_items]


@router.get("/{item_id}", response_model=schemas.InventoryItem)
async def get_inventory_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific inventory item by ID"""
    inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return schemas.InventoryItem.from_orm(inventory_item)


@router.post("/", response_model=schemas.InventoryItem)
async def create_inventory_item(inventory_item: schemas.InventoryItemCreate, db: Session = Depends(get_db)):
    """Create a new inventory item"""
    db_inventory_item = InventoryItemModel(
        name=inventory_item.name,
        category=inventory_item.category,
        current_stock=inventory_item.current_stock,
        unit=inventory_item.unit,
        threshold=inventory_item.minimum_stock,  # Map minimum_stock to threshold
        supplier=inventory_item.supplier,
        last_updated=datetime.utcnow()
    )
    db.add(db_inventory_item)
    db.commit()
    db.refresh(db_inventory_item)
    return schemas.InventoryItem.from_orm(db_inventory_item)


@router.put("/{item_id}", response_model=schemas.InventoryItem)
async def update_inventory_item(item_id: int, inventory_item: schemas.InventoryItemUpdate, db: Session = Depends(get_db)):
    """Update an existing inventory item"""
    db_inventory_item = db.query(InventoryItemModel).filter(InventoryItemModel.id == item_id).first()
    if not db_inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = inventory_item.dict(exclude_unset=True)
    
    # Map minimum_stock to threshold if present
    if 'minimum_stock' in update_data:
        update_data['threshold'] = update_data.pop('minimum_stock')
    
    for field, value in update_data.items():
        if hasattr(db_inventory_item, field):
            setattr(db_inventory_item, field, value)
    
    db_inventory_item.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_inventory_item)
    return schemas.InventoryItem.from_orm(db_inventory_item)


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


@router.get("/alcohol", response_model=List[schemas.InventoryItem])
async def get_alcohol_inventory(db: Session = Depends(get_db)):
    """Get all alcohol inventory items"""
    alcohol_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.is_alcohol == True
    ).all()
    return [schemas.InventoryItem.from_orm(item) for item in alcohol_items]


@router.get("/alcohol/by-type")
async def get_alcohol_by_type(db: Session = Depends(get_db)):
    """Get alcohol inventory grouped by type"""
    alcohol_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.is_alcohol == True
    ).all()
    
    grouped = {}
    for item in alcohol_items:
        alcohol_type = item.alcohol_type or 'Other'
        if alcohol_type not in grouped:
            grouped[alcohol_type] = []
        grouped[alcohol_type].append(schemas.InventoryItem.from_orm(item))
    
    return grouped


@router.post("/stock-movement")
async def create_stock_movement(
    inventory_item_id: int,
    movement_type: str,
    quantity: float,
    reason: str,
    performed_by: int,
    cost: Optional[float] = None,
    reference: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Record a stock movement (in/out/adjustment/waste)"""
    from models import StockMovement
    
    # Verify inventory item exists
    inventory_item = db.query(InventoryItemModel).filter(
        InventoryItemModel.id == inventory_item_id
    ).first()
    
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Create stock movement record
    movement = StockMovement(
        inventory_item_id=inventory_item_id,
        movement_type=movement_type,
        quantity=quantity,
        cost=cost,
        reason=reason,
        reference=reference,
        performed_by=performed_by
    )
    
    db.add(movement)
    
    # Update inventory stock
    if movement_type == 'in':
        inventory_item.current_stock += quantity
    elif movement_type in ['out', 'waste']:
        inventory_item.current_stock -= quantity
    elif movement_type == 'adjustment':
        inventory_item.current_stock = quantity
    
    inventory_item.last_updated = datetime.now()
    
    db.commit()
    db.refresh(movement)
    
    return {
        "message": "Stock movement recorded successfully",
        "movement_id": movement.id,
        "new_stock_level": inventory_item.current_stock
    }


@router.get("/movements/{inventory_item_id}")
async def get_stock_movements(inventory_item_id: int, db: Session = Depends(get_db)):
    """Get stock movement history for an item"""
    from models import StockMovement
    
    movements = db.query(StockMovement).filter(
        StockMovement.inventory_item_id == inventory_item_id
    ).order_by(StockMovement.created_at.desc()).all()
    
    return movements


@router.get("/analytics")
async def get_inventory_analytics(db: Session = Depends(get_db)):
    """Get inventory analytics and insights"""
    from sqlalchemy import func
    from models import StockMovement
    
    # Basic counts
    total_items = db.query(InventoryItemModel).count()
    low_stock_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.current_stock <= InventoryItemModel.threshold
    ).count()
    
    # Calculate total value (where cost_per_unit is available)
    total_value = db.query(
        func.sum(InventoryItemModel.current_stock * InventoryItemModel.cost_per_unit)
    ).filter(InventoryItemModel.cost_per_unit.isnot(None)).scalar() or 0
    
    # Category breakdown
    category_breakdown = db.query(
        InventoryItemModel.category,
        func.count(InventoryItemModel.id).label('item_count'),
        func.sum(InventoryItemModel.current_stock * InventoryItemModel.cost_per_unit).label('total_value')
    ).filter(
        InventoryItemModel.cost_per_unit.isnot(None)
    ).group_by(InventoryItemModel.category).all()
    
    # Alcohol-specific analytics
    alcohol_items = db.query(InventoryItemModel).filter(
        InventoryItemModel.is_alcohol == True
    ).all()
    
    alcohol_analytics = []
    for item in alcohol_items:
        alcohol_analytics.append({
            "name": item.name,
            "type": item.alcohol_type,
            "current_stock": item.current_stock,
            "unit": item.unit,
            "volume": item.alcohol_volume,
            "bottle_size": item.bottle_size,
            "par_level": item.par_level,
            "status": "low" if item.current_stock <= item.threshold else "ok"
        })
    
    # Most consumed items (based on out movements)
    top_consumed = db.query(
        InventoryItemModel.name,
        func.sum(StockMovement.quantity).label('total_consumed')
    ).join(StockMovement, InventoryItemModel.id == StockMovement.inventory_item_id)\
     .filter(StockMovement.movement_type == 'out')\
     .group_by(InventoryItemModel.id, InventoryItemModel.name)\
     .order_by(func.sum(StockMovement.quantity).desc())\
     .limit(10).all()
    
    return {
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "total_value": float(total_value),
        "category_breakdown": [
            {
                "category": cat.category,
                "item_count": cat.item_count,
                "total_value": float(cat.total_value or 0)
            } for cat in category_breakdown
        ],
        "alcohol_inventory": alcohol_analytics,
        "top_consumed_items": [
            {
                "name": item.name,
                "total_consumed": float(item.total_consumed)
            } for item in top_consumed
        ]
    }
