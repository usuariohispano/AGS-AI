import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3

def render_hr_module(conn):
    st.title("👥 Recursos Humanos")
    
    # KPIs de RRHH
    st.header("📊 KPIs de RRHH")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Empleados Activos", "24", "+4%")
    with col2:
        st.metric("Nómina Mensual", "$28,750", "+8%")
    with col3:
        st.metric("Evaluación Promedio", "4.5/5", "+12%")
    with col4:
        st.metric("Rotación Anual", "8%", "-15%")
    
    # Estructura Organizacional
    st.header("🏢 Estructura Organizacional")
    
    org_data = pd.DataFrame({
        'Departamento': ['Ventas', 'Finanzas', 'Operaciones', 'Soporte'],
        'Empleados': [8, 4, 7, 5],
        'Color': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
    })
    
    fig = px.pie(org_data, values='Empleados', names='Departamento',
                title='Distribución por Departamento')
    st.plotly_chart(fig, use_container_width=True)
    
    # Directorio de Empleados
    st.header("📋 Directorio de Empleados")
    
    employees_data = pd.DataFrame({
        'Nombre': ['Juan Pérez', 'Laura Martínez', 'Carlos Rodríguez', 'Ana García'],
        'Cargo': ['Gerente de Ventas', 'Asistente Contable', 'Supervisor de Inventario', 'Ejecutiva de Ventas'],
        'Departamento': ['Ventas', 'Finanzas', 'Operaciones', 'Ventas'],
        'Salario': [1200, 850, 950, 750],
        'Fecha Ingreso': ['2023-01-15', '2023-06-10', '2022-11-20', '2024-02-15'],
        'Evaluación': [4.8, 4.5, 4.2, 4.9],
        'Vacaciones': [12, 8, 5, 18]
    })
    
    st.dataframe(employees_data)
    
    # Control de Nómina
    st.header("💰 Control de Nómina")
    
    payroll_data = pd.DataFrame({
        'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        'Nómina Bruta': [25000, 25500, 26000, 26500, 27000, 27500],
        'Deducciones': [5000, 5100, 5200, 5300, 5400, 5500],
        'Nómina Neta': [20000, 20400, 20800, 21200, 21600, 22000]
    })
    
    fig = px.line(payroll_data, x='Mes', y=['Nómina Bruta', 'Nómina Neta'],
                 title='Evolución de Nómina')
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertas de RRHH
    st.header("🔔 Alertas de RRHH")
    
    alerts = [
        {"tipo": "Evaluación", "mensaje": "3 evaluaciones de desempeño pendientes", "prioridad": "alta"},
        {"tipo": "Vacaciones", "mensaje": "Juan Pérez tiene 12 días de vacaciones pendientes", "prioridad": "media"},
        {"tipo": "Aniversario", "mensaje": "Ana García cumple 1 año la próxima semana", "prioridad": "baja"}
    ]
    
    for alert in alerts:
        priority_color = "🔴" if alert["prioridad"] == "alta" else "🟡" if alert["prioridad"] == "media" else "🟢"
        st.write(f"{priority_color} **{alert['tipo']}:** {alert['mensaje']}")