# sistema_pyme/run_api.py
# ✅ Importar directamente desde el módulo donde está definido app
from api.api_main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )