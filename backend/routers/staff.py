# staff.py - Staff Management API router
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models import StaffMember as StaffMemberModel
from database import get_db
import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.StaffMember])
async def get_staff_members(
    position: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all staff members with optional filtering"""
    query = db.query(StaffMemberModel)
    
    if active_only:
        query = query.filter(StaffMemberModel.is_active == True)
    
    if position:
        query = query.filter(StaffMemberModel.position == position)
    
    staff_members = query.all()
    return [schemas.StaffMember.from_orm(member) for member in staff_members]


@router.get("/{staff_id}", response_model=schemas.StaffMember)
async def get_staff_member(staff_id: int, db: Session = Depends(get_db)):
    """Get a specific staff member by ID"""
    staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    if not staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return staff_member


@router.post("/", response_model=schemas.StaffMember)
async def create_staff_member(staff_member: schemas.StaffMemberCreate, db: Session = Depends(get_db)):
    """Create a new staff member"""
    # Check if email already exists
    existing_staff = db.query(StaffMemberModel).filter(StaffMemberModel.email == staff_member.email).first()
    if existing_staff:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Combine first_name and last_name into name for database storage
    full_name = f"{staff_member.first_name} {staff_member.last_name}"
    
    db_staff_member = StaffMemberModel(
        name=full_name,
        position=staff_member.position,
        email=staff_member.email,
        phone=staff_member.phone,
        hire_date=datetime.now(),
        is_active=staff_member.is_active
    )
    
    db.add(db_staff_member)
    db.commit()
    db.refresh(db_staff_member)
    
    return schemas.StaffMember.from_orm(db_staff_member)


@router.put("/{staff_id}", response_model=schemas.StaffMember)
async def update_staff_member(staff_id: int, staff_member: schemas.StaffMemberUpdate, db: Session = Depends(get_db)):
    """Update an existing staff member"""
    db_staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    if not db_staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check if email is being updated and already exists
    if staff_member.email and staff_member.email != db_staff_member.email:
        existing_staff = db.query(StaffMemberModel).filter(StaffMemberModel.email == staff_member.email).first()
        if existing_staff:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    update_data = staff_member.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_staff_member, field, value)
    
    db.commit()
    db.refresh(db_staff_member)
    return schemas.StaffMember.from_orm(db_staff_member)


@router.delete("/{staff_id}")
async def delete_staff_member(staff_id: int, db: Session = Depends(get_db)):
    """Delete a staff member"""
    db_staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    if not db_staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    db.delete(db_staff_member)
    db.commit()
    return {"message": "Staff member deleted successfully"}


@router.patch("/{staff_id}/toggle-active")
async def toggle_staff_member_active(staff_id: int, db: Session = Depends(get_db)):
    """Toggle staff member active status"""
    db_staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    if not db_staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    db_staff_member.is_active = not db_staff_member.is_active
    db.commit()
    db.refresh(db_staff_member)
    return schemas.StaffMember.from_orm(db_staff_member)


@router.get("/positions/list")
async def get_staff_positions(db: Session = Depends(get_db)):
    """Get all unique staff positions"""
    positions = db.query(StaffMemberModel.position).distinct().all()
    return [position[0] for position in positions if position[0]]


@router.get("/summary/stats")
async def get_staff_summary(db: Session = Depends(get_db)):
    """Get staff summary statistics"""
    total_staff = db.query(StaffMemberModel).filter(StaffMemberModel.is_active == True).count()
    
    # Count by position
    positions_count = {}
    positions = db.query(StaffMemberModel.position).filter(StaffMemberModel.is_active == True).distinct().all()
    for position in positions:
        count = db.query(StaffMemberModel).filter(
            StaffMemberModel.position == position[0],
            StaffMemberModel.is_active == True
        ).count()
        positions_count[position[0]] = count
    
    return {
        "total_staff": total_staff,
        "positions_count": positions_count
    }
