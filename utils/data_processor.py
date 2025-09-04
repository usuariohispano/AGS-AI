# sistema_pyme/utils/data_processor.py
import pandas as pd
import numpy as np
from datetime import datetime
import json
from typing import Dict, List, Any, Optional
import re

class DataProcessor:
    def __init__(self):
        self.supported_formats = ['csv', 'xlsx', 'xls', 'json']
    
    def detect_file_type(self, file_path: str) -> str:
        """Detectar el tipo de archivo basado en la extensión"""
        if file_path.endswith('.csv'):
            return 'csv'
        elif file_path.endswith('.xlsx'):
            return 'xlsx'
        elif file_path.endswith('.xls'):
            return 'xls'
        elif file_path.endswith('.json'):
            return 'json'
        else:
            raise ValueError(f"Formato no soportado: {file_path}")
    
    def read_file(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Leer archivo según su formato"""
        file_type = self.detect_file_type(file_path)
        
        try:
            if file_type == 'csv':
                return pd.read_csv(file_path, **kwargs)
            elif file_type in ['xlsx', 'xls']:
                return pd.read_excel(file_path, **kwargs)
            elif file_type == 'json':
                return pd.read_json(file_path, **kwargs)
        except Exception as e:
            raise ValueError(f"Error leyendo archivo {file_path}: {str(e)}")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpiar y preprocesar datos"""
        # Hacer una copia para no modificar el original
        df_clean = df.copy()
        
        # Eliminar filas completamente vacías
        df_clean = df_clean.dropna(how='all')
        
        # Eliminar duplicados
        df_clean = df_clean.drop_duplicates()
        
        # Limpiar nombres de columnas
        df_clean.columns = [self.clean_column_name(col) for col in df_clean.columns]
        
        # Inferir tipos de datos
        df_clean = self.infer_data_types(df_clean)
        
        return df_clean
    
    def clean_column_name(self, column_name: str) -> str:
        """Limpiar nombre de columna"""
        if pd.isna(column_name):
            return 'unknown_column'
        
        # Convertir a string si no lo es
        col_str = str(column_name)
        
        # Reemplazar caracteres especiales y espacios
        col_clean = re.sub(r'[^\w]', '_', col_str.lower().strip())
        
        # Reemplazar múltiples underscores por uno solo
        col_clean = re.sub(r'_+', '_', col_clean)
        
        # Eliminar underscores al inicio y final
        col_clean = col_clean.strip('_')
        
        return col_clean if col_clean else 'unknown_column'
    
    def infer_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Inferir tipos de datos automáticamente"""
        for col in df.columns:
            # Intentar convertir a numérico
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
            
            # Intentar convertir a fecha
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
        
        return df
    
    def detect_anomalies(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Detectar anomalías en una columna numérica"""
        if not pd.api.types.is_numeric_dtype(df[column]):
            return {"error": "La columna debe ser numérica"}
        
        values = df[column].dropna()
        
        if len(values) == 0:
            return {"error": "No hay datos válidos en la columna"}
        
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = values[(values < lower_bound) | (values > upper_bound)]
        
        return {
            "total_values": len(values),
            "anomalies_count": len(anomalies),
            "anomalies_percentage": (len(anomalies) / len(values)) * 100,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "anomalies": anomalies.tolist()
        }
    
    def generate_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generar perfil completo de los datos"""
        profile = {
            "general": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "missing_values": df.isnull().sum().sum(),
                "missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                "duplicate_rows": df.duplicated().sum()
            },
            "columns": {},
            "data_types": {}
        }
        
        # Información por columna
        for col in df.columns:
            profile["columns"][col] = {
                "data_type": str(df[col].dtype),
                "missing_values": df[col].isnull().sum(),
                "missing_percentage": (df[col].isnull().sum() / len(df)) * 100,
                "unique_values": df[col].nunique() if df[col].dtype == 'object' else None,
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                profile["columns"][col].update({
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std()
                })
        
        # Distribución de tipos de datos
        dtype_counts = df.dtypes.value_counts().to_dict()
        profile["data_types"] = {str(k): int(v) for k, v in dtype_counts.items()}
        
        return profile

# Instancia global para uso fácil
data_processor = DataProcessor()