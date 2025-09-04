# sistema_pyme/api/__init__.py
"""
API REST para el Sistema de Gestión PYME.

Este paquete proporciona endpoints REST para integraciones externas.
"""

# ❌ REMOVER estas líneas que causan el error:
# from .main import app
# from .endpoints import router

# ✅ Dejar solo la metadata del paquete
__version__ = '1.0.0'
__author__ = 'Sistema de Gestión PYME'
__description__ = 'API REST para integraciones externas'

# Opcional: Si realmente necesitas exportar, hazlo así:
# __all__ = []  # Lista vacía porque no exportamos símbolos directamente