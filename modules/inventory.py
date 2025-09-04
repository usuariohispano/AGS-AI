import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3

def render_inventory_module(conn, current_business):
    st.title("📦 Gestión de Inventario")
    
    # KPIs de Inventario
    st.header("📊 KPIs de Inventario")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Productos", "156", "+12%")
    with col2:
        st.metric("Rotación Mensual", "2.4x", "+8%")
    with col3:
        st.metric("Stock Bajo", "8", "+5%")
    with col4:
        st.metric("Stock Muerto", "5", "-15%")
    
    # Control de Inventario adaptado al tipo de negocio
    st.header(f"📋 Control de Inventario - {current_business['type'] if current_business else 'Negocio'}")
    
    # Datos de ejemplo según tipo de negocio
    if current_business and current_business['type'] == 'Panadería':
        inventory_data = pd.DataFrame({
            'Producto': ['Pan Blanco', 'Pan Integral', 'Pasteles', 'Bebidas'],
            'Categoría': ['Pan', 'Pan', 'Pastelería', 'Bebidas'],
            'Stock Actual': [45, 32, 18, 56],
            'Stock Mínimo': [20, 25, 15, 30],
            'Estado': ['Ok', 'Ok', 'Bajo', 'Ok']
        })
    elif current_business and current_business['type'] == 'Restaurante':
        inventory_data = pd.DataFrame({
            'Producto': ['Carne', 'Pollo', 'Verduras', 'Bebidas'],
            'Categoría': ['Proteínas', 'Proteínas', 'Vegetales', 'Bebidas'],
            'Stock Actual': [25, 35, 45, 60],
            'Stock Mínimo': [30, 40, 20, 50],
            'Estado': ['Bajo', 'Bajo', 'Ok', 'Ok']
        })
    else:
        inventory_data = pd.DataFrame({
            'Producto': ['Producto A', 'Producto B', 'Producto C', 'Producto D'],
            'Categoría': ['Categoría 1', 'Categoría 1', 'Categoría 2', 'Categoría 2'],
            'Stock Actual': [100, 75, 50, 25],
            'Stock Mínimo': [50, 40, 30, 20],
            'Estado': ['Ok', 'Ok', 'Bajo', 'Ok']
        })
    
    # Aplicar colores según estado
    color_map = {'Ok': 'green', 'Bajo': 'orange', 'Crítico': 'red'}
    inventory_data['Color'] = inventory_data['Estado'].map(color_map)
    
    # Mostrar tabla de inventario
    st.dataframe(inventory_data)
    
    # Gráfico de estado de inventario
    st.header("📊 Estado del Inventario")
    
    status_counts = inventory_data['Estado'].value_counts().reset_index()
    status_counts.columns = ['Estado', 'Cantidad']
    
    fig = px.pie(status_counts, values='Cantidad', names='Estado',
                color='Estado', color_discrete_map=color_map,
                title='Distribución por Estado de Inventario')
    st.plotly_chart(fig, use_container_width=True)
    
    # Acciones de inventario
    st.header("⚡ Acciones de Inventario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Actualizar Stock")
        product_to_update = st.selectbox("Seleccionar producto", inventory_data['Producto'])
        new_stock = st.number_input("Nuevo stock", min_value=0, value=0)
        
        if st.button("Actualizar Stock"):
            st.success(f"Stock de {product_to_update} actualizado a {new_stock}")
    
    with col2:
        st.subheader("Reabastecer")
        product_to_restock = st.selectbox("Seleccionar producto para reabastecer", 
                                         inventory_data[inventory_data['Estado'] != 'Ok']['Producto'])
        restock_quantity = st.number_input("Cantidad a reabastecer", min_value=1, value=10)
        
        if st.button("Solicitar Reabastecimiento"):
            st.success(f"Orden de reabastecimiento para {product_to_restock} creada")
    
    # Alertas de inventario
    st.header("🔔 Alertas de Inventario")
    
    for _, product in inventory_data.iterrows():
        if product['Estado'] == 'Bajo':
            st.warning(f"⚠️ {product['Producto']}: Stock bajo ({product['Stock Actual']}/{product['Stock Mínimo']})")
        elif product['Estado'] == 'Crítico':
            st.error(f"🚨 {product['Producto']}: Stock crítico ({product['Stock Actual']}/{product['Stock Mínimo']})")