import streamlit as st
from streamlit.components.v1 import html
import json

class ResponsiveDesign:
    @staticmethod
    def init_responsive():
        """Inicializar configuración responsive"""
        st.set_page_config(
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items=None
        )
        
        # Inject CSS for responsive design
        st.markdown("""
        <style>
        /* Responsive design */
        @media (max-width: 768px) {
            .main .block-container {
                padding: 1rem;
            }
            
            .stButton > button {
                width: 100%;
                margin: 0.25rem 0;
            }
            
            .stDataFrame {
                font-size: 12px;
            }
            
            .metric-card {
                padding: 0.5rem;
                margin: 0.25rem 0;
            }
            
            /* Hide sidebar on mobile */
            section[data-testid="stSidebar"] {
                display: none;
            }
            
            /* Mobile navigation bar */
            .mobile-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid #ddd;
                z-index: 1000;
                display: flex;
                justify-content: space-around;
                padding: 0.5rem;
            }
            
            .mobile-nav button {
                flex: 1;
                margin: 0 0.25rem;
                font-size: 0.8rem;
            }
        }
        
        @media (min-width: 769px) {
            .mobile-nav {
                display: none;
            }
        }
        
        /* General responsive adjustments */
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }
        
        .responsive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def mobile_navigation():
        """Barra de navegación móvil"""
        nav_html = """
        <div class="mobile-nav">
            <button onclick="navigate('Dashboard')">📊 Dashboard</button>
            <button onclick="navigate('Ventas')">💰 Ventas</button>
            <button onclick="navigate('Inventario')">📦 Inventario</button>
            <button onclick="navigate('Config')">⚙️ Config</button>
        </div>
        
        <script>
        function navigate(section) {
            window.parent.document.querySelectorAll('.stButton button')
                .forEach(btn => {
                    if (btn.textContent.includes(section)) {
                        btn.click();
                    }
                });
        }
        
        // Detect mobile device
        function isMobile() {
            return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        }
        
        if (isMobile()) {
            document.addEventListener('DOMContentLoaded', function() {
                // Add mobile-specific behaviors
            });
        }
        </script>
        """
        html(nav_html, height=60)
    
    @staticmethod
    def responsive_grid(items_per_row=2):
        """Crear grid responsive"""
        return st.columns(items_per_row)
    
    @staticmethod
    def metric_card(title, value, delta=None, help_text=None):
        """Tarjeta de métrica responsive"""
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(title)
            if help_text:
                st.caption(help_text)
        with col2:
            st.metric("", value, delta)
    
    @staticmethod
    def mobile_friendly_table(dataframe, key=None):
        """Tabla optimizada para móviles"""
        return st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
            column_config={
                col: st.column_config.Column(
                    width="small" if dataframe[col].dtype == 'object' else "medium"
                ) for col in dataframe.columns
            }
        )
    
    @staticmethod
    def responsive_plot(fig, height=400):
        """Gráfico responsive"""
        fig.update_layout(
            autosize=True,
            height=height,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        return st.plotly_chart(fig, use_container_width=True)

def detect_mobile():
    """Detectar si es dispositivo móvil"""
    try:
        user_agent = st.query_params.get('user_agent', '')
        mobile_keywords = ['Mobile', 'Android', 'iPhone', 'iPad', 'iPod']
        return any(keyword in user_agent for keyword in mobile_keywords)
    except:
        return False