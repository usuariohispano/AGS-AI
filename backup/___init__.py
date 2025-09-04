"""
Sistema de backup y restauración para el Sistema de Gestión PYME.

Este paquete maneja las copias de seguridad automáticas y manuales de la base de datos.
"""

from backup.backup_system import BackupSystem

__all__ = [
    'BackupSystem'
]

__version__ = '1.0.0'
__author__ = 'Sistema de Gestión PYME'
__description__ = 'Sistema de backup y restauración'