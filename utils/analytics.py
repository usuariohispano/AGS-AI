# sistema_pyme/utils/analytics.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AnalyticsEngine:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calcular ratios financieros clave"""
        ratios = {}
        
        try:
            # Ratio de liquidez corriente
            if 'current_assets' in financial_data and 'current_liabilities' in financial_data:
                ratios['liquidity_ratio'] = financial_data['current_assets'] / financial_data['current_liabilities']
            
            # Margen de beneficio neto
            if 'net_income' in financial_data and 'revenue' in financial_data and financial_data['revenue'] > 0:
                ratios['profit_margin'] = (financial_data['net_income'] / financial_data['revenue']) * 100
            
            # ROI (Return on Investment)
            if 'net_income' in financial_data and 'total_assets' in financial_data and financial_data['total_assets'] > 0:
                ratios['roi'] = (financial_data['net_income'] / financial_data['total_assets']) * 100
            
            # Ratio de endeudamiento
            if 'total_debt' in financial_data and 'total_assets' in financial_data and financial_data['total_assets'] > 0:
                ratios['debt_ratio'] = financial_data['total_debt'] / financial_data['total_assets']
            
            # Rotación de inventario
            if 'cogs' in financial_data and 'average_inventory' in financial_data and financial_data['average_inventory'] > 0:
                ratios['inventory_turnover'] = financial_data['cogs'] / financial_data['average_inventory']
                
        except ZeroDivisionError:
            pass
        
        return ratios
    
    def forecast_sales(self, sales_data: pd.DataFrame, periods: int = 6) -> Dict[str, Any]:
        """Predecir ventas futuras usando promedio móvil simple"""
        try:
            if len(sales_data) < 2:
                return {"error": "Se necesitan al menos 2 puntos de datos para forecasting"}
            
            # Usar promedio móvil simple de 3 periodos
            sales_series = sales_data['sales']
            forecast = []
            
            for i in range(periods):
                last_values = sales_series[-3:] if len(sales_series) >= 3 else sales_series
                next_value = last_values.mean()
                forecast.append(next_value)
                sales_series = pd.concat([sales_series, pd.Series([next_value])])
            
            return {
                "forecast": forecast,
                "method": "moving_average",
                "periods": periods,
                "last_actual_value": sales_data['sales'].iloc[-1] if len(sales_data) > 0 else None
            }
            
        except Exception as e:
            return {"error": f"Error en forecasting: {str(e)}"}
    
    def segment_customers(self, customers_data: pd.DataFrame, n_clusters: int = 3) -> Dict[str, Any]:
        """Segmentar clientes usando K-Means clustering"""
        try:
            # Seleccionar características para clustering
            features = customers_data[['total_spent', 'purchase_frequency', 'last_purchase_days']].copy()
            features = features.dropna()
            
            if len(features) < n_clusters:
                return {"error": f"Se necesitan al menos {n_clusters} clientes para segmentación"}
            
            # Estandarizar características
            scaled_features = self.scaler.fit_transform(features)
            
            # Aplicar K-Means
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(scaled_features)
            
            # Añadir clusters al DataFrame original
            customers_segmented = customers_data.copy()
            customers_segmented = customers_segmented.loc[features.index]
            customers_segmented['cluster'] = clusters
            
            # Analizar clusters
            cluster_analysis = {}
            for cluster_id in range(n_clusters):
                cluster_data = customers_segmented[customers_segmented['cluster'] == cluster_id]
                cluster_analysis[cluster_id] = {
                    "size": len(cluster_data),
                    "avg_spent": cluster_data['total_spent'].mean(),
                    "avg_frequency": cluster_data['purchase_frequency'].mean(),
                    "avg_recency": cluster_data['last_purchase_days'].mean()
                }
            
            return {
                "success": True,
                "n_clusters": n_clusters,
                "clusters": cluster_analysis,
                "customers_segmented": customers_segmented.to_dict('records')
            }
            
        except Exception as e:
            return {"error": f"Error en segmentación: {str(e)}"}
    
    def detect_seasonality(self, time_series: pd.Series) -> Dict[str, Any]:
        """Detectar patrones estacionales en series temporales"""
        try:
            if len(time_series) < 12:  # Mínimo 12 puntos para análisis estacional
                return {"error": "Se necesitan al menos 12 puntos de datos"}
            
            # Análisis de autocorrelación simple
            autocorr = []
            for lag in range(1, 13):  # Lags de 1 a 12 meses
                if lag < len(time_series):
                    corr = time_series.autocorr(lag=lag)
                    autocorr.append({"lag": lag, "correlation": corr})
            
            # Encontrar lag con mayor autocorrelación
            significant_lags = [ac for ac in autocorr if abs(ac['correlation']) > 0.5]
            
            return {
                "autocorrelation": autocorr,
                "significant_lags": significant_lags,
                "has_seasonality": len(significant_lags) > 0
            }
            
        except Exception as e:
            return {"error": f"Error en detección de estacionalidad: {str(e)}"}
    
    def calculate_customer_lifetime_value(self, customers_data: pd.DataFrame) -> pd.DataFrame:
        """Calcular Customer Lifetime Value (LTV)"""
        try:
            df = customers_data.copy()
            
            # Fórmula simple de LTV: Valor promedio por compra × Frecuencia de compra × Vida útil del cliente
            df['ltv'] = df['avg_purchase_value'] * df['purchase_frequency'] * df['expected_lifetime']
            
            # Clasificar clientes por LTV
            df['ltv_segment'] = pd.qcut(df['ltv'], q=4, labels=['Bajo', 'Medio', 'Alto', 'VIP'])
            
            return df
            
        except Exception as e:
            print(f"Error calculando LTV: {e}")
            return customers_data

# Instancia global para uso fácil
analytics_engine = AnalyticsEngine()