import streamlit as st
import pandas as pd
import plotly.express as px
from utils.web_scraper import scrape_potential_leads
import sqlite3

def render_crm_module(conn):
    st.title("👥 CRM Clientes")
    
    # KPIs de CRM
    st.header("📊 KPIs de CRM")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clientes", "247", "+8%")
    with col2:
        st.metric("Clientes VIP", "23", "+15%")
    with col3:
        st.metric("Ticket Promedio", "$185", "+12%")
    with col4:
        st.metric("Satisfacción", "4.6/5", "+3%")
    
    # Segmentación de Clientes
    st.header("🎯 Segmentación de Clientes")
    
    segmentation_data = pd.DataFrame({
        'Segmento': ['Premium', 'Regular', 'Básico'],
        'Clientes': [23, 154, 70],
        'Color': ['#8B5CF6', '#3B82F6', '#10B981']
    })
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(segmentation_data, values='Clientes', names='Segmento',
                    title='Distribución por Segmento')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(segmentation_data, x='Segmento', y='Clientes', color='Segmento',
                    color_discrete_map={'Premium': '#8B5CF6', 'Regular': '#3B82F6', 'Básico': '#10B981'},
                    title='Clientes por Segmento')
        st.plotly_chart(fig, use_container_width=True)
    
    # Base de Clientes
    st.header("📋 Base de Clientes")
    
    customers_data = pd.DataFrame({
        'Nombre': ['María González', 'Carlos Mendoza', 'Ana Rodríguez', 'Roberto Sánchez'],
        'Empresa': ['Restaurante El Sabor', 'Ferretería Central', 
                   'Boutique Elegance', 'Supermercado Express'],
        'Email': ['maria@elsabor.com', 'carlos@ferreteria.com',
                 'ana@boutique.com', 'roberto@superexpress.com'],
        'Estado': ['VIP', 'Activo', 'Inactivo', 'VIP'],
        'Valor Total': [15400, 8900, 24500, 5600],
        'Última Compra': ['2025-08-20', '2025-08-18', '2025-08-15', '2025-08-10']
    })
    
    st.dataframe(customers_data)
    
    # Web Scraping para Leads
    st.header("🔍 Búsqueda de Leads Potenciales")
    
    if st.button("Buscar Leads Potenciales"):
        with st.spinner("Buscando leads potenciales..."):
            leads = scrape_potential_leads()
            if leads:
                st.success(f"Encontrados {len(leads)} leads potenciales")
                
                for lead in leads:
                    with st.expander(f"{lead['nombre']} - {lead['empresa']}"):
                        st.write(f"**Teléfono:** {lead['telefono']}")
                        st.write(f"**Email:** {lead['email']}")
                        st.write(f"**Fuente:** {lead['fuente']}")
                        st.write(f"**Notas:** {lead['notas']}")
                        
                        if st.button("Agregar como cliente", key=lead['email']):
                            # Guardar en base de datos
                            save_customer(conn, lead)
                            st.success("Cliente agregado exitosamente")
            else:
                st.warning("No se encontraron leads. Intenta con otros parámetros.")

def save_customer(conn, customer_data):
    c = conn.cursor()
    c.execute('''INSERT INTO customers 
                 (name, company, email, phone, status, segment, value, last_purchase, notes)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
             (customer_data['nombre'], customer_data['empresa'], customer_data['email'],
              customer_data['telefono'], 'Potencial', 'Por segmentar', 0,
              datetime.now().strftime('%Y-%m-%d'), customer_data['notas']))
    conn.commit()