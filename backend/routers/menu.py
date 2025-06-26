# menu.py - Menu Management API router
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models import MenuItem as MenuItemModel
from database import get_db
import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.MenuItem])
async def get_menu_items(
    category: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all menu items with optional filtering"""
    query = db.query(MenuItemModel)
    
    if active_only:
        query = query.filter(MenuItemModel.is_active == True)
    
    if category:
        query = query.filter(MenuItemModel.category == category)
    
    menu_items = query.all()
    return menu_items


@router.get("/{item_id}", response_model=schemas.MenuItem)
async def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific menu item by ID"""
    menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return menu_item


@router.post("/", response_model=schemas.MenuItem)
async def create_menu_item(menu_item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    """Create a new menu item"""
    db_menu_item = MenuItemModel(
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price,
        category=menu_item.category,
        image_path=menu_item.image_path,
        tags=menu_item.tags,
        is_active=menu_item.is_active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@router.put("/{item_id}", response_model=schemas.MenuItem)
async def update_menu_item(item_id: int, menu_item: schemas.MenuItemUpdate, db: Session = Depends(get_db)):
    """Update an existing menu item"""
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    update_data = menu_item.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_menu_item, field, value)
    
    db_menu_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item


@router.delete("/{item_id}")
async def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a menu item"""
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    db.delete(db_menu_item)
    db.commit()
    return {"message": "Menu item deleted successfully"}


@router.get("/categories/list")
async def get_menu_categories(db: Session = Depends(get_db)):
    """Get all unique menu categories"""
    categories = db.query(MenuItemModel.category).distinct().all()
    return [category[0] for category in categories if category[0]]


@router.patch("/{item_id}/toggle-active")
async def toggle_menu_item_active(item_id: int, db: Session = Depends(get_db)):
    """Toggle menu item active status"""
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if not db_menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    db_menu_item.is_active = not db_menu_item.is_active
    db_menu_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item
