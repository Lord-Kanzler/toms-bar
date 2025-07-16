# staff.py - Staff Management API router
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from models import StaffMember as StaffMemberModel
from database import get_db
from schemas import StaffMember as StaffMemberSchema, StaffMemberCreate, StaffMemberUpdate

router = APIRouter()


@router.get("/", response_model=List[StaffMemberSchema])
async def get_staff_members(
    position: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all staff members with optional filtering"""
    query = db.query(StaffMemberModel)
    
    if position:
        query = query.filter(StaffMemberModel.position == position)
    
    if active_only:
        query = query.filter(StaffMemberModel.is_active == True)
    
    staff_members = query.all()
    return [StaffMemberSchema.from_orm(member) for member in staff_members]


@router.get("/{staff_id}", response_model=StaffMemberSchema)
async def get_staff_member(staff_id: int, db: Session = Depends(get_db)):
    """Get a specific staff member by ID"""
    staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    
    if not staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    return StaffMemberSchema.from_orm(staff_member)


@router.post("/", response_model=StaffMemberSchema)
async def create_staff_member(staff_member: StaffMemberCreate, db: Session = Depends(get_db)):
    """Create a new staff member"""
    # Combine first_name and last_name for the database
    full_name = f"{staff_member.first_name} {staff_member.last_name}".strip()
    
    db_staff_member = StaffMemberModel(
        name=full_name,
        position=staff_member.position,
        email=staff_member.email,
        phone=staff_member.phone,
        hire_date=datetime.utcnow(),
        is_active=staff_member.is_active
    )
    
    db.add(db_staff_member)
    db.commit()
    db.refresh(db_staff_member)
    return StaffMemberSchema.from_orm(db_staff_member)


@router.put("/{staff_id}", response_model=StaffMemberSchema)
async def update_staff_member(staff_id: int, staff_member: StaffMemberUpdate, db: Session = Depends(get_db)):
    """Update an existing staff member"""
    db_staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    
    if not db_staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Process special fields
    if staff_member.first_name is not None or staff_member.last_name is not None:
        # Get current name parts
        current_name_parts = db_staff_member.name.split(' ', 1) if db_staff_member.name else ['', '']
        current_first = current_name_parts[0] if len(current_name_parts) > 0 else ''
        current_last = current_name_parts[1] if len(current_name_parts) > 1 else ''
        
        # Update with new values if provided
        new_first = staff_member.first_name if staff_member.first_name is not None else current_first
        new_last = staff_member.last_name if staff_member.last_name is not None else current_last
        
        # Set the full name
        db_staff_member.name = f"{new_first} {new_last}".strip()
    
    # Update other fields if provided
    if staff_member.position is not None:
        db_staff_member.position = staff_member.position
    
    if staff_member.email is not None:
        db_staff_member.email = staff_member.email
    
    if staff_member.phone is not None:
        db_staff_member.phone = staff_member.phone
    
    if staff_member.is_active is not None:
        db_staff_member.is_active = staff_member.is_active
    
    db.commit()
    db.refresh(db_staff_member)
    return StaffMemberSchema.from_orm(db_staff_member)


@router.delete("/{staff_id}")
async def delete_staff_member(staff_id: int, db: Session = Depends(get_db)):
    """Delete a staff member (soft delete by setting is_active to False)"""
    db_staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    
    if not db_staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Soft delete
    db_staff_member.is_active = False
    db.commit()
    
    return {"message": "Staff member successfully deactivated"}


@router.patch("/{staff_id}/restore")
async def restore_staff_member(staff_id: int, db: Session = Depends(get_db)):
    """Restore a previously deactivated staff member"""
    db_staff_member = db.query(StaffMemberModel).filter(StaffMemberModel.id == staff_id).first()
    
    if not db_staff_member:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    db_staff_member.is_active = True
    db.commit()
    db.refresh(db_staff_member)
    return StaffMemberSchema.from_orm(db_staff_member)


@router.get("/positions/list")
async def get_staff_positions(db: Session = Depends(get_db)):
    """Get all unique staff positions"""
    positions = db.query(StaffMemberModel.position).distinct().all()
    return [position[0] for position in positions if position[0]]
