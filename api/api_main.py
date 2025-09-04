# sistema_pyme/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import importlib

# ✅ Definir app en el ámbito global del módulo
app = FastAPI(title="Sistema PYME API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes (ajustar en producción)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los headers
)

# Importar y configurar routers dinámicamente para evitar errores de importación
try:
    # Intentar importar el router de endpoints
    from api.api_endpoints import router as api_router
    app.include_router(api_router, prefix="/api/v1", tags=["api"])
    print("✅ Router de endpoints cargado correctamente")
except ImportError as e:
    print(f"⚠️ Error cargando endpoints: {e}")
    # Crear un router vacío para que la API no falle completamente
    from fastapi import APIRouter
    fallback_router = APIRouter()
    
    @fallback_router.get("/")
    async def fallback_root():
        return {"message": "API funcionando pero endpoints no disponibles", "error": str(e)}
    
    app.include_router(fallback_router, prefix="/api/v1", tags=["api"])

@app.get("/")
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": "Sistema PYME API", 
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": True
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "Sistema PYME API",
        "version": "1.0.0"
    }

@app.get("/info")
async def api_info():
    """Información detallada de la API"""
    return {
        "name": "Sistema PYME API",
        "version": "1.0.0",
        "description": "API REST para el Sistema de Gestión PYME",
        "documentation": "/docs",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "info": "/info",
            "api_v1": "/api/v1",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# ✅ Exportar explícitamente para que otros módulos puedan importar
__all__ = ['app']