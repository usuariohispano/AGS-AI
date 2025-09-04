# sistema_pyme/database.py
import sqlite3
import json
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager

# Variable local para almacenar conexiones por hilo
_local = threading.local()

def get_connection(db_path='data/sistema_pyme.db') -> sqlite3.Connection:
    """Obtener conexión a la base de datos (una por hilo)"""
    if not hasattr(_local, 'conn') or _local.conn is None:
        _local.conn = sqlite3.connect(db_path, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn

@contextmanager
def get_db_connection(db_path='data/sistema_pyme.db'):
    """Context manager para manejar conexiones de base de datos"""
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        # No cerramos la conexión para reutilizarla en el mismo hilo
        pass

def close_connection():
    """Cerrar la conexión actual del hilo"""
    if hasattr(_local, 'conn') and _local.conn:
        _local.conn.close()
        _local.conn = None

def init_db(db_path='data/sistema_pyme.db') -> sqlite3.Connection:
    """Inicializar la base de datos y crear tablas si no existen"""
    conn = get_connection(db_path)
    c = conn.cursor()
    
    # Tabla de negocios
    c.execute('''CREATE TABLE IF NOT EXISTS businesses
                (id INTEGER PRIMARY KEY, name TEXT, type TEXT, 
                 description TEXT, created_at TIMESTAMP)''')
    
    # Tabla de eventos del sistema
    c.execute('''CREATE TABLE IF NOT EXISTS system_events
                (id INTEGER PRIMARY KEY, event_type TEXT, event_data TEXT,
                 created_by INTEGER, created_at TIMESTAMP)''')
    
    # Tabla de notificaciones
    c.execute('''CREATE TABLE IF NOT EXISTS notifications
                (id INTEGER PRIMARY KEY, type TEXT, title TEXT, message TEXT,
                 priority TEXT, read BOOLEAN, user_id INTEGER, created_at TIMESTAMP)''')
    
    conn.commit()
    return conn

def save_business(conn: sqlite3.Connection, name: str, business_type: str, description: Optional[str] = None) -> None:
    """Guardar un nuevo negocio en la base de datos"""
    c = conn.cursor()
    c.execute("INSERT INTO businesses (name, type, description, created_at) VALUES (?, ?, ?, ?)",
             (name, business_type, description, datetime.now()))
    conn.commit()

def get_current_business(conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    """Obtener el negocio actual de la base de datos"""
    c = conn.cursor()
    c.execute("SELECT * FROM businesses ORDER BY id DESC LIMIT 1")
    business = c.fetchone()
    
    if business:
        return {
            'id': business[0],
            'name': business[1],
            'type': business[2],
            'description': business[3]
        }
    return None

def log_event(conn: sqlite3.Connection, event_type: str, event_data: Any, user_id: Optional[int] = None) -> int:
    """Registrar un evento en el sistema"""
    c = conn.cursor()
    c.execute('''INSERT INTO system_events 
                (event_type, event_data, created_by, created_at)
                VALUES (?, ?, ?, ?)''',
             (event_type, json.dumps(event_data), user_id, datetime.now()))
    conn.commit()
    return c.lastrowid or 0

def get_recent_events(conn: sqlite3.Connection, limit: int = 50) -> List[Any]:
    """Obtener eventos recientes"""
    c = conn.cursor()
    c.execute('''SELECT event_type, event_data, created_by, created_at 
                FROM system_events ORDER BY created_at DESC LIMIT ?''', (limit,))
    results = c.fetchall()
    return results if results else []

def create_notification(conn: sqlite3.Connection, notif_type: str, title: str, message: str, 
                       priority: str = "medium", user_id: Optional[int] = None) -> int:
    """Crear una nueva notificación"""
    c = conn.cursor()
    c.execute('''INSERT INTO notifications 
                (type, title, message, priority, read, user_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
             (notif_type, title, message, priority, False, user_id, datetime.now()))
    conn.commit()
    return c.lastrowid or 0

def get_user_notifications(conn: sqlite3.Connection, user_id: int, unread_only: bool = True) -> List[Any]:
    """Obtener notificaciones de un usuario"""
    c = conn.cursor()
    if unread_only:
        c.execute('''SELECT * FROM notifications 
                    WHERE user_id = ? AND read = FALSE ORDER BY created_at DESC''',
                 (user_id,))
    else:
        c.execute('''SELECT * FROM notifications 
                    WHERE user_id = ? ORDER BY created_at DESC''',
                 (user_id,))
    results = c.fetchall()
    return results if results else []

def mark_notification_as_read(conn: sqlite3.Connection, notification_id: int, user_id: int) -> bool:
    """Marcar notificación como leída"""
    c = conn.cursor()
    c.execute('''UPDATE notifications SET read = TRUE 
                WHERE id = ? AND user_id = ?''', (notification_id, user_id))
    conn.commit()
    return c.rowcount > 0