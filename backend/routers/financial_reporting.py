# routers/financial_reporting.py - Financial reporting and analysis
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func, desc, and_, or_, distinct
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
import calendar

from database import get_db
from models import (
    Sale, Order, OrderItem, MenuItem, DailyReport, 
    StaffMember, SalaryRecord, InventoryItem,
    StockMovement
)
from schemas import (
    FinancialOverview,
    ExpenseReport,
    ProfitLossReport,
    ProfitLossStatement,
    CashFlow,
    BalanceSheet,
    FinancialTransaction,
    FinancialTransactionCreate
)

router = APIRouter(prefix="/api/financial", tags=["financial"])

@router.get("/overview")
def get_financial_overview(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get a financial overview of the restaurant's operations
    for a specific time period.
    """
    if not start_date:
        start_date = date.today().replace(day=1)  # First day of current month
    if not end_date:
        end_date = date.today()  # Today
    
    # Total revenue for the period
    total_revenue = db.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).scalar() or 0
    
    # Cost of goods sold (from inventory movements)
    total_cogs = db.query(func.sum(StockMovement.cost)).filter(
        StockMovement.created_at >= datetime.combine(start_date, datetime.min.time()),
        StockMovement.created_at <= datetime.combine(end_date, datetime.max.time()),
        StockMovement.movement_type == 'usage'
    ).scalar() or 0
    
    # Labor costs (from salary records)
    labor_costs = db.query(func.sum(SalaryRecord.total_pay)).filter(
        SalaryRecord.period_start >= start_date,
        SalaryRecord.period_end <= end_date
    ).scalar() or 0
    
    # Gross profit
    gross_profit = total_revenue - total_cogs
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Operating profit (assumes other expenses are in daily reports)
    other_expenses = db.query(func.sum(DailyReport.other_expenses)).filter(
        DailyReport.report_date >= start_date,
        DailyReport.report_date <= end_date
    ).scalar() or 0
    
    operating_profit = gross_profit - labor_costs - other_expenses
    net_profit_margin = (operating_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Daily breakdown
    daily_finances = db.query(
        DailyReport.report_date,
        DailyReport.total_sales,
        DailyReport.total_inventory_cost,
        DailyReport.staff_cost,
        DailyReport.other_expenses,
        DailyReport.net_profit
    ).filter(
        DailyReport.report_date >= start_date,
        DailyReport.report_date <= end_date
    ).order_by(DailyReport.report_date).all()
    
    # Top 5 expense categories (placeholder - would need an expense categories model)
    expense_categories = [
        {"category": "Labor", "amount": labor_costs},
        {"category": "Inventory", "amount": total_cogs},
        {"category": "Utilities", "amount": other_expenses * 0.3},  # Placeholder assumption
        {"category": "Rent", "amount": other_expenses * 0.4},       # Placeholder assumption
        {"category": "Marketing", "amount": other_expenses * 0.2},  # Placeholder assumption
        {"category": "Other", "amount": other_expenses * 0.1}       # Placeholder assumption
    ]
    
    # Sort by amount descending
    expense_categories.sort(key=lambda x: x["amount"], reverse=True)
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "summary": {
            "total_revenue": total_revenue,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "gross_margin": gross_margin,
            "labor_costs": labor_costs,
            "other_expenses": other_expenses,
            "operating_profit": operating_profit,
            "net_profit_margin": net_profit_margin
        },
        "daily_breakdown": daily_finances,
        "expense_breakdown": expense_categories[:5]  # Top 5 expense categories
    }

@router.get("/profit-loss")
def get_profit_loss_statement(
    year: int = Query(...),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate a profit and loss statement for a specific month or year
    """
    # Determine start and end dates
    if month:
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)
        period_name = f"{calendar.month_name[month]} {year}"
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        period_name = f"Annual {year}"
    
    # Revenue calculations
    total_revenue = db.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).scalar() or 0
    
    # Revenue by category
    category_revenue = db.query(
        MenuItem.category,
        func.sum(OrderItem.quantity * MenuItem.price).label('revenue')
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .join(Sale, Order.id == Sale.order_id)\
     .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)\
     .group_by(MenuItem.category).all()
    
    # Cost of goods sold
    total_cogs = db.query(func.sum(StockMovement.cost)).filter(
        StockMovement.created_at >= datetime.combine(start_date, datetime.min.time()),
        StockMovement.created_at <= datetime.combine(end_date, datetime.max.time()),
        StockMovement.movement_type == 'usage'
    ).scalar() or 0
    
    # COGS by category (if inventory items have categories matching menu items)
    cogs_by_category = db.query(
        InventoryItem.category,
        func.sum(StockMovement.cost).label('cost')
    ).join(StockMovement, InventoryItem.id == StockMovement.inventory_item_id)\
     .filter(
        StockMovement.created_at >= datetime.combine(start_date, datetime.min.time()),
        StockMovement.created_at <= datetime.combine(end_date, datetime.max.time()),
        StockMovement.movement_type == 'usage'
     ).group_by(InventoryItem.category).all()
    
    # Labor costs
    labor_costs = db.query(func.sum(SalaryRecord.total_pay)).filter(
        SalaryRecord.period_start >= start_date,
        SalaryRecord.period_end <= end_date
    ).scalar() or 0
    
    # Other expenses (from daily reports)
    other_expenses = db.query(func.sum(DailyReport.other_expenses)).filter(
        DailyReport.report_date >= start_date,
        DailyReport.report_date <= end_date
    ).scalar() or 0
    
    # Calculate profits
    gross_profit = total_revenue - total_cogs
    operating_profit = gross_profit - labor_costs - other_expenses
    
    # Month-by-month breakdown for annual reports
    monthly_breakdown = []
    if not month:
        for m in range(1, 13):
            m_start = date(year, m, 1)
            m_end = date(year, m, calendar.monthrange(year, m)[1])
            
            m_revenue = db.query(func.sum(Sale.total_amount)).filter(
                Sale.sale_date >= m_start,
                Sale.sale_date <= m_end
            ).scalar() or 0
            
            m_cogs = db.query(func.sum(StockMovement.cost)).filter(
                StockMovement.created_at >= datetime.combine(m_start, datetime.min.time()),
                StockMovement.created_at <= datetime.combine(m_end, datetime.max.time()),
                StockMovement.movement_type == 'usage'
            ).scalar() or 0
            
            m_labor = db.query(func.sum(SalaryRecord.total_pay)).filter(
                SalaryRecord.period_start >= m_start,
                SalaryRecord.period_end <= m_end
            ).scalar() or 0
            
            m_expenses = db.query(func.sum(DailyReport.other_expenses)).filter(
                DailyReport.report_date >= m_start,
                DailyReport.report_date <= m_end
            ).scalar() or 0
            
            m_profit = m_revenue - m_cogs - m_labor - m_expenses
            
            monthly_breakdown.append({
                "month": calendar.month_name[m],
                "revenue": m_revenue,
                "cogs": m_cogs,
                "gross_profit": m_revenue - m_cogs,
                "labor_costs": m_labor,
                "other_expenses": m_expenses,
                "net_profit": m_profit
            })
    
    return {
        "statement": {
            "period": period_name,
            "start_date": start_date,
            "end_date": end_date
        },
        "revenue": {
            "total": total_revenue,
            "by_category": [{"category": cat, "amount": rev} for cat, rev in category_revenue]
        },
        "expenses": {
            "cogs": {
                "total": total_cogs,
                "by_category": [{"category": cat, "amount": cost} for cat, cost in cogs_by_category]
            },
            "labor": labor_costs,
            "other_expenses": other_expenses
        },
        "profits": {
            "gross_profit": gross_profit,
            "gross_margin_percentage": (gross_profit / total_revenue * 100) if total_revenue > 0 else 0,
            "operating_profit": operating_profit,
            "net_margin_percentage": (operating_profit / total_revenue * 100) if total_revenue > 0 else 0
        },
        "monthly_breakdown": monthly_breakdown
    }

@router.get("/expense-report")
def get_expense_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate an expense report for a specific time period
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Labor expenses
    labor_query = db.query(
        StaffMember.id,
        StaffMember.name.label('staff_name'),
        StaffMember.position,
        func.sum(SalaryRecord.total_pay).label('amount'),
        func.sum(SalaryRecord.regular_hours + SalaryRecord.overtime_hours).label('hours')
    ).join(SalaryRecord, StaffMember.id == SalaryRecord.staff_id)\
     .filter(
         SalaryRecord.period_start >= start_date,
         SalaryRecord.period_end <= end_date
     )
    
    if category and category.lower() == 'labor':
        labor_query = labor_query.group_by(StaffMember.id, StaffMember.name, StaffMember.position)
        labor_expenses = labor_query.all()
        
        labor_expense_details = []
        for expense in labor_expenses:
            labor_expense_details.append({
                "staff_id": expense.id,
                "staff_name": expense.staff_name,
                "position": expense.position,
                "amount": expense.amount,
                "hours": expense.hours
            })
        
        total_labor = sum(item["amount"] for item in labor_expense_details)
        
        return {
            "category": "Labor",
            "total_amount": total_labor,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "items": labor_expense_details
        }
    
    # Inventory expenses
    inventory_query = db.query(
        InventoryItem.id,
        InventoryItem.name.label('item_name'),
        InventoryItem.category,
        func.sum(StockMovement.quantity).label('quantity'),
        func.sum(StockMovement.cost).label('amount')
    ).join(StockMovement, InventoryItem.id == StockMovement.inventory_item_id)\
     .filter(
         StockMovement.created_at >= datetime.combine(start_date, datetime.min.time()),
         StockMovement.created_at <= datetime.combine(end_date, datetime.max.time()),
         StockMovement.movement_type == 'purchase'
     )
    
    if category and category.lower() == 'inventory':
        inventory_query = inventory_query.group_by(
            InventoryItem.id, InventoryItem.name, InventoryItem.category
        )
        inventory_expenses = inventory_query.all()
        
        inventory_expense_details = []
        for expense in inventory_expenses:
            inventory_expense_details.append({
                "item_id": expense.id,
                "item_name": expense.item_name,
                "category": expense.category,
                "quantity": expense.quantity,
                "amount": expense.amount
            })
        
        total_inventory = sum(item["amount"] for item in inventory_expense_details)
        
        return {
            "category": "Inventory",
            "total_amount": total_inventory,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "items": inventory_expense_details
        }
    
    # Summary of all expenses if no specific category
    labor_total = db.query(func.sum(SalaryRecord.total_pay)).filter(
        SalaryRecord.period_start >= start_date,
        SalaryRecord.period_end <= end_date
    ).scalar() or 0
    
    inventory_total = db.query(func.sum(StockMovement.cost)).filter(
        StockMovement.created_at >= datetime.combine(start_date, datetime.min.time()),
        StockMovement.created_at <= datetime.combine(end_date, datetime.max.time()),
        StockMovement.movement_type == 'purchase'
    ).scalar() or 0
    
    other_expenses = db.query(func.sum(DailyReport.other_expenses)).filter(
        DailyReport.report_date >= start_date,
        DailyReport.report_date <= end_date
    ).scalar() or 0
    
    # For this example, we'll break down other expenses into categories
    # In a real system, you'd have an actual expenses table with categories
    utilities = other_expenses * 0.3
    rent = other_expenses * 0.4
    marketing = other_expenses * 0.2
    miscellaneous = other_expenses * 0.1
    
    expense_categories = [
        {"category": "Labor", "amount": labor_total, "percentage": 0},
        {"category": "Inventory", "amount": inventory_total, "percentage": 0},
        {"category": "Utilities", "amount": utilities, "percentage": 0},
        {"category": "Rent", "amount": rent, "percentage": 0},
        {"category": "Marketing", "amount": marketing, "percentage": 0},
        {"category": "Miscellaneous", "amount": miscellaneous, "percentage": 0}
    ]
    
    total_expenses = sum(item["amount"] for item in expense_categories)
    
    # Calculate percentages
    if total_expenses > 0:
        for item in expense_categories:
            item["percentage"] = (item["amount"] / total_expenses) * 100
    
    return {
        "total_expenses": total_expenses,
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "categories": expense_categories
    }

@router.get("/cash-flow")
def get_cash_flow(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate a cash flow report for a specific time period
    """
    if not start_date:
        start_date = date.today().replace(day=1)  # First day of current month
    if not end_date:
        end_date = date.today()  # Today
    
    # Get daily cash inflows (sales)
    daily_inflows = db.query(
        Sale.sale_date,
        func.sum(Sale.total_amount).label('inflow'),
        Sale.payment_method
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).group_by(Sale.sale_date, Sale.payment_method).all()
    
    # Process into the format we want
    cash_flow_data = {}
    for entry in daily_inflows:
        date_str = str(entry.sale_date)
        if date_str not in cash_flow_data:
            cash_flow_data[date_str] = {
                "date": entry.sale_date,
                "inflows": [],
                "outflows": [],
                "net_cash_flow": 0
            }
        
        cash_flow_data[date_str]["inflows"].append({
            "type": "Sales",
            "method": entry.payment_method,
            "amount": entry.inflow
        })
    
    # Get daily cash outflows (expenses - simplified version)
    for current_date in cash_flow_data:
        # For this example, we're using the daily reports to estimate outflows
        date_obj = datetime.strptime(current_date, "%Y-%m-%d").date()
        
        daily_report = db.query(DailyReport).filter(
            DailyReport.report_date == date_obj
        ).first()
        
        if daily_report:
            # Add inventory costs
            if daily_report.total_inventory_cost:
                cash_flow_data[current_date]["outflows"].append({
                    "type": "Inventory",
                    "description": "Daily inventory costs",
                    "amount": daily_report.total_inventory_cost
                })
            
            # Add staff costs
            if daily_report.staff_cost:
                cash_flow_data[current_date]["outflows"].append({
                    "type": "Labor",
                    "description": "Staff wages and salaries",
                    "amount": daily_report.staff_cost
                })
            
            # Add other expenses
            if daily_report.other_expenses:
                cash_flow_data[current_date]["outflows"].append({
                    "type": "Other",
                    "description": "Other operating expenses",
                    "amount": daily_report.other_expenses
                })
        
        # Calculate net cash flow for the day
        total_inflows = sum(item["amount"] for item in cash_flow_data[current_date]["inflows"])
        total_outflows = sum(item["amount"] for item in cash_flow_data[current_date]["outflows"])
        cash_flow_data[current_date]["net_cash_flow"] = total_inflows - total_outflows
    
    # Convert to list and sort by date
    cash_flow_list = list(cash_flow_data.values())
    cash_flow_list.sort(key=lambda x: x["date"])
    
    # Calculate summary statistics
    total_inflows = sum(
        sum(item["amount"] for item in day["inflows"])
        for day in cash_flow_list
    )
    
    total_outflows = sum(
        sum(item["amount"] for item in day["outflows"])
        for day in cash_flow_list
    )
    
    net_cash_flow = total_inflows - total_outflows
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_inflows": total_inflows,
            "total_outflows": total_outflows,
            "net_cash_flow": net_cash_flow
        },
        "daily_cash_flow": cash_flow_list
    }

@router.get("/tax-report")
def get_tax_report(
    year: int = Query(...),
    quarter: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Generate a tax report for sales tax, VAT, or other tax requirements
    """
    # Define the time period based on year and optional quarter
    if quarter:
        if quarter < 1 or quarter > 4:
            raise HTTPException(status_code=400, detail="Quarter must be between 1 and 4")
        
        start_month = (quarter - 1) * 3 + 1
        start_date = date(year, start_month, 1)
        
        if quarter < 4:
            end_month = quarter * 3
            end_date = date(year, end_month + 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, 12, 31)
        
        period_name = f"Q{quarter} {year}"
    else:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        period_name = f"Annual {year}"
    
    # Get total sales amount
    total_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).scalar() or 0
    
    # Get total tax amount (assuming it's stored in the Sale model)
    total_tax = db.query(func.sum(Sale.tax_amount)).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).scalar() or 0
    
    # Calculate net sales
    net_sales = total_sales - total_tax
    
    # Get breakdown by payment method
    payment_breakdown = db.query(
        Sale.payment_method,
        func.sum(Sale.total_amount).label('total_amount'),
        func.sum(Sale.tax_amount).label('tax_amount'),
        func.count(Sale.id).label('transaction_count')
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).group_by(Sale.payment_method).all()
    
    payment_methods = []
    for item in payment_breakdown:
        payment_methods.append({
            "method": item.payment_method,
            "total_amount": item.total_amount,
            "tax_amount": item.tax_amount,
            "net_amount": item.total_amount - item.tax_amount,
            "transaction_count": item.transaction_count
        })
    
    # Monthly breakdown for quarterly or annual reports
    monthly_breakdown = []
    
    # Determine months to include
    start_month = start_date.month
    end_month = end_date.month
    
    for month in range(start_month, end_month + 1):
        month_start = date(year, month, 1)
        month_end = date(year, month, calendar.monthrange(year, month)[1])
        
        month_sales = db.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).scalar() or 0
        
        month_tax = db.query(func.sum(Sale.tax_amount)).filter(
            Sale.sale_date >= month_start,
            Sale.sale_date <= month_end
        ).scalar() or 0
        
        monthly_breakdown.append({
            "month": calendar.month_name[month],
            "total_sales": month_sales,
            "tax_amount": month_tax,
            "net_sales": month_sales - month_tax
        })
    
    return {
        "period": {
            "name": period_name,
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_sales": total_sales,
            "tax_amount": total_tax,
            "net_sales": net_sales,
            "tax_rate": (total_tax / net_sales * 100) if net_sales > 0 else 0
        },
        "payment_methods": payment_methods,
        "monthly_breakdown": monthly_breakdown
    }
