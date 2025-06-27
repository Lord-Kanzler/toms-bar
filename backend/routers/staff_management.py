# routers/staff_management.py - Enhanced staff management with salary tracking
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from typing import List, Optional
from datetime import date, datetime, timedelta
import calendar

from database import get_db
from models import StaffMember, Timesheet, SalaryRecord, WorkSchedule
from schemas import (
    StaffMember as StaffMemberSchema,
    StaffMemberCreate, StaffMemberUpdate,
    Timesheet as TimesheetSchema,
    TimesheetCreate, TimesheetUpdate,
    SalaryRecord as SalaryRecordSchema,
    SalaryRecordCreate,
    WorkSchedule as WorkScheduleSchema,
    WorkScheduleCreate,
    StaffAnalytics
)

router = APIRouter(prefix="/api/staff-management", tags=["staff-management"])

# Timesheet Management
@router.post("/timesheets/", response_model=TimesheetSchema)
def create_timesheet(timesheet: TimesheetCreate, db: Session = Depends(get_db)):
    db_timesheet = Timesheet(**timesheet.dict())
    db.add(db_timesheet)
    db.commit()
    db.refresh(db_timesheet)
    return db_timesheet

@router.get("/timesheets/", response_model=List[TimesheetSchema])
def get_timesheets(
    staff_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Timesheet)
    
    if staff_id:
        query = query.filter(Timesheet.staff_member_id == staff_id)
    if start_date:
        query = query.filter(Timesheet.date >= start_date)
    if end_date:
        query = query.filter(Timesheet.date <= end_date)
    
    return query.all()

@router.put("/timesheets/{timesheet_id}", response_model=TimesheetSchema)
def update_timesheet(timesheet_id: int, timesheet: TimesheetUpdate, db: Session = Depends(get_db)):
    db_timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not db_timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    for field, value in timesheet.dict(exclude_unset=True).items():
        setattr(db_timesheet, field, value)
    
    # Calculate total hours and overtime
    if db_timesheet.clock_in and db_timesheet.clock_out:
        total_time = db_timesheet.clock_out - db_timesheet.clock_in
        break_time = timedelta(0)
        
        if db_timesheet.break_start and db_timesheet.break_end:
            break_time = db_timesheet.break_end - db_timesheet.break_start
        
        worked_time = total_time - break_time
        db_timesheet.total_hours = worked_time.total_seconds() / 3600
        
        # Calculate overtime (anything over 8 hours)
        if db_timesheet.total_hours > 8:
            db_timesheet.overtime_hours = db_timesheet.total_hours - 8
        else:
            db_timesheet.overtime_hours = 0
    
    db.commit()
    db.refresh(db_timesheet)
    return db_timesheet

@router.post("/timesheets/{timesheet_id}/clock-in")
def clock_in(timesheet_id: int, db: Session = Depends(get_db)):
    db_timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not db_timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    db_timesheet.clock_in = datetime.now()
    db.commit()
    return {"message": "Clocked in successfully", "time": db_timesheet.clock_in}

@router.post("/timesheets/{timesheet_id}/clock-out")
def clock_out(timesheet_id: int, db: Session = Depends(get_db)):
    db_timesheet = db.query(Timesheet).filter(Timesheet.id == timesheet_id).first()
    if not db_timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")
    
    db_timesheet.clock_out = datetime.now()
    
    # Calculate hours
    if db_timesheet.clock_in:
        total_time = db_timesheet.clock_out - db_timesheet.clock_in
        break_time = timedelta(0)
        
        if db_timesheet.break_start and db_timesheet.break_end:
            break_time = db_timesheet.break_end - db_timesheet.break_start
        
        worked_time = total_time - break_time
        db_timesheet.total_hours = worked_time.total_seconds() / 3600
        
        if db_timesheet.total_hours > 8:
            db_timesheet.overtime_hours = db_timesheet.total_hours - 8
        else:
            db_timesheet.overtime_hours = 0
    
    db.commit()
    return {"message": "Clocked out successfully", "time": db_timesheet.clock_out, "total_hours": db_timesheet.total_hours}

# Salary Management
@router.get("/salary/{staff_id}", response_model=List[SalaryRecordSchema])
def get_staff_salary_records(staff_id: int, db: Session = Depends(get_db)):
    return db.query(SalaryRecord).filter(SalaryRecord.staff_member_id == staff_id).all()

@router.post("/salary/calculate/{staff_id}")
def calculate_monthly_salary(staff_id: int, month: int, year: int, db: Session = Depends(get_db)):
    # Get staff member
    staff = db.query(StaffMember).filter(StaffMember.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Get timesheets for the month
    timesheets = db.query(Timesheet).filter(
        Timesheet.staff_member_id == staff_id,
        extract('month', Timesheet.date) == month,
        extract('year', Timesheet.date) == year,
        Timesheet.approved == True
    ).all()
    
    # Calculate totals
    total_regular_hours = sum(ts.total_hours - (ts.overtime_hours or 0) for ts in timesheets if ts.total_hours)
    total_overtime_hours = sum(ts.overtime_hours or 0 for ts in timesheets)
    
    regular_pay = total_regular_hours * float(staff.hourly_rate or 0)
    overtime_pay = total_overtime_hours * float(staff.hourly_rate or 0) * 1.5  # 1.5x for overtime
    
    total_salary = regular_pay + overtime_pay
    
    # Check if record already exists
    existing_record = db.query(SalaryRecord).filter(
        SalaryRecord.staff_member_id == staff_id,
        SalaryRecord.month == month,
        SalaryRecord.year == year
    ).first()
    
    if existing_record:
        # Update existing record
        existing_record.regular_hours = total_regular_hours
        existing_record.overtime_hours = total_overtime_hours
        existing_record.regular_pay = regular_pay
        existing_record.overtime_pay = overtime_pay
        existing_record.total_salary = total_salary
        db.commit()
        return existing_record
    else:
        # Create new record
        salary_record = SalaryRecord(
            staff_member_id=staff_id,
            month=month,
            year=year,
            regular_hours=total_regular_hours,
            overtime_hours=total_overtime_hours,
            regular_pay=regular_pay,
            overtime_pay=overtime_pay,
            total_salary=total_salary
        )
        db.add(salary_record)
        db.commit()
        db.refresh(salary_record)
        return salary_record

@router.get("/salary/monthly-report")
def get_monthly_salary_report(month: int, year: int, db: Session = Depends(get_db)):
    salary_records = db.query(SalaryRecord).filter(
        SalaryRecord.month == month,
        SalaryRecord.year == year
    ).all()
    
    total_payroll = sum(float(record.total_salary) for record in salary_records)
    
    return {
        "month": month,
        "year": year,
        "month_name": calendar.month_name[month],
        "total_staff": len(salary_records),
        "total_payroll": total_payroll,
        "records": salary_records
    }

# Work Schedule Management
@router.post("/schedules/", response_model=WorkScheduleSchema)
def create_work_schedule(schedule: WorkScheduleCreate, db: Session = Depends(get_db)):
    db_schedule = WorkSchedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.get("/schedules/", response_model=List[WorkScheduleSchema])
def get_work_schedules(
    staff_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(WorkSchedule)
    
    if staff_id:
        query = query.filter(WorkSchedule.staff_member_id == staff_id)
    if start_date:
        query = query.filter(WorkSchedule.date >= start_date)
    if end_date:
        query = query.filter(WorkSchedule.date <= end_date)
    
    return query.all()

# Staff Analytics
@router.get("/analytics", response_model=StaffAnalytics)
def get_staff_analytics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Basic staff counts
    total_staff = db.query(StaffMember).count()
    active_staff = db.query(StaffMember).filter(StaffMember.is_active == True).count()
    
    # Hours and payroll
    timesheets = db.query(Timesheet).filter(
        Timesheet.date >= start_date,
        Timesheet.date <= end_date,
        Timesheet.approved == True
    ).all()
    
    total_hours = sum(ts.total_hours or 0 for ts in timesheets)
    overtime_hours = sum(ts.overtime_hours or 0 for ts in timesheets)
    
    # Get salary records for the period
    salary_records = db.query(SalaryRecord).filter(
        SalaryRecord.year >= start_date.year,
        SalaryRecord.month >= start_date.month if SalaryRecord.year == start_date.year else True
    ).all()
    
    total_payroll = sum(float(record.total_salary) for record in salary_records)
    
    # Staff performance (hours worked by staff member)
    staff_performance = []
    for staff in db.query(StaffMember).filter(StaffMember.is_active == True).all():
        staff_timesheets = [ts for ts in timesheets if ts.staff_member_id == staff.id]
        staff_hours = sum(ts.total_hours or 0 for ts in staff_timesheets)
        staff_performance.append({
            "staff_id": staff.id,
            "name": f"{staff.first_name} {staff.last_name}",
            "position": staff.position,
            "hours_worked": staff_hours,
            "shifts": len(staff_timesheets)
        })
    
    return StaffAnalytics(
        total_staff=total_staff,
        active_staff=active_staff,
        total_hours_worked=total_hours,
        total_payroll=total_payroll,
        overtime_hours=overtime_hours,
        staff_performance=staff_performance
    )
