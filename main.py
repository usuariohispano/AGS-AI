# sistema_pyme/main.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import time
from functools import wraps

# ✅ IMPORTS ACTUALIZADOS (sin sistema_pyme.)
from auth import AuthSystem, render_login_register
from responsive import ResponsiveDesign, detect_mobile
from modules.data_import import render_data_import_module
from modules.finance import render_finance_module
from modules.crm import render_crm_module
from modules.hr import render_hr_module
from modules.inventory import render_inventory_module

# ✅ Importar Optional para type hints
from typing import Optional, Dict, Any, List

# ✅ Importar nuevos sistemas (estos están bien)
from event_system import EventSystem, EventTypes
from backup.backup_system import BackupSystem
from notifications.notification_system import NotificationSystem
from plugins.base import PluginSystem
from templates.email_templates import EmailTemplateSystem

# ✅ Importar requests para las pruebas de API
import requests

import database as db

# Decorador para reintentar operaciones en base de datos bloqueada
def retry_on_locked(db_operation):
    @wraps(db_operation)
    def wrapper(*args, **kwargs):
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return db_operation(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
                raise
    return wrapper

# Configuración de página
st.set_page_config(
    page_title="Sistema de Gestión PYME con IA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar diseño responsive
ResponsiveDesign.init_responsive()

# Inicializar base de datos con manejo de errores
try:
    conn = db.init_db()
    auth_system = AuthSystem(conn)
    
    # ✅ Inicializar nuevos sistemas
    event_system = EventSystem(conn)
    backup_system = BackupSystem('data/sistema_pyme.db')
    notification_system = NotificationSystem(conn)
    plugin_system = PluginSystem(conn)
    email_templates = EmailTemplateSystem()
    
    # ✅ Configurar canales de notificación
    def in_app_channel(title: str, message: str, priority: str, user_id: Optional[int] = None) -> None:
        pass

    notification_system.register_channel("in_app", in_app_channel)
    
    # ✅ Iniciar backups automáticos
    backup_system.start_automatic_backups(interval_hours=24)
    
    # ✅ Cargar plugins
    plugin_system.load_plugins()
    
except sqlite3.OperationalError as e:
    st.error(f"Error de base de datos: {e}")
    st.stop()

# Verificar autenticación
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
    st.session_state.user = None

# Página de login si no está autenticado
if not st.session_state.auth_token or not auth_system.validate_session(st.session_state.auth_token):
    render_login_register(auth_system)
    st.stop()

# Obtener usuario actual y permisos
user_id = auth_system.validate_session(st.session_state.auth_token)
if user_id is None:
    st.error("Sesión inválida. Por favor, inicia sesión nuevamente.")
    st.session_state.auth_token = None
    st.session_state.user = None
    st.stop()

# ✅ Obtener rol de usuario de forma segura
user_role = auth_system.get_user_role(user_id)

# ✅ Verificar que st.session_state.user existe antes de acceder a él
user_name = st.session_state.user.get('username', 'Usuario') if st.session_state.user and isinstance(st.session_state.user, dict) else 'Usuario'

# ✅ Publicar evento de login
try:
    event_system.publish(
        EventTypes.USER_LOGIN,
        {"user_id": user_id, "username": user_name}, 
        user_id
    )
except:
    pass  # Ignorar errores de eventos

# Sidebar de navegación con permisos
st.sidebar.title("📋 Sistema de Gestión PYME con IA")
st.sidebar.image("https://img.icons8.com/clouds/100/000000/business.png", width=100)

# ✅ Notificaciones del usuario - VERIFICAR que user_id no es None
try:
    notifications = notification_system.get_user_notifications(user_id, unread_only=True) if user_id is not None else []
    if notifications:
        notification_count = len(notifications)
        st.sidebar.markdown(f"**🔔 Notificaciones ({notification_count})**")
        
        for notif in notifications[:3]:
            if notif and len(notif) > 3:
                notification_id = notif[0]
                notification_title = notif[2]
                notification_message = notif[3]
                
                with st.sidebar.expander(f"{notification_title}", expanded=False):
                    st.write(notification_message)
                    if st.button("Marcar como leída", key=f"read_{notification_id}"):
                        if user_id is not None:
                            notification_system.mark_as_read(notification_id, user_id)
                            st.rerun()
except:
    pass  # Ignorar errores de notificaciones

# Menú basado en permisos
menu_options = []
if auth_system.has_permission(user_role, 'dashboard', 'can_view'):
    menu_options.append("Dashboard")
if auth_system.has_permission(user_role, 'data_import', 'can_view'):
    menu_options.append("Importar Datos")
if auth_system.has_permission(user_role, 'finance', 'can_view'):
    menu_options.append("Finanzas")
if auth_system.has_permission(user_role, 'crm', 'can_view'):
    menu_options.append("CRM Clientes")
if auth_system.has_permission(user_role, 'hr', 'can_view'):
    menu_options.append("Recursos Humanos")
if auth_system.has_permission(user_role, 'inventory', 'can_view'):
    menu_options.append("Inventario")

if auth_system.has_permission(user_role, 'admin', 'can_view'):
    menu_options.append("Administración")
    menu_options.append("Plugins")
    menu_options.append("Backups")

menu_options.append("Cerrar Sesión")

# ✅ Definir menu variable
menu = st.sidebar.radio("Navegación", menu_options)

# Barra de navegación móvil
if detect_mobile():
    ResponsiveDesign.mobile_navigation()

# Obtener negocio actual
try:
    current_business = db.get_current_business(conn)
except:
    current_business = None

# Contenido principal basado en selección de menú
try:
    if menu == "Dashboard" and auth_system.has_permission(user_role, 'dashboard', 'can_view'):
        st.title("📊 Dashboard Principal")
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Ventas Hoy", "$2,845", "+15%")
        with col2:
            st.metric("Clientes Activos", "156", "+8%")
        with col3:
            st.metric("Órdenes Pendientes", "24", "-3%")
        with col4:
            st.metric("Inventario", "85%", "+2%")
        
        # Gráficos
        col1, col2 = st.columns(2)
        with col1:
            sales_data = pd.DataFrame({
                'Día': ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
                'Ventas': [1200, 1900, 1600, 2100, 2800, 3200, 2400],
                'Costos': [800, 1200, 1000, 1300, 1700, 1900, 1400]
            })
            fig = px.bar(sales_data, x='Día', y=['Ventas', 'Costos'], 
                        title='Ventas vs Costos - Esta Semana', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            category_data = pd.DataFrame({
                'Categoría': ['Producto A', 'Producto B', 'Producto C', 'Producto D'],
                'Valor': [850, 650, 450, 350]
            })
            fig = px.pie(category_data, values='Valor', names='Categoría', 
                        title='Distribución por Categoría')
            st.plotly_chart(fig, use_container_width=True)

    elif menu == "Importar Datos" and auth_system.has_permission(user_role, 'data_import', 'can_view'):
        render_data_import_module(conn)

    elif menu == "Finanzas" and auth_system.has_permission(user_role, 'finance', 'can_view'):
        render_finance_module(conn)

    elif menu == "CRM Clientes" and auth_system.has_permission(user_role, 'crm', 'can_view'):
        render_crm_module(conn)

    elif menu == "Recursos Humanos" and auth_system.has_permission(user_role, 'hr', 'can_view'):
        render_hr_module(conn)

    elif menu == "Inventario" and auth_system.has_permission(user_role, 'inventory', 'can_view'):
        render_inventory_module(conn, current_business)

    elif menu == "Administración" and auth_system.has_permission(user_role, 'admin', 'can_view'):
        st.title("⚙️ Administración del Sistema")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Eventos", "Notificaciones", "Configuración", "API"])
        
        with tab1:
            st.header("Eventos del Sistema")
            try:
                events = event_system.get_recent_events(limit=20)
                for event in events:
                    with st.expander(f"{event[0]} - {event[3]}"):
                        st.json(event[1])
            except:
                st.error("Error al cargar eventos")
        
        with tab2:
            st.header("Configuración de Notificaciones")
            st.write("Configuración de canales de notificación...")
        
        with tab3:
            st.header("Configuración del Sistema")
            st.write("Opciones de configuración avanzada...")
        
        with tab4:
            st.header("🌐 API REST del Sistema")
            st.success("API REST disponible para integraciones externas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Información de la API")
                st.write("""
                **URL Base:** `http://localhost:8000`
                **Versión:** 1.0.0
                **Estado:** ✅ Activa
                """)
                
            with col2:
                st.subheader("🔗 Acceso Rápido")
                if st.button("🩺 Ver Estado de la API", use_container_width=True):
                    try:
                        response = requests.get("http://localhost:8000/health", timeout=5)
                        if response.status_code == 200:
                            st.success(f"API saludable: {response.json()}")
                        else:
                            st.warning(f"API respondió con código: {response.status_code}")
                    except Exception as e:
                        st.error(f"No se pudo conectar a la API: {e}")

    elif menu == "Plugins" and auth_system.has_permission(user_role, 'admin', 'can_view'):
        st.title("🧩 Gestión de Plugins")
        st.info("Funcionalidad de plugins en desarrollo")

    elif menu == "Backups" and auth_system.has_permission(user_role, 'admin', 'can_view'):
        st.title("💾 Gestión de Backups")
        st.info("Funcionalidad de backups en desarrollo")

    elif menu == "Cerrar Sesión":
        try:
            event_system.publish(
                EventTypes.USER_LOGOUT,
                {"user_id": user_id, "username": user_name}, 
                user_id
            )
        except:
            pass
        
        st.session_state.auth_token = None
        st.session_state.user = None
        st.rerun()

except Exception as e:
    st.error(f"Error al cargar el módulo: {e}")

# Cerrar conexión al final
try:
    db.close_connection()
except:
    pass