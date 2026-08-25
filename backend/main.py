"""
main.py — NovaCart Account Dashboard API

Built with FastAPI. Auto-generated docs at: http://localhost:8000/docs

Endpoints:
  GET /health                                  — service health check
  GET /authorize                               — SPCS OAuth flow
  GET /franchise/{id}/summary                  — overview stats
  GET /franchise/{id}/orders                   — monthly order volume and revenue
  GET /franchise/{id}/products                 — top products by revenue
  GET /franchise/{id}/customers                — top customers by revenue
  GET /franchise/{id}/countries                — revenue by country (city/state for US data)

Data schema (from the DE capstone Gold layer):
  fact_orders:   order_id, customer_id, product_id, order_date, amount, currency, status, quantity, date_key
  dim_customer:  customer_id, name, email, addr_city, addr_state, valid_from, valid_to, is_current
  dim_product:   product_id, name, category, price
  dim_date:      date_key, year, quarter, month, month_name, day_of_week

Your job: implement the TODO sections in each endpoint.
The connection and query helpers are already set up in connection.py.
"""

import os
import time
from datetime import datetime
from tracemalloc import start
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from connection import get_connection, execute_query

#my extra libraries
from datetime import datetime
import re

load_dotenv()

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="NovaCart Account Dashboard API",
    description=(
        "REST API for the NovaCart account manager dashboard. "
        "Built on top of the Gold data layer produced by the Data Engineering team."
    ),
    version="1.0.0",
)

PORT              = int(os.getenv("PORT", 8000))
CLIENT_VALIDATION = os.getenv("CLIENT_VALIDATION", "Dev")
START_TIME        = time.time()

# CORS — only needed for local development
# In SPCS, the NGINX router handles routing so CORS is not required
if CLIENT_VALIDATION == "Dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )


# ── Startup log ───────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    print("\nStarting NovaCart Dashboard API")
    print(f"Port:            {PORT}")
    print(f"Data backend:    {os.getenv('DATA_BACKEND', 'sqlite')}")
    print(f"Validation mode: {CLIENT_VALIDATION}")
    print(f"Docs:            http://localhost:{PORT}/docs\n")


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    """
    Returns service health and confirms the database connection is working.
    Used by the frontend service status indicator.
    """
    uptime = round(time.time() - START_TIME)
    try:
        conn    = get_connection()
        results = execute_query(conn, "SELECT 1 AS ping")
        assert len(results) > 0
    except Exception as e:
        return JSONResponse(status_code=503, content={
            "status":   "degraded",
            "uptime_s": uptime,
            "database": {"status": "error", "message": str(e)},
        })
    return {
        "status":   "healthy",
        "uptime_s": uptime,
        "backend":  os.getenv("DATA_BACKEND", "sqlite"),
        "database": {"status": "connected"},
    }

def is_valid_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.get("/authorize", tags=["Auth"])
def authorize(request: Request):
    """
    SPCS OAuth authorization endpoint.

    When running inside SPCS, the platform injects the authenticated Snowflake
    username in the Sf-Context-Current-User header. This endpoint reads that
    header and returns the user's identity so the frontend can store it.

    In Dev mode: returns a mock user for local development.
    """
    if CLIENT_VALIDATION == "Dev":
        return {"user": "dev_user", "status": "authorized"}

    username = request.headers.get("sf-context-current-user")
    if not username:
        raise HTTPException(status_code=422, detail="Missing Sf-Context-Current-User header")

    return {"user": username, "status": "authorized"}


# ── Franchise endpoints ───────────────────────────────────────────────────────

@app.get("/franchise/summary", tags=["Franchise"])
def get_summary():
    """
    Returns an overview of all orders in the database:
    - Total revenue (delivered + shipped orders only)
    - Total orders
    - Number of unique customers
    - Date range of available data

    Expected response:
    {
        "total_revenue": 1284750.00,
        "total_orders": 8432,
        "unique_customers": 380,
        "date_range": { "start": "2022-01-01", "end": "2022-12-31" }
    }

    TODO: implement this endpoint.
    Hints:
    - Use fact_orders table
    - Filter status IN ('delivered', 'shipped') for revenue
    - Use MIN/MAX of order_date for date_range
    """
    #query code 
    conn = get_connection()
    try:
        results = execute_query(conn, """
            SELECT
                COUNT(DISTINCT order_id)    AS total_orders,
                SUM(amount)                 AS total_revenue,
                COUNT(DISTINCT customer_id) AS unique_customers,
                MIN(order_date)             AS start_date,
                MAX(order_date)             AS end_date
                FROM fact_orders
                WHERE status IN ('delivered', 'shipped')
        """)
        row = results[0]  

        
        return {
            "total_revenue":     round(row["total_revenue"] or 0, 2),
            "total_orders":      row["total_orders"],
            "unique_customers":  row["unique_customers"],
            "date_range": {"start": row["start_date"], "end": row["end_date"]},
        }
    except Exception as e:
        raise HTTPException(
        status_code=500,
        detail=str(e)
    )

    # ── YOUR CODE HERE ────────────────────────────────────────────────────────
    #
    # results = execute_query(conn, """
    #     SELECT
    #         COUNT(DISTINCT order_id)    AS total_orders,
    #         SUM(amount)                 AS total_revenue,
    #         COUNT(DISTINCT customer_id) AS unique_customers,
    #         MIN(order_date)             AS start_date,
    #         MAX(order_date)             AS end_date
    #     FROM fact_orders
    #     WHERE status IN ('delivered', 'shipped')
    # """)
    #
    # row = results[0]
    # return {
    #     "total_revenue":     round(row["total_revenue"] or 0, 2),
    #     "total_orders":      row["total_orders"],
    #     "unique_customers":  row["unique_customers"],
    #     "date_range": {"start": row["start_date"], "end": row["end_date"]},
    # }
    # ─────────────────────────────────────────────────────────────────────────

# i removed these dates str = "2022-01-01", str = "2022-12-31"
@app.get("/franchise/orders", tags=["Franchise"])
def get_orders(
    start: str = Query(..., description = "Start date in YYYY-MM-DD format"), 
    end: str = Query(..., description = "End date in YYYY-MM-DD format") 
    ):
    """
    Returns monthly order volume and revenue for the given date range.
    Used to power the orders overview chart.

    Query parameters:
    start: start date (YYYY-MM-DD)
    end:   end date (YYYY-MM-DD)

    Expected response:
    [
        { "month": "2022-01", "month_name": "January", "order_count": 842, "revenue": 128450.00 },
        { "month": "2022-02", "month_name": "February", "order_count": 910, "revenue": 141230.00 }
    ]

    TODO: implement this endpoint.
    Hints:
    - JOIN fact_orders with dim_date on date_key
    - GROUP BY year, month, month_name
    - Filter order_date between start and end
    - Only include delivered + shipped for revenue
    """
    try:
        #error checking to check the dates
        if not validate_date_format(start):
            raise HTTPException(status_code=400, detail = "Invalid date format. Must be YYYY-MM-DD.")
        if not validate_date_format(end):
            raise HTTPException(status_code=400, detail = "Invalid date format. Must be YYYY-MM-DD.")
        elif start > end:
            raise HTTPException(status_code=400, detail="Invalid date entry")
        elif not start:
            raise HTTPException(status_code=400, detail="Missing start date parameter")
        elif not end:
            raise HTTPException(status_code=400, detail="Missing end date parameter")
        """
        Hints:
        - JOIN fact_orders with dim_date on date_key
        - GROUP BY year, month, month_name
        - Filter order_date between start and end
        - Only include delivered + shipped for revenue
        """
        conn = get_connection()
        results = execute_query(conn, """
            SELECT
            dim_date.year,
            dim_date.month,
            month_name,
            COUNT(DISTINCT(fact_orders.order_id)) AS order_count,
            SUM(amount) AS revenue
            FROM fact_orders 
            JOIN dim_date ON fact_orders.date_key = dim_date.date_key
            WHERE fact_orders.order_date >= ? AND fact_orders.order_date <= ?
                AND fact_orders.status in ('shipped','delivered')
            GROUP BY dim_date.year, dim_date.month, dim_date.month_name
            ORDER BY dim_date.year, dim_date.month

        """, (start,end))
        
        #print(f"Results count: {len(results)}")  # See how many rows
        orders = []
        for row in results:
            orders.append({
            "month": f"{row['year']}-{row['month']:02d}",
            "month_name": row['month_name'],
            "order_count": row['order_count'],
            "revenue": row['revenue']
            })

        #return an json object that is a list of orders
        return orders
        
    #need this so it raises my custom HTTP errors 
    except HTTPException:
        raise
    except Exception as e:
        #print("Error: {e}")
        raise HTTPException(status_code= 500, detail="Internal Server Error")




@app.get("/franchise/products", tags=["Franchise"])
def get_products(start: str = "2022-01-01", end: str = "2022-12-31"):
    """
    Returns the top 10 products by revenue for the given date range.

    Expected response:
    [
        { "product_id": "P001", "name": "Wireless Headphones", "category": "Electronics",
        "units_sold": 342, "revenue": 30578.58 }
    ]

    TODO: implement this endpoint.
    Hints:
      - JOIN fact_orders with dim_product on product_id
      - GROUP BY product_id, name, category
      - ORDER BY revenue DESC, LIMIT 10
    """

    if not start or not end:
        raise HTTPException(status_code=400, detail="Missing start or end date")
    if not is_valid_date(start) or not is_valid_date(end):
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    if start > end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    try:
        conn = get_connection()
        results = execute_query(conn, """
            SELECT p.product_id, p.name, p.category,
                SUM(o.quantity) AS units_sold, SUM(o.amount) AS revenue
            FROM fact_orders o
            JOIN dim_product p 
                ON o.product_id = p.product_id
            WHERE o.order_date >= ? AND o.order_date <= ?
            GROUP BY p.product_id, p.name, p.category
            ORDER BY revenue DESC LIMIT 10
        """, (start, end))
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/franchise/customers", tags=["Franchise"])
def get_customers(start: str = "2022-01-01", end: str = "2022-12-31"):
    """
    Returns the top 20 customers by revenue for the given date range.

    Expected response:
    [
        { "customer_id": "C001", "name": "Alice Johnson", "city": "Austin",
          "state": "TX", "total_orders": 14, "total_spent": 1240.50 }
    ]

    TODO: implement this endpoint.
    Hints:
      - JOIN fact_orders with dim_customer on customer_id
      - Only use dim_customer WHERE is_current = 1
      - GROUP BY customer_id, name, addr_city, addr_state
      - ORDER BY total_spent DESC, LIMIT 20
    """
    if not start or not end:
        raise HTTPException(status_code=400, detail="Missing start or end date")
    if not is_valid_date(start) or not is_valid_date(end):
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    if start > end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")

    try:
        conn = get_connection()
        results = execute_query(conn, """
            SELECT c.customer_id, c.name, c.addr_city AS city, c.addr_state AS state,
                    COUNT(DISTINCT o.order_id) AS total_orders, SUM(o.amount) AS total_spent
            FROM fact_orders o
            JOIN dim_customer c ON o.customer_id = c.customer_id
            WHERE c.is_current = 1 AND o.order_date >= ? AND o.order_date <= ?
            GROUP BY c.customer_id, c.name, c.addr_city, c.addr_state
            ORDER BY total_spent DESC
            LIMIT 20              
        """, (start, end))
        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/franchise/cities", tags=["Franchise"])
def get_cities(start: str = "2022-01-01", end: str = "2022-12-31"):
    """
    Returns revenue grouped by city and state.
    Used to power the geographic breakdown chart.

    Expected response:
    [
        { "city": "Austin", "state": "TX", "order_count": 420, "revenue": 38430.00 }
    ]

    TODO: implement this endpoint.
    Hints:
      - JOIN fact_orders with dim_customer (is_current = 1) on customer_id
      - GROUP BY addr_city, addr_state
      - ORDER BY revenue DESC
    """
    conn = get_connection()

    # ── YOUR CODE HERE ────────────────────────────────────────────────────────
    raise HTTPException(status_code=501, detail="Not implemented yet — your turn!")


def validate_date_format(date_string: str) -> bool:
    # Check pattern: exactly 4 digits, hyphen, 2 digits, hyphen, 2 digits
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    print(f"Validating: {date_string}")
    
    if not re.match(pattern, date_string):
        print(f"Pattern match failed for: {date_string}")
        return False
    
    # Also validate it's a real date (not 2022-13-45)
    try:
        result = datetime.strptime(date_string, '%Y-%m-%d')
        print(f"Date validation passed: {result}")
        return True
    except ValueError as e:
        print(f"ValueError: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return False