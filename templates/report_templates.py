# sistema_pyme/utils/report_templates.py
from jinja2 import Template
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Dict, Any, Optional
import base64
from io import BytesIO

class ReportTemplateSystem:
    def __init__(self, templates_dir: str = "templates/reports"):
        self.templates_dir = templates_dir
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Cargar plantillas de reportes desde el directorio"""
        templates = {}
        # Aquí iría la lógica para cargar plantillas desde archivos
        return templates
    
    def generate_sales_report(self, sales_data: pd.DataFrame, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generar reporte de ventas con análisis y gráficos"""
        try:
            # Análisis básico de ventas
            total_sales = sales_data['amount'].sum()
            avg_sale = sales_data['amount'].mean()
            total_quantity = sales_data['quantity'].sum()
            
            # Productos más vendidos
            top_products = sales_data.groupby('product').agg({
                'quantity': 'sum',
                'amount': 'sum'
            }).sort_values('amount', ascending=False).head(5)
            
            # Gráfico de ventas por día
            sales_by_day = sales_data.groupby('date')['amount'].sum().reset_index()
            fig_daily = px.line(sales_by_day, x='date', y='amount', 
                               title='Ventas por Día', labels={'amount': 'Ventas ($)', 'date': 'Fecha'})
            
            # Gráfico de productos más vendidos
            fig_products = px.bar(top_products.reset_index(), x='product', y='amount',
                                 title='Productos Más Vendidos por Valor',
                                 labels={'amount': 'Ventas ($)', 'product': 'Producto'})
            
            # Convertir gráficos a HTML
            chart_daily_html = fig_daily.to_html(include_plotlyjs='cdn')
            chart_products_html = fig_products.to_html(include_plotlyjs=False)
            
            return {
                'success': True,
                'report_data': {
                    'periodo': f'{start_date} a {end_date}',
                    'total_ventas': total_sales,
                    'venta_promedio': avg_sale,
                    'cantidad_total': total_quantity,
                    'productos_top': top_products.to_dict('records'),
                    'chart_daily': chart_daily_html,
                    'chart_products': chart_products_html,
                    'generado_el': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generando reporte: {str(e)}'
            }
    
    def generate_financial_report(self, financial_data: pd.DataFrame) -> Dict[str, Any]:
        """Generar reporte financiero"""
        try:
            # Análisis financiero básico
            total_income = financial_data['income'].sum()
            total_expenses = financial_data['expenses'].sum()
            net_profit = total_income - total_expenses
            profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
            
            # Gráfico de ingresos vs gastos
            fig_financial = px.line(financial_data, x='month', y=['income', 'expenses'],
                                   title='Ingresos vs Gastos',
                                   labels={'value': 'Monto ($)', 'month': 'Mes', 'variable': 'Tipo'})
            
            chart_financial_html = fig_financial.to_html(include_plotlyjs='cdn')
            
            return {
                'success': True,
                'report_data': {
                    'ingresos_totales': total_income,
                    'gastos_totales': total_expenses,
                    'ganancia_neta': net_profit,
                    'margen_ganancia': profit_margin,
                    'chart_financial': chart_financial_html,
                    'generado_el': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error generando reporte financiero: {str(e)}'
            }

# Plantillas predefinidas para reportes
SALES_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Reporte de Ventas - {{ business_name }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 30px; }
        .section { margin-bottom: 20px; }
        .metric { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .chart { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Reporte de Ventas</h1>
        <h2>{{ business_name }}</h2>
        <p>Período: {{ periodo }}</p>
        <p>Generado el: {{ generado_el }}</p>
    </div>
    
    <div class="section">
        <h3>Métricas Principales</h3>
        <div class="metric">
            <strong>Ventas Totales:</strong> ${{ total_ventas | round(2) }}
        </div>
        <div class="metric">
            <strong>Venta Promedio:</strong> ${{ venta_promedio | round(2) }}
        </div>
        <div class="metric">
            <strong>Cantidad Total Vendida:</strong> {{ cantidad_total }}
        </div>
    </div>
    
    <div class="chart">
        {{ chart_daily | safe }}
    </div>
    
    <div class="chart">
        {{ chart_products | safe }}
    </div>
    
    <div class="section">
        <h3>Productos Más Vendidos</h3>
        <table border="1" style="width:100%; border-collapse: collapse;">
            <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Ventas</th>
            </tr>
            {% for product in productos_top %}
            <tr>
                <td>{{ product.product }}</td>
                <td>{{ product.quantity }}</td>
                <td>${{ product.amount | round(2) }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""