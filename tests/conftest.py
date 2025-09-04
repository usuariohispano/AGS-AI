# sistema_pyme/tests/conftest.py
"""
Archivo de configuración de pytest - se ejecuta automáticamente antes de los tests
"""
import sys
import os
from pathlib import Path

# Obtener el directorio raíz del proyecto
project_root = Path(__file__).parent.parent
print(f"📍 Directorio raíz del proyecto: {project_root}")

# Añadir el directorio raíz al path de Python
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    print(f"✅ Añadido al sys.path: {project_root}")

# Verificar que los módulos existen
modules_to_check = ['auth.py', 'database.py']
for module in modules_to_check:
    module_path = project_root / module
    if module_path.exists():
        print(f"✅ Módulo encontrado: {module_path}")
    else:
        print(f"❌ Módulo no encontrado: {module_path}")

print(f"📋 Sys.path actual: {sys.path}")