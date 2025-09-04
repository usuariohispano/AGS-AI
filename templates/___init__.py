"""
Sistema de plantillas para el Sistema de Gestión PYME.

Este paquete maneja plantillas para emails, reportes y otros contenidos.
"""

from templates.email_templates import EmailTemplateSystem, DEFAULT_TEMPLATES

__all__ = [
    'EmailTemplateSystem',
    'DEFAULT_TEMPLATES'
]

__version__ = '1.0.0'
__author__ = 'Sistema de Gestión PYME'
__description__ = 'Sistema de plantillas para emails y reportes'