# sistema_pyme/plugins/__init__.py
"""
Paquete de plugins para el Sistema de Gestión PYME.
"""

# ✅ Exportar solo lo que realmente existe y está disponible
from plugins.base import Plugin, PluginSystem
from plugins.example_plugin import AdvancedAnalyticsPlugin, EmailMarketingPlugin

__all__ = [
    'Plugin',
    'PluginSystem', 
    'AdvancedAnalyticsPlugin',
    'EmailMarketingPlugin'
]

__version__ = '1.0.0'