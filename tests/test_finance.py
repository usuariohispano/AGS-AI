# sistema_pyme/tests/test_finance.py
import pytest

# Los imports ahora funcionarán gracias a conftest.py
from modules.finance import calculate_financial_ratios, generate_cash_flow_forecast

def test_financial_ratios_calculation():
    """Test de cálculo de ratios financieros"""
    # Datos de prueba
    test_data = {
        'income': [50000, 55000, 60000],
        'expenses': [40000, 42000, 45000],
        'assets': [100000, 110000, 120000],
        'liabilities': [60000, 65000, 70000]
    }
    
    ratios = calculate_financial_ratios(test_data)
    
    # Verificar que se calculan todos los ratios
    assert 'liquidity_ratio' in ratios
    assert 'profit_margin' in ratios
    assert 'roi' in ratios
    assert 'debt_ratio' in ratios
    
    # Verificar que los ratios son valores numéricos razonables
    assert ratios['liquidity_ratio'] > 0
    assert 0 <= ratios['profit_margin'] <= 1
    assert ratios['roi'] > 0

def test_cash_flow_forecast():
    """Test de forecast de flujo de caja"""
    historical_data = {
        'months': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        'income': [50000, 55000, 60000, 65000, 70000, 75000],
        'expenses': [40000, 42000, 45000, 47000, 50000, 52000]
    }
    
    forecast = generate_cash_flow_forecast(historical_data, periods=3)
    
    # Verificar que se genera forecast
    assert 'forecast_months' in forecast
    assert 'forecast_income' in forecast
    assert 'forecast_expenses' in forecast
    assert 'forecast_cash_flow' in forecast
    
    # Verificar longitud del forecast
    assert len(forecast['forecast_months']) == 3
    assert len(forecast['forecast_income']) == 3
    assert len(forecast['forecast_expenses']) == 3
    assert len(forecast['forecast_cash_flow']) == 3