# sistema_pyme/event_system.py
import sqlite3
from typing import Dict, List, Any, Optional, Union
import json
from datetime import datetime, timedelta

class EventSystem:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        # ✅ CORREGIDO: Simplificar el type hint
        self.subscribers: Dict[str, List[Any]] = {}
        self.init_events_table()
    
    def init_events_table(self) -> None:
        """Crear tabla para registro de eventos"""
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS system_events
                    (id INTEGER PRIMARY KEY, event_type TEXT, event_data TEXT,
                     created_by INTEGER, created_at TIMESTAMP)''')
        self.conn.commit()
    
    def subscribe(self, event_type: str, callback: Any) -> None:
        """Suscribir una función a un tipo de evento"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def publish(self, event_type: str, event_data: Any, user_id: Optional[int] = None) -> int:
        """Publicar un evento y notificar a los suscriptores"""
        # Registrar evento en base de datos
        c = self.conn.cursor()
        c.execute('''INSERT INTO system_events 
                    (event_type, event_data, created_by, created_at)
                    VALUES (?, ?, ?, ?)''',
                 (event_type, json.dumps(event_data), user_id, datetime.now()))
        self.conn.commit()
        event_id = c.lastrowid or 0
        
        # Notificar a suscriptores
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    print(f"Error en callback para evento {event_type}: {e}")
        
        return event_id
    
    def get_recent_events(self, limit: int = 50) -> List[Any]:
        """Obtener eventos recientes"""
        c = self.conn.cursor()
        c.execute('''SELECT event_type, event_data, created_by, created_at 
                    FROM system_events ORDER BY created_at DESC LIMIT ?''', (limit,))
        results = c.fetchall()
        return results if results else []
    
    def get_events_by_type(self, event_type: str, limit: int = 50) -> List[Any]:
        """Obtener eventos por tipo"""
        c = self.conn.cursor()
        c.execute('''SELECT event_type, event_data, created_by, created_at 
                    FROM system_events WHERE event_type = ? ORDER BY created_at DESC LIMIT ?''', 
                 (event_type, limit))
        results = c.fetchall()
        return results if results else []
    
    def get_events_by_user(self, user_id: int, limit: int = 50) -> List[Any]:
        """Obtener eventos por usuario"""
        c = self.conn.cursor()
        c.execute('''SELECT event_type, event_data, created_by, created_at 
                    FROM system_events WHERE created_by = ? ORDER BY created_at DESC LIMIT ?''', 
                 (user_id, limit))
        results = c.fetchall()
        return results if results else []
    
    def clear_old_events(self, days_old: int = 30) -> int:
        """Eliminar eventos más antiguos que X días"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        c = self.conn.cursor()
        c.execute('''DELETE FROM system_events WHERE created_at < ?''', 
                 (cutoff_date,))
        self.conn.commit()
        return c.rowcount

# Eventos predefinidos del sistema
class EventTypes:
    USER_LOGIN = 'user_login'
    USER_LOGOUT = 'user_logout'
    USER_CREATED = 'user_created'
    USER_UPDATED = 'user_updated'
    FILE_UPLOADED = 'file_uploaded'
    FILE_PROCESSED = 'file_processed'
    FILE_ERROR = 'file_error'
    SALE_CREATED = 'sale_created'
    SALE_UPDATED = 'sale_updated'
    SALE_DELETED = 'sale_deleted'
    CUSTOMER_CREATED = 'customer_created'
    CUSTOMER_UPDATED = 'customer_updated'
    INVENTORY_LOW = 'inventory_low'
    INVENTORY_CRITICAL = 'inventory_critical'
    INVENTORY_UPDATED = 'inventory_updated'
    LEAD_CREATED = 'lead_created'
    LEAD_CONVERTED = 'lead_converted'
    FINANCIAL_ALERT = 'financial_alert'
    BACKUP_CREATED = 'backup_created'
    BACKUP_RESTORED = 'backup_restored'
    SYSTEM_ERROR = 'system_error'
    SYSTEM_WARNING = 'system_warning'
    SYSTEM_INFO = 'system_info'

# Alias para backwards compatibility
EVENT_TYPES = EventTypes

# Ejemplos de uso
def setup_default_event_handlers(event_system: EventSystem) -> None:
    """Configurar manejadores de eventos por defecto"""
    
    def log_event_to_console(event_data: Any) -> None:
        """Manejador simple que loggea eventos a consola"""
        print(f"📝 [Evento] {event_data}")
    
    def handle_inventory_alerts(event_data: Any) -> None:
        """Manejador para alertas de inventario"""
        if isinstance(event_data, dict) and event_data.get('type') == 'low_stock':
            product = event_data.get('product', 'Desconocido')
            stock = event_data.get('current_stock', 0)
            print(f"⚠️  Alerta de inventario: {product} tiene solo {stock} unidades")
    
    def handle_financial_alerts(event_data: Any) -> None:
        """Manejador para alertas financieras"""
        if isinstance(event_data, dict):
            alert_type = event_data.get('type', '')
            message = event_data.get('message', '')
            print(f"💰 Alerta financiera ({alert_type}): {message}")
    
    # Suscribir manejadores
    event_system.subscribe(EventTypes.INVENTORY_LOW, handle_inventory_alerts)
    event_system.subscribe(EventTypes.INVENTORY_CRITICAL, handle_inventory_alerts)
    event_system.subscribe(EventTypes.FINANCIAL_ALERT, handle_financial_alerts)
    event_system.subscribe(EventTypes.SYSTEM_ERROR, log_event_to_console)