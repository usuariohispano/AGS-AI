# sistema_pyme/notifications/notification_system.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
import sqlite3

class NotificationSystem:
    def __init__(self, conn):
        self.conn = conn
        self.channels = {}
        self.init_notifications_table()
    
    def init_notifications_table(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS notifications
                    (id INTEGER PRIMARY KEY, type TEXT, title TEXT, message TEXT,
                     priority TEXT, read BOOLEAN, user_id INTEGER, created_at TIMESTAMP)''')
        self.conn.commit()
    
    def register_channel(self, name, channel_func):
        self.channels[name] = channel_func
    
    def send_notification(self, title: str, message: str, priority: str = "medium", 
                         channels: Optional[List[str]] = None, user_id: Optional[int] = None) -> int:
        """Enviar notificación a través de los canales especificados"""
        if channels is None:
            channels = ["in_app"]
        
        # Asegurar que user_id sea None o int
        db_user_id = user_id
        
        # Registrar en base de datos
        c = self.conn.cursor()
        c.execute('''INSERT INTO notifications 
                    (type, title, message, priority, read, user_id, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 ("system", title, message, priority, False, db_user_id, datetime.now()))
        self.conn.commit()
        notification_id = c.lastrowid or 0
        
        # Enviar a través de canales
        for channel_name in channels:
            if channel_name in self.channels:
                try:
                    self.channels[channel_name](title, message, priority, user_id)
                except Exception as e:
                    print(f"Error enviando notificación por {channel_name}: {e}")
        
        return notification_id
    
    def get_user_notifications(self, user_id: int, unread_only: bool = True) -> List[Any]:
        """Obtener notificaciones de un usuario"""
        c = self.conn.cursor()
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
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Marcar notificación como leída"""
        c = self.conn.cursor()
        c.execute('''UPDATE notifications SET read = TRUE 
                    WHERE id = ? AND user_id = ?''', (notification_id, user_id))
        self.conn.commit()
        return c.rowcount > 0

    def get_notification_count(self, user_id: int, unread_only: bool = True) -> int:
        """Obtener cantidad de notificaciones de un usuario"""
        c = self.conn.cursor()
        if unread_only:
            c.execute('''SELECT COUNT(*) FROM notifications 
                        WHERE user_id = ? AND read = FALSE''',
                     (user_id,))
        else:
            c.execute('''SELECT COUNT(*) FROM notifications 
                        WHERE user_id = ?''',
                     (user_id,))
        result = c.fetchone()
        return result[0] if result and result[0] is not None else 0

# ✅ CORREGIDO: Funciones de canal sin type hints problemáticos
def email_channel(smtp_config: Dict[str, Any]):
    """Canal de notificación por email"""
    def send_email(title: str, message: str, priority: str, user_id: Optional[int] = None):
        # Obtener email del usuario desde la base de datos
        # y enviar email usando la configuración SMTP
        print(f"Email enviado: {title} - {message} - Prioridad: {priority}")
    return send_email

def in_app_channel(title: str, message: str, priority: str, user_id: Optional[int] = None):
    """Canal de notificación in-app (ya implementado en la base de datos)"""
    # La notificación ya se registró en la base de datos
    print(f"Notificación in-app: {title} - {message}")

def sms_channel(sms_config: Dict[str, Any]):
    """Canal de notificación por SMS"""
    def send_sms(title: str, message: str, priority: str, user_id: Optional[int] = None):
        # Implementar envío de SMS
        print(f"SMS enviado: {title} - {message} - Prioridad: {priority}")
    return send_sms

def push_channel(push_config: Dict[str, Any]):
    """Canal de notificación push"""
    def send_push(title: str, message: str, priority: str, user_id: Optional[int] = None):
        # Implementar notificación push
        print(f"Push notification: {title} - {message} - Prioridad: {priority}")
    return send_push