# sistema_pyme/tests/test_auth.py
import pytest
import sqlite3

# Import absoluto desde el paquete raíz
from auth import AuthSystem

@pytest.fixture
def auth_system():
    """Fixture para sistema de autenticación"""
    conn = sqlite3.connect(':memory:')
    return AuthSystem(conn)

def test_auth_initialization(auth_system):
    """Test de inicialización del sistema de autenticación"""
    # Verificar que las tablas se crearon
    c = auth_system.conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in c.fetchall()]
    
    assert 'users' in tables
    assert 'sessions' in tables
    assert 'permissions' in tables

def test_user_creation(auth_system):
    """Test de creación de usuario"""
    result = auth_system.create_user('testuser', 'test@example.com', 'password123')
    assert result == True
    
    # Verificar que el usuario existe
    c = auth_system.conn.cursor()
    c.execute("SELECT username FROM users WHERE username = 'testuser'")
    user = c.fetchone()
    assert user is not None

def test_user_authentication(auth_system):
    """Test de autenticación de usuario"""
    auth_system.create_user('testuser', 'test@example.com', 'password123')
    
    # Autenticación exitosa
    user = auth_system.authenticate_user('testuser', 'password123')
    assert user is not None
    assert user['username'] == 'testuser'
    
    # Autenticación fallida
    user = auth_system.authenticate_user('testuser', 'wrongpassword')
    assert user is None

def test_password_hashing(auth_system):
    """Test de hashing de contraseñas"""
    password = "mysecurepassword"
    hashed = auth_system.hash_password(password)
    
    # Verificar que el hash es diferente a la contraseña original
    assert password != hashed
    
    # Verificar que la verificación funciona
    assert auth_system.verify_password(password, hashed) == True
    assert auth_system.verify_password("wrongpassword", hashed) == False

def test_session_management(auth_system):
    """Test de gestión de sesiones"""
    auth_system.create_user('testuser', 'test@example.com', 'password123')
    user = auth_system.authenticate_user('testuser', 'password123')
    
    # Crear sesión
    session_token = auth_system.create_session(user['id'])
    assert session_token is not None
    
    # Validar sesión
    user_id = auth_system.validate_session(session_token)
    assert user_id == user['id']

def test_permission_system(auth_system):
    """Test del sistema de permisos"""
    # Verificar permisos de admin
    assert auth_system.has_permission('admin', 'finance', 'can_view') == True
    assert auth_system.has_permission('admin', 'finance', 'can_edit') == True
    
    # Verificar permisos de usuario regular
    assert auth_system.has_permission('user', 'dashboard', 'can_view') == True
    assert auth_system.has_permission('user', 'finance', 'can_edit') == False