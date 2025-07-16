# routers/sales_analytics.py - Sales analytics and reporting
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, func, desc
from typing import List, Optional
from datetime import date, datetime, timedelta

from database import get_db
from models import Sale, Order, OrderItem, MenuItem, DailyReport, StaffMember
from schemas import (
    Sale as SaleSchema,
    SaleCreate,
    DailyReport as DailyReportSchema,
    DailyReportCreate,
    SalesAnalytics
)

router = APIRouter(prefix="/api/sales-analytics", tags=["sales-analytics"])

@router.post("/sales/", response_model=SaleSchema)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    db_sale = Sale(**sale.dict())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/sales/", response_model=List[SaleSchema])
def get_sales(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    payment_method: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Sale)
    
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if payment_method:
        query = query.filter(Sale.payment_method == payment_method)
    
    return query.order_by(desc(Sale.created_at)).all()

@router.get("/analytics/overview")
def get_sales_overview(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Basic sales metrics
    sales_query = db.query(Sale).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    )
    
    total_revenue = sales_query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
    total_orders = sales_query.count()
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Payment method breakdown
    payment_breakdown = db.query(
        Sale.payment_method,
        func.sum(Sale.total_amount).label('total'),
        func.count(Sale.id).label('count')
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).group_by(Sale.payment_method).all()
    
    # Daily sales for chart
    daily_sales = db.query(
        Sale.sale_date,
        func.sum(Sale.total_amount).label('total'),
        func.count(Sale.id).label('orders')
    ).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).group_by(Sale.sale_date).order_by(Sale.sale_date).all()
    
    # Top selling items (need to join with orders and menu items)
    top_items = db.query(
        MenuItem.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.quantity * MenuItem.price).label('revenue')
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .join(Sale, Order.id == Sale.order_id)\
     .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)\
     .group_by(MenuItem.id, MenuItem.name)\
     .order_by(desc('total_sold'))\
     .limit(10).all()
    
    # Revenue by category
    category_revenue = db.query(
        MenuItem.category,
        func.sum(OrderItem.quantity * MenuItem.price).label('revenue')
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .join(Sale, Order.id == Sale.order_id)\
     .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)\
     .group_by(MenuItem.category)\
     .order_by(desc('revenue')).all()
    
    return SalesAnalytics(
        total_revenue=float(total_revenue),
        total_orders=total_orders,
        average_order_value=float(average_order_value),
        top_selling_items=[
            {
                "name": item.name,
                "quantity_sold": int(item.total_sold),
                "revenue": float(item.revenue)
            } for item in top_items
        ],
        revenue_by_category=[
            {
                "category": cat.category,
                "revenue": float(cat.revenue)
            } for cat in category_revenue
        ],
        daily_sales=[
            {
                "date": day.sale_date.isoformat(),
                "revenue": float(day.total),
                "orders": int(day.orders)
            } for day in daily_sales
        ],
        payment_method_breakdown=[
            {
                "method": method.payment_method,
                "amount": float(method.total),
                "count": int(method.count)
            } for method in payment_breakdown
        ]
    )

@router.post("/daily-reports/generate")
def generate_daily_report(report_date: date, db: Session = Depends(get_db)):
    # Check if report already exists
    existing_report = db.query(DailyReport).filter(DailyReport.report_date == report_date).first()
    
    # Calculate metrics for the day
    sales_query = db.query(Sale).filter(Sale.sale_date == report_date)
    
    total_sales = sales_query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
    total_orders = sales_query.count()
    average_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    # Payment method breakdown
    cash_sales = sales_query.filter(Sale.payment_method == 'cash').with_entities(func.sum(Sale.total_amount)).scalar() or 0
    card_sales = sales_query.filter(Sale.payment_method == 'card').with_entities(func.sum(Sale.total_amount)).scalar() or 0
    
    # Count unique customers (assuming customer_name in orders)
    total_customers = db.query(Order).join(Sale, Order.id == Sale.order_id)\
                       .filter(Sale.sale_date == report_date)\
                       .with_entities(func.count(func.distinct(Order.customer_name))).scalar() or 0
    
    report_data = {
        "report_date": report_date,
        "total_sales": float(total_sales),
        "total_orders": total_orders,
        "average_order_value": float(average_order_value),
        "cash_sales": float(cash_sales),
        "card_sales": float(card_sales),
        "total_customers": total_customers,
        "staff_cost": 0,  # Will be calculated from timesheet data
        "inventory_cost": 0,  # Will be calculated from stock movements
        "net_profit": float(total_sales)  # Simplified calculation
    }
    
    if existing_report:
        for key, value in report_data.items():
            setattr(existing_report, key, value)
        db.commit()
        return existing_report
    else:
        daily_report = DailyReport(**report_data)
        db.add(daily_report)
        db.commit()
        db.refresh(daily_report)
        return daily_report

@router.get("/daily-reports/", response_model=List[DailyReportSchema])
def get_daily_reports(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DailyReport)
    
    if start_date:
        query = query.filter(DailyReport.report_date >= start_date)
    if end_date:
        query = query.filter(DailyReport.report_date <= end_date)
    
    return query.order_by(desc(DailyReport.report_date)).all()

@router.get("/reports/monthly")
def get_monthly_report(month: int, year: int, db: Session = Depends(get_db)):
    # Get all daily reports for the month
    daily_reports = db.query(DailyReport).filter(
        extract('month', DailyReport.report_date) == month,
        extract('year', DailyReport.report_date) == year
    ).all()
    
    if not daily_reports:
        raise HTTPException(status_code=404, detail="No reports found for this month")
    
    # Aggregate monthly data
    total_sales = sum(float(report.total_sales) for report in daily_reports)
    total_orders = sum(report.total_orders for report in daily_reports)
    total_customers = sum(report.total_customers or 0 for report in daily_reports)
    total_staff_cost = sum(float(report.staff_cost or 0) for report in daily_reports)
    total_inventory_cost = sum(float(report.inventory_cost or 0) for report in daily_reports)
    net_profit = sum(float(report.net_profit) for report in daily_reports)
    
    average_daily_sales = total_sales / len(daily_reports)
    average_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    return {
        "month": month,
        "year": year,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "average_daily_sales": average_daily_sales,
        "average_order_value": average_order_value,
        "total_staff_cost": total_staff_cost,
        "total_inventory_cost": total_inventory_cost,
        "net_profit": net_profit,
        "daily_breakdown": [
            {
                "date": report.report_date.isoformat(),
                "sales": float(report.total_sales),
                "orders": report.total_orders,
                "customers": report.total_customers
            } for report in daily_reports
        ]
    }

@router.get("/export/excel")
def export_sales_to_excel(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Export sales data to Excel format (returns data for frontend to handle)"""
    sales = db.query(Sale).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).all()
    
    # Format data for Excel export
    excel_data = []
    for sale in sales:
        excel_data.append({
            "Date": sale.sale_date.isoformat(),
            "Order ID": sale.order_id,
            "Total Amount": float(sale.total_amount),
            "Payment Method": sale.payment_method,
            "Tax Amount": float(sale.tax_amount),
            "Discount": float(sale.discount_amount),
            "Served By": sale.served_by
        })
    
    return {
        "filename": f"sales_report_{start_date}_{end_date}.xlsx",
        "data": excel_data,
        "summary": {
            "total_records": len(excel_data),
            "date_range": f"{start_date} to {end_date}",
            "total_revenue": sum(float(sale.total_amount) for sale in sales)
        }
    }

@router.get("/analytics/hourly-sales")
def get_hourly_sales(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get hourly sales data to identify peak hours"""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Query to extract hour of day and sum sales by hour
    hourly_sales = db.query(
        extract('hour', Order.created_at).label('hour'),
        func.sum(Sale.total_amount).label('total_sales'),
        func.count(Sale.id).label('order_count')
    ).join(Sale, Order.id == Sale.order_id)\
     .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)\
     .group_by('hour')\
     .order_by('hour')\
     .all()
    
    # Format the results
    result = [
        {
            "hour": int(hour),
            "hour_display": f"{int(hour)}:00 - {int(hour) + 1}:00",
            "total_sales": float(total_sales),
            "order_count": int(order_count)
        }
        for hour, total_sales, order_count in hourly_sales
    ]
    
    return result

@router.get("/analytics/staff-performance")
def get_staff_performance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get sales performance by staff member"""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Join with StaffMember to get staff name
    staff_performance = db.query(
        StaffMember.id,
        StaffMember.name.label('staff_name'),
        func.sum(Sale.total_amount).label('total_sales'),
        func.count(Sale.id).label('order_count')
    ).join(Sale, StaffMember.id == Sale.served_by)\
     .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)\
     .group_by(StaffMember.id, StaffMember.name)\
     .order_by(desc('total_sales'))\
     .all()
    
    # Format the results
    result = [
        {
            "staff_id": staff_id,
            "staff_name": staff_name,
            "total_sales": float(total_sales),
            "order_count": int(order_count),
            "average_order_value": float(total_sales) / int(order_count) if order_count else 0
        }
        for staff_id, staff_name, total_sales, order_count in staff_performance
    ]
    
    return result

@router.get("/analytics/product-category-performance")
def get_category_performance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get sales performance by product category"""
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Analyze sales by product category with quantity and revenue
    category_performance = db.query(
        MenuItem.category,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.quantity * MenuItem.price).label('total_revenue')
    ).join(OrderItem, MenuItem.id == OrderItem.menu_item_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .join(Sale, Order.id == Sale.order_id)\
     .filter(Sale.sale_date >= start_date, Sale.sale_date <= end_date)\
     .group_by(MenuItem.category)\
     .order_by(desc('total_revenue'))\
     .all()
    
    # Format the results
    result = [
        {
            "category": category,
            "total_quantity": int(total_quantity),
            "total_revenue": float(total_revenue),
            "average_price_per_item": float(total_revenue) / int(total_quantity) if total_quantity else 0
        }
        for category, total_quantity, total_revenue in category_performance
    ]
    
    return result
