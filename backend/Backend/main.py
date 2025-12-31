
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
import bcrypt
from pydantic import BaseModel
from pydantic import BaseModel
from typing import List, Optional

# Add these with your other Pydantic models
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItem]


# Add this class to define what data we need to create a product
class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float
    category_id: int

app = FastAPI()

# Setup Password Hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

# --- DATABASE CONFIGURATION ---
# REPLACE 'YOUR_SERVER_NAME_HERE' with your actual SQL Server Name
SERVER_NAME = 'FALAKSHER\SQLEXPRESS' 
DATABASE_NAME = 'FH_Store_DB'

# Connection String (Windows Authentication)
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;"
)

# --- CORS (Allow React to talk to Python) ---
origins = [
    "http://localhost:5173",  # This is your React App
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODELS (Pydantic) ---
# These define what the data looks like for the API
class Product(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    price: float
    status: str

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "FH Store API is running!"}

@app.get("/products")
def get_products():
    try:
        # 1. Connect to Database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 2. Run SQL Query
        # We join with Categories to get the Category Name instead of just the ID
        query = """
            SELECT p.ProductID, p.Name, p.SKU, c.Name as CategoryName, p.Price, p.Status 
            FROM Products p
            LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
        """
        cursor.execute(query)
        
        # 3. Format the data into a list of dictionaries
        products = []
        rows = cursor.fetchall()
        for row in rows:
            products.append({
                "id": row.ProductID,
                "name": row.Name,
                "sku": row.SKU,
                "category": row.CategoryName if row.CategoryName else "Uncategorized",
                "price": float(row.Price),
                "status": row.Status
            })
            
        # 4. Close connection
        conn.close()
        
        return products

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/products")
def create_product(product: ProductCreate):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        query = """
            INSERT INTO Products (Name, SKU, CategoryID, Price, Status) 
            VALUES (?, ?, ?, ?, 'Active')
        """
        cursor.execute(query, (product.name, product.sku, product.category_id, product.price))
        conn.commit()
        
        conn.close()
        return {"message": "Product created successfully"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/login")
# def login(request: LoginRequest):
#     try:
#         conn = pyodbc.connect(conn_str)
#         cursor = conn.cursor()
        
#         # 1. Find user by Email
#         cursor.execute("SELECT UserID, Name, Role, PasswordHash FROM Users WHERE Email = ?", (request.email,))
#         user = cursor.fetchone()
#         conn.close()

#         # 2. If user doesn't exist
#         if not user:
#             raise HTTPException(status_code=400, detail="Invalid email or password")

#         # 3. Verify Password (Compare the plain text to the Hash in DB)
#         # Note: In real app, we verify hash. For simplicity if you manually inserted plain text:
#         # if request.password != user.PasswordHash: ...
        
#         # PROPER SECURITY CHECK:
#         if not pwd_context.verify(request.password, user.PasswordHash):
#              raise HTTPException(status_code=400, detail="Invalid email or password")

#         # 4. Return User Info (Success!)
#         return {
#             "message": "Login successful",
#             "user": {
#                 "id": user.UserID,
#                 "name": user.Name,
#                 "role": user.Role
#             }
#         }

#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
@app.post("/login")
def login(request: LoginRequest):
    try:
        print(f"\n--- LOGIN ATTEMPT FOR: {request.email} ---") # Debug 1
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 1. Find user
        cursor.execute("SELECT UserID, Name, Role, PasswordHash FROM Users WHERE Email = ?", (request.email,))
        user = cursor.fetchone()
        conn.close()

        # 2. Check if user exists
        if not user:
            print("ERROR: User not found in database") # Debug 2
            raise HTTPException(status_code=400, detail="Invalid email or password")

        # 3. Prepare Data for Check
        # .strip() removes invisible spaces that SQL might have added
        db_hash = user.PasswordHash.strip() 
        
        print(f"User Found: {user.Name}")           # Debug 3
        print(f"Stored Hash: '{db_hash}'")          # Debug 4 (Check if this looks like $2b$...)
        print(f"Input Pass:  '{request.password}'") # Debug 5
        
        # Convert to bytes (Required by bcrypt)
        user_hash_bytes = db_hash.encode('utf-8')
        password_bytes = request.password.encode('utf-8')

        # 4. Verify
        if not bcrypt.checkpw(password_bytes, user_hash_bytes):
             print("ERROR: Password Mismatch! (Hash verification failed)") # Debug 6
             raise HTTPException(status_code=400, detail="Invalid email or password")

        print("SUCCESS: Login Verified!") # Debug 7
        
        return {
            "message": "Login successful",
            "user": {
                "id": user.UserID,
                "name": user.Name,
                "role": user.Role
            }
        }

    except Exception as e:
        print(f"CRITICAL ERROR: {e}") # Debug 8
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW ENDPOINTS FOR PURCHASING ---

@app.get("/customers")
def get_customers():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("SELECT CustomerID, Name FROM Customers")
        customers = [{"id": row.CustomerID, "name": row.Name} for row in cursor.fetchall()]
        conn.close()
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/orders")
def create_order(order: OrderCreate):
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 1. Calculate Total Amount
        total_amount = sum(item.quantity * item.unit_price for item in order.items)
        
        # 2. Insert the Main Order Record
        # We use OUTPUT INSERTED.OrderID to get the ID of the new order immediately
        cursor.execute("""
            INSERT INTO Orders (CustomerID, OrderDate, Status, TotalAmount) 
            OUTPUT INSERTED.OrderID
            VALUES (?, GETDATE(), 'Pending', ?)
        """, (order.customer_id, total_amount))
        
        order_id = cursor.fetchone()[0] # Get the new Order ID
        
        # 3. Process Each Item (Insert Detail + Update Stock)
        for item in order.items:
            # A. Add to OrderDetails
            cursor.execute("""
                INSERT INTO OrderDetails (OrderID, ProductID, QuantityOrdered, UnitPrice)
                VALUES (?, ?, ?, ?)
            """, (order_id, item.product_id, item.quantity, item.unit_price))
            
            # B. Decrease Inventory Stock
            cursor.execute("""
                UPDATE Inventory 
                SET QuantityOnHand = QuantityOnHand - ? 
                WHERE ProductID = ?
            """, (item.quantity, item.product_id))

        conn.commit() # Save everything
        conn.close()
        
        return {"message": "Order placed successfully!", "order_id": order_id}

    except Exception as e:
        if 'conn' in locals(): conn.rollback() # Undo changes if error
        print(f"Transaction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

        