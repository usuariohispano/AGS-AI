# sistema_pyme/api/endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Modelos Pydantic
class SaleCreate(BaseModel):
    product: str
    quantity: int
    amount: float
    business_id: int

class CustomerCreate(BaseModel):
    name: str
    company: str
    email: str
    phone: str
    status: str = "Activo"

class InventoryUpdate(BaseModel):
    product: str
    quantity: int

# Dependencia para obtener la conexión a la base de datos
def get_db_connection():
    try:
        conn = sqlite3.connect('data/sistema_pyme.db', check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
        yield conn
    finally:
        if conn:
            conn.close()

@router.post("/sales/", response_model=dict)
async def create_sale(sale: SaleCreate, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Endpoint para crear una nueva venta"""
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO sales (date, product, quantity, amount, business_id)
                    VALUES (?, ?, ?, ?, ?)''',
                 (datetime.now().isoformat(), sale.product, sale.quantity, 
                  sale.amount, sale.business_id))
        conn.commit()
        return {"message": "Venta creada exitosamente", "sale_id": c.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear venta: {str(e)}")

@router.get("/sales/", response_model=dict)
async def get_sales(limit: int = 100, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Endpoint para obtener ventas"""
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM sales ORDER BY date DESC LIMIT ?''', (limit,))
        sales = [dict(row) for row in c.fetchall()]  # Convertir a diccionarios
        return {"sales": sales, "count": len(sales)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")

@router.post("/customers/", response_model=dict)
async def create_customer(customer: CustomerCreate, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Endpoint para crear un nuevo cliente"""
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO customers 
                    (name, company, email, phone, status, last_purchase)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (customer.name, customer.company, customer.email, 
                  customer.phone, customer.status, datetime.now().isoformat()))
        conn.commit()
        return {"message": "Cliente creado exitosamente", "customer_id": c.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear cliente: {str(e)}")

@router.get("/customers/", response_model=dict)
async def get_customers(limit: int = 100, conn: sqlite3.Connection = Depends(get_db_connection)):
    """Endpoint para obtener clientes"""
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM customers ORDER BY name LIMIT ?''', (limit,))
        customers = [dict(row) for row in c.fetchall()]
        return {"customers": customers, "count": len(customers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener clientes: {str(e)}")

@router.get("/inventory/", response_model=dict)
async def get_inventory(conn: sqlite3.Connection = Depends(get_db_connection)):
    """Endpoint para obtener inventario"""
    try:
        c = conn.cursor()
        c.execute('''SELECT * FROM inventory ORDER BY product''')
        inventory = [dict(row) for row in c.fetchall()]
        return {"inventory": inventory, "count": len(inventory)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener inventario: {str(e)}")

@router.put("/inventory/{product_id}", response_model=dict)
async def update_inventory(product_id: int, update: InventoryUpdate, 
                          conn: sqlite3.Connection = Depends(get_db_connection)):
    """Endpoint para actualizar inventario"""
    try:
        c = conn.cursor()
        c.execute('''UPDATE inventory SET current_stock = ? WHERE id = ?''',
                 (update.quantity, product_id))
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
            
        conn.commit()
        return {"message": "Inventario actualizado exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar inventario: {str(e)}")

# ✅ Exportar el router
__all__ = ['router']