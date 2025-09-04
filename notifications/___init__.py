"""
Sistema de notificaciones para el Sistema de Gestión PYME.

Este paquete maneja las notificaciones multi-canal (in-app, email, etc.).
"""

from notifications.notification_system import NotificationSystem, email_channel, in_app_channel, sms_channel

__all__ = [
    'NotificationSystem',
    'email_channel',
    'in_app_channel', 
    'sms_channel'
]

__version__ = '1.0.0'
__author__ = 'Sistema de Gestión PYME'
__description__ = 'Sistema de notificaciones multi-canal'