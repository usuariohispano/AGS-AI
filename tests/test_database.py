# sistema_pyme/tests/test_database.py
import pytest
import sqlite3

# Import absoluto desde el paquete raíz  
import database as db

def test_database_initialization():
    """Test de inicialización de la base de datos"""
    conn = sqlite3.connect(':memory:')
    db.init_db(conn)
    
    # Verificar que las tablas se crearon
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in c.fetchall()]
    
    expected_tables = ['businesses', 'imported_files', 'sales', 'customers', 
                      'employees', 'inventory', 'finances']
    
    for table in expected_tables:
        assert table in tables

def test_business_operations():
    """Test de operaciones de negocio"""
    conn = sqlite3.connect(':memory:')
    db.init_db(conn)
    
    # Guardar negocio
    db.save_business(conn, "Mi Negocio", "restaurante", "Descripción de prueba")  # type: ignore
    
    # Obtener negocio actual
    business = db.get_current_business(conn)  # type: ignore
    assert business is not None
    assert business['name'] == "Mi Negocio"
    assert business['type'] == "restaurante"

def test_multiple_businesses():
    """Test con múltiples negocios"""
    conn = sqlite3.connect(':memory:')
    db.init_db(conn)
    
    # Guardar múltiples negocios
    db.save_business(conn, "Negocio 1", "tienda", "Descripción 1")  # type: ignore
    db.save_business(conn, "Negocio 2", "restaurante", "Descripción 2")  # type: ignore
    
    # Debería obtener el último negocio
    business = db.get_current_business(conn)  # type: ignore
    assert business is not None
    assert business['name'] == "Negocio 2"

def test_get_current_business_none():
    """Test para verificar que get_current_business retorna None cuando no hay negocios"""
    conn = sqlite3.connect(':memory:')
    db.init_db(conn)
    
    # Cuando no hay negocios, debería retornar None
    business = db.get_current_business(conn)  # type: ignore
    assert business is None

def test_save_business_with_none_values():
    """Test para verificar el manejo de valores None"""
    conn = sqlite3.connect(':memory:')
    db.init_db(conn)
    
    # Probar con valores None/empty
    db.save_business(conn, "Test Business", "tienda", None)  # type: ignore
    
    business = db.get_current_business(conn)  # type: ignore
    assert business is not None
    assert business['name'] == "Test Business"
    assert business['type'] == "tienda"

def test_business_fields_completeness():
    """Test para verificar que todos los campos del negocio están presentes"""
    conn = sqlite3.connect(':memory:')
    db.init_db(conn)
    
    db.save_business(conn, "Negocio Completo", "restaurante", "Descripción completa")  # type: ignore
    
    business = db.get_current_business(conn)  # type: ignore
    assert business is not None
    
    # Verificar que todos los campos esperados están presentes
    expected_fields = ['id', 'name', 'type', 'description']
    for field in expected_fields:
        assert field in business, f"El campo {field} debería estar en el negocio"