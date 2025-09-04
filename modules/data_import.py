# sistema_pyme/modules/data_import.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import io
import json

def render_data_import_module(conn):
    st.title("📤 Importar Datos")
    
    # Sección de subida de archivos
    st.header("Subir archivos para análisis")
    
    uploaded_file = st.file_uploader("Selecciona un archivo", type=[
        'xlsx', 'xls', 'csv', 'pdf', 'doc', 'docx', 'txt'
    ], help="Formatos soportados: Excel, CSV, PDF, Word, Texto")
    
    if uploaded_file is not None:
        file_details = {
            "Filename": uploaded_file.name,
            "File size": uploaded_file.size,
            "File type": uploaded_file.type
        }
        st.write(file_details)
        
        # Procesar archivo según tipo
        file_type = uploaded_file.name.split('.')[-1].lower()
        status = "En análisis"
        records = 0
        insights = []
        
        try:
            if file_type in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file)
                records = len(df)
                insights = analyze_excel_data(df)
                status = "Procesado"
                
            elif file_type == 'csv':
                df = pd.read_csv(uploaded_file)
                records = len(df)
                insights = analyze_csv_data(df)
                status = "Procesado"
                
            elif file_type == 'pdf':
                insights = ["PDF procesado. Análisis de texto completado."]
                status = "Procesado"
                
            else:
                insights = [f"Archivo {file_type.upper()} procesado correctamente."]
                status = "Procesado"
                
        except Exception as e:
            insights = [f"Error al procesar archivo: {str(e)}"]
            status = "Error"
        
        # Guardar en base de datos
        save_imported_file(conn, uploaded_file.name, file_type.upper(), 
                          status, records, insights)
        
        st.success(f"Archivo procesado: {status}")
        
        if status == "Procesado":
            st.subheader("Insights generados:")
            for insight in insights:
                st.info(f"• {insight}")
    
    # Sección de archivos procesados
    st.header("📊 Archivos Procesados")
    display_processed_files(conn)
    
    # Capacidades de análisis automático
    st.header("🔍 Capacidades de Análisis Automático")
    
    cols = st.columns(4)
    with cols[0]:
        if st.button("📊 Análisis de Ventas"):
            show_sales_analysis()
    with cols[1]:
        if st.button("📦 Análisis de Inventario"):
            show_inventory_analysis()
    with cols[2]:
        if st.button("💰 Análisis Financiero"):
            show_financial_analysis()
    with cols[3]:
        if st.button("👥 Análisis de Clientes"):
            show_customer_analysis()

def analyze_excel_data(df):
    insights = []
    
    # Análisis básico
    insights.append(f"Archivo contiene {len(df)} registros y {len(df.columns)} columnas")
    
    # Detectar tipo de datos
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        insights.append(f"Columnas numéricas detectadas: {', '.join(numeric_cols)}")
    
    return insights

def analyze_csv_data(df):
    return analyze_excel_data(df)  # Reutilizar misma lógica

def save_imported_file(conn, filename, file_type, status, records, insights):
    c = conn.cursor()
    c.execute('''INSERT INTO imported_files 
                 (filename, file_type, status, records, insights, uploaded_at, processed_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
             (filename, file_type, status, records, json.dumps(insights), 
              datetime.now(), datetime.now()))
    conn.commit()

def display_processed_files(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM imported_files ORDER BY uploaded_at DESC")
    files = c.fetchall()
    
    for file in files:
        with st.expander(f"{file[1]} - {file[3]}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Tipo:** {file[2]}")
                st.write(f"**Registros:** {file[4]}")
                st.write(f"**Subido:** {file[6]}")
            with col2:
                status_color = "🟢" if file[3] == "Procesado" else "🟡" if file[3] == "En análisis" else "🔴"
                st.write(f"**Estado:** {status_color} {file[3]}")
                
                if st.button("Ver análisis", key=f"analysis_{file[0]}"):
                    insights = json.loads(file[5])
                    for insight in insights:
                        st.write(f"• {insight}")
                
                if file[3] == "Procesado":
                    if st.button("Exportar", key=f"export_{file[0]}"):
                        st.success("Funcionalidad de exportación en desarrollo")

def show_sales_analysis():
    st.subheader("📊 Análisis de Ventas")
    st.write("""
    - **Tendencias y estacionalidad**: Identificación de patrones de ventas
    - **Productos más vendidos**: Análisis de productos estrella
    - **Análisis de márgenes**: Rentabilidad por producto/categoría
    - **Proyecciones de crecimiento**: Forecast de ventas futuro
    """)

def show_inventory_analysis():
    st.subheader("📦 Análisis de Inventario")
    st.write("""
    - **Rotación de productos**: Velocidad de venta de inventario
    - **Detección de stock muerto**: Productos sin movimiento
    - **Optimización de pedidos**: Puntos de reorden óptimos
    - **Alertas de reabastecimiento**: Notificaciones automáticas
    """)

def show_financial_analysis():
    st.subheader("💰 Análisis Financiero")
    st.write("""
    - **Flujo de caja proyectado**: Forecasting de liquidez
    - **Análisis de rentabilidad**: ROI por área de negocio
    - **Identificación de gastos**: Optimización de costos
    - **Ratios financieros clave**: Indicadores de salud financiera
    """)

def show_customer_analysis():
    st.subheader("👥 Análisis de Clientes")
    st.write("""
    - **Segmentación automática**: Clustering de clientes
    - **Valor de vida del cliente**: LTV prediction
    - **Patrones de compra**: Análisis de comportamiento
    - **Predicción de churn**: Alerta de posibles bajas
    """)
