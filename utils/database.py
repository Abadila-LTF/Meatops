import sqlite3
import os
from datetime import datetime
import streamlit as st
from typing import List, Dict, Optional

DB_PATH = os.getenv("LOCAL_DB_PATH", "meat_shop.db")

def get_db_connection():
    """Get SQLite database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        raise e

def init_local_db():
    """Initialize local SQLite database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'cashier',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price_per_kg REAL NOT NULL,
                stock_kg REAL DEFAULT 0,
                category TEXT,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                customer_phone TEXT,
                total_amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create invoice_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER REFERENCES invoices(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id),
                product_name TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                price_per_kg REAL NOT NULL,
                total_price REAL NOT NULL
            )
        """)
        # Insert default users if they don't exist
        default_users = [
            ("admin", "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9", "admin"),
            ("cashier", "8d23cf6c86e834a7aa6eded54c26ce2bb2e74903538c61bdd5d2197997ab2f72", "cashier"),
            ("manager", "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f", "manager")
        ]
        for username, password_hash, role in default_users:
            cursor.execute("""
                INSERT OR IGNORE INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
        # Note: No sample products will be inserted automatically
        # Products should be added through the Stock Management interface
        # Add image_path column to existing products table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN image_path TEXT")
        except sqlite3.OperationalError:
            # Column already exists, which is fine
            pass
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def generate_invoice_number():
    """Generate unique invoice number"""
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    return f"INV-{timestamp}"

def add_product(name: str, price_per_kg: float, stock_kg: float, category: str, description: str = "", image_path: str = ""):
    """Add a new product"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO products (name, price_per_kg, stock_kg, category, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, price_per_kg, stock_kg, category, description, image_path))
        
        product_id = cursor.lastrowid
        conn.commit()
        return product_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_products():
    """Get all products from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products ORDER BY name")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return products

def get_product_by_id(product_id: int):
    """Get a specific product by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return product

def update_product(product_id: int, **kwargs):
    """Update product information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Build dynamic update query
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ['name', 'price_per_kg', 'stock_kg', 'category', 'description', 'image_path']:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            return False
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(product_id)
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def update_stock(product_id: int, new_stock: float):
    """Update product stock"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE products SET stock_kg = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (new_stock, product_id))
        
        conn.commit()
        return cursor.rowcount > 0
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def reduce_stock(product_id: int, amount: float):
    """Reduce product stock by specified amount"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE products SET stock_kg = stock_kg - ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND stock_kg >= ?
        """, (amount, product_id, amount))
        
        if cursor.rowcount == 0:
            # Check if product exists and has insufficient stock
            cursor.execute("SELECT stock_kg FROM products WHERE id = ?", (product_id,))
            result = cursor.fetchone()
            if result:
                raise ValueError(f"Insufficient stock. Available: {result['stock_kg']:.3f} kg, Requested: {amount:.3f} kg")
            else:
                raise ValueError("Product not found")
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def create_invoice(customer_name: str, customer_phone: str, items: List[Dict], payment_method: str):
    """Create a new invoice with items"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Calculate total amount
        total_amount = sum(item['total_price'] for item in items)
        
        # Generate invoice number
        invoice_number = generate_invoice_number()
        
        # Insert invoice
        cursor.execute("""
            INSERT INTO invoices (invoice_number, customer_name, customer_phone, total_amount, payment_method)
            VALUES (?, ?, ?, ?, ?)
        """, (invoice_number, customer_name, customer_phone, total_amount, payment_method))
        
        invoice_id = cursor.lastrowid
        
        # Insert invoice items and update stock
        for item in items:
            cursor.execute("""
                INSERT INTO invoice_items (invoice_id, product_id, product_name, weight_kg, price_per_kg, total_price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (invoice_id, item['product_id'], item['product_name'], 
                  item['weight_kg'], item['price_per_kg'], item['total_price']))
            
            # Reduce stock within the same transaction
            cursor.execute("""
                UPDATE products SET stock_kg = stock_kg - ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ? AND stock_kg >= ?
            """, (item['weight_kg'], item['product_id'], item['weight_kg']))
            
            if cursor.rowcount == 0:
                # Check if product exists and has insufficient stock
                cursor.execute("SELECT stock_kg FROM products WHERE id = ?", (item['product_id'],))
                result = cursor.fetchone()
                if result:
                    raise ValueError(f"Insufficient stock for {item['product_name']}. Available: {result['stock_kg']:.3f} kg, Requested: {item['weight_kg']:.3f} kg")
                else:
                    raise ValueError(f"Product {item['product_name']} not found")
        
        conn.commit()
        return True, invoice_number, invoice_id
        
    except Exception as e:
        conn.rollback()
        return False, str(e), None
    finally:
        cursor.close()
        conn.close()

def get_invoices(limit: int = 100, offset: int = 0):
    """Get invoices with pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM invoices 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    invoices = cursor.fetchall()
    cursor.close()
    conn.close()
    return invoices

def get_invoice_by_id(invoice_id: int):
    """Get a specific invoice by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    invoice = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return invoice

def get_invoice_items(invoice_id: int):
    """Get items for a specific invoice"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT product_name, weight_kg, price_per_kg, total_price
        FROM invoice_items
        WHERE invoice_id = ?
        ORDER BY id
    """, (invoice_id,))
    
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

def get_low_stock_products(threshold: float = 5.0):
    """Get products with stock below threshold"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM products 
        WHERE stock_kg < ? 
        ORDER BY stock_kg ASC
    """, (threshold,))
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def get_sales_summary(start_date: str = None, end_date: str = None):
    """Get sales summary for a date range"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if start_date and end_date:
        cursor.execute("""
            SELECT COUNT(*) as invoice_count,
                   SUM(total_amount) as total_revenue,
                   AVG(total_amount) as avg_invoice_value
            FROM invoices
            WHERE DATE(created_at) BETWEEN ? AND ?
        """, (start_date, end_date))
    else:
        cursor.execute("""
            SELECT COUNT(*) as invoice_count,
                   SUM(total_amount) as total_revenue,
                   AVG(total_amount) as avg_invoice_value
            FROM invoices
        """)
    
    summary = cursor.fetchone()
    cursor.close()
    conn.close()
    return summary

def search_products(query: str):
    """Search products by name or category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM products 
        WHERE name LIKE ? OR category LIKE ?
        ORDER BY name
    """, (f"%{query}%", f"%{query}%"))
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def reset_database():
    """Reset database - Clear all data except user accounts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear all tables except users
        cursor.execute("DELETE FROM invoice_items")
        cursor.execute("DELETE FROM invoices")
        cursor.execute("DELETE FROM products")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('invoice_items', 'invoices', 'products')")
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# Initialize database when module is imported
try:
    init_local_db()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}") 