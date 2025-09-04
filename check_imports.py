# sistema_pyme/check_imports.py
#!/usr/bin/env python3
"""
Script para verificar que todos los imports funcionan correctamente
"""
import sys
import os
from pathlib import Path

print("🔍 Verificando configuración de imports...")

# Mostrar el directorio actual
current_dir = Path(__file__).parent
print(f"📂 Directorio actual: {current_dir}")

# Mostrar sys.path
print("🗺️  Sys.path:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

# Verificar módulos críticos
modules_to_check = [
    ('auth', 'auth.py'),
    ('database', 'database.py'),
    ('modules.finance', 'modules/finance.py')
]

print("\n🔎 Verificando módulos:")
all_ok = True

for module_name, module_path in modules_to_check:
    try:
        # Verificar si el archivo existe físicamente
        physical_path = current_dir / module_path
        if physical_path.exists():
            print(f"✅ Archivo físico: {physical_path}")
        else:
            print(f"❌ Archivo no encontrado: {physical_path}")
            all_ok = False
            continue
        
        # Intentar importar
        if module_name == 'database':
            import database as db
            print(f"✅ Import exitoso: {module_name}")
        else:
            __import__(module_name)
            print(f"✅ Import exitoso: {module_name}")
            
    except ImportError as e:
        print(f"❌ Error importando {module_name}: {e}")
        all_ok = False
    except Exception as e:
        print(f"⚠️  Error inesperado con {module_name}: {e}")
        all_ok = False

if all_ok:
    print("\n🎉 ¡Todos los imports funcionan correctamente!")
else:
    print("\n❌ Algunos imports tienen problemas")
    sys.exit(1)