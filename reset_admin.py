# reset_admin.py
import sqlite3
import bcrypt
from datetime import datetime
import os

def reset_admin():
    """Resetear completamente el usuario admin"""
    
    # Asegurarse que la carpeta data existe
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/sistema_pyme.db')
    c = conn.cursor()
    
    # Crear tabla de usuarios si no existe
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                 email TEXT UNIQUE, password_hash TEXT, role TEXT,
                 is_active INTEGER, created_at TIMESTAMP,
                 last_login TIMESTAMP, two_factor_secret TEXT)''')
    
    # Crear tabla de permisos
    c.execute('''CREATE TABLE IF NOT EXISTS permissions
                (id INTEGER PRIMARY KEY, role TEXT, module TEXT,
                 can_view INTEGER, can_edit INTEGER, can_delete INTEGER)''')
    
    # Eliminar usuario admin existente
    c.execute("DELETE FROM users WHERE username = 'admin'")
    
    # Crear nuevo usuario admin SIN 2FA
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    c.execute('''INSERT INTO users 
                (username, email, password_hash, role, is_active, 
                 created_at, two_factor_secret)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
             ('admin', 'admin@sistema.pyme', password_hash, 'admin', 1,
              datetime.now(), None))  # two_factor_secret = None
    
    # Configurar permisos completos para admin
    modules = ['dashboard', 'data_import', 'finance', 'crm', 'hr', 'inventory', 'admin']
    for module in modules:
        c.execute('''INSERT OR REPLACE INTO permissions 
                    (role, module, can_view, can_edit, can_delete)
                    VALUES (?, ?, ?, ?, ?)''',
                 ('admin', module, 1, 1, 1))
    
    conn.commit()
    conn.close()
    
    print("✅ Admin reseteado exitosamente!")
    print("👤 Usuario: admin")
    print("🔑 Contraseña: admin123")
    print("🎯 Permisos: Acceso completo a todos los módulos")
    print("🔓 2FA: Deshabilitado para acceso fácil")

if __name__ == "__main__":
    reset_admin()