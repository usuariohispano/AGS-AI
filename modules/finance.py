import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3

def render_finance_module(conn):
    st.title("💰 Módulo Financiero")
    
    # KPIs Financieros
    st.header("📈 KPIs Financieros")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Flujo de Caja", "$20,000", "+15%")
    with col2:
        st.metric("Cuentas por Cobrar", "$14,700", "-8%")
    with col3:
        st.metric("Liquidez", "2.4", "+12%")
    with col4:
        st.metric("ROI", "18%", "+5%")
    
    # Gráfico de Flujo de Caja
    st.header("💸 Flujo de Caja")
    
    cash_flow_data = pd.DataFrame({
        'Mes': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        'Ingresos': [45000, 52000, 48000, 58000, 61000, 65000],
        'Gastos': [32000, 35000, 38000, 41000, 43000, 45000],
        'Flujo Neto': [13000, 17000, 10000, 17000, 18000, 20000]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=cash_flow_data['Mes'], y=cash_flow_data['Ingresos'],
                        name='Ingresos', marker_color='#10B981'))
    fig.add_trace(go.Bar(x=cash_flow_data['Mes'], y=cash_flow_data['Gastos'],
                        name='Gastos', marker_color='#EF4444'))
    fig.add_trace(go.Scatter(x=cash_flow_data['Mes'], y=cash_flow_data['Flujo Neto'],
                            name='Flujo Neto', line=dict(color='#3B82F6', width=3)))
    
    fig.update_layout(barmode='group', title='Flujo de Caja - Últimos 6 Meses')
    st.plotly_chart(fig, use_container_width=True)
    
    # Gestión de Cuentas por Cobrar
    st.header("📋 Cuentas por Cobrar")
    
    accounts_data = pd.DataFrame({
        'Cliente': ['Restaurante El Sabor', 'Ferretería Central', 
                   'Boutique Elegance', 'Supermercado Express'],
        'Monto': [4500, 2800, 1200, 6200],
        'Días Vencido': [15, -5, 32, -12],
        'Estado': ['Vencido', 'Por vencer', 'Crítico', 'Al día']
    })
    
    # Aplicar colores según estado
    color_map = {'Al día': 'green', 'Por vencer': 'orange', 
                'Vencido': 'red', 'Crítico': 'darkred'}
    accounts_data['Color'] = accounts_data['Estado'].map(color_map)
    
    fig = px.bar(accounts_data, x='Cliente', y='Monto', color='Estado',
                 color_discrete_map=color_map,
                 title='Cuentas por Cobrar por Estado')
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla detallada
    st.subheader("Detalle de Cuentas por Cobrar")
    st.dataframe(accounts_data)
    
    # Análisis de Liquidez
    st.header("📊 Análisis de Liquidez")
    
    liquidity_data = pd.DataFrame({
        'Ratio': ['Corriente', 'Prueba Ácida', 'Disponibilidad', 'Endeudamiento'],
        'Valor': [2.4, 1.8, 0.9, 0.6],
        'Recomendado': [2.0, 1.0, 0.2, 0.4]
    })
    
    fig = px.bar(liquidity_data, x='Ratio', y='Valor', 
                 title='Ratios de Liquidez', text='Valor')
    fig.add_scatter(x=liquidity_data['Ratio'], y=liquidity_data['Recomendado'],
                   mode='markers', marker=dict(color='red', size=10),
                   name='Recomendado')
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertas de Vencimientos
    st.header("🔔 Alertas de Vencimientos")
    
    for _, row in accounts_data.iterrows():
        if row['Días Vencido'] > 0:
            st.warning(f"⚠️ {row['Cliente']}: {row['Monto']} - {row['Días Vencido']} días vencidos")
            if st.button(f"Contactar {row['Cliente']}", key=row['Cliente']):
                st.success(f"Acción de contacto iniciada para {row['Cliente']}")