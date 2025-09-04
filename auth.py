# auth.py
import streamlit as st
import sqlite3
import bcrypt
import pyotp
import qrcode
import io
from datetime import datetime, timedelta
import secrets

class AuthSystem:
    def __init__(self, conn):
        self.conn = conn
        self.init_auth_tables()
    
    def init_auth_tables(self):
        c = self.conn.cursor()
        
        # Tabla de usuarios
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                     email TEXT UNIQUE, password_hash TEXT, role TEXT,
                     is_active INTEGER, created_at TIMESTAMP,
                     last_login TIMESTAMP, two_factor_secret TEXT)''')
        
        # Tabla de sesiones
        c.execute('''CREATE TABLE IF NOT EXISTS sessions
                    (id INTEGER PRIMARY KEY, user_id INTEGER, session_token TEXT,
                     created_at TIMESTAMP, expires_at TIMESTAMP,
                     FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # Tabla de permisos
        c.execute('''CREATE TABLE IF NOT EXISTS permissions
                    (id INTEGER PRIMARY KEY, role TEXT, module TEXT,
                     can_view INTEGER, can_edit INTEGER, can_delete INTEGER)''')
        
        self.conn.commit()
        self.create_default_roles()
    
    def create_default_roles(self):
        c = self.conn.cursor()
        
        # Roles por defecto
        roles_permissions = [
            ('admin', 'dashboard', 1, 1, 1),
            ('admin', 'data_import', 1, 1, 1),
            ('admin', 'finance', 1, 1, 1),
            ('admin', 'crm', 1, 1, 1),
            ('admin', 'hr', 1, 1, 1),
            ('admin', 'inventory', 1, 1, 1),
            ('admin', 'admin', 1, 1, 1),
            ('manager', 'dashboard', 1, 1, 0),
            ('manager', 'finance', 1, 1, 0),
            ('manager', 'crm', 1, 1, 0),
            ('analyst', 'dashboard', 1, 0, 0),
            ('analyst', 'finance', 1, 0, 0),
            ('user', 'dashboard', 1, 0, 0)
        ]
        
        for role, module, can_view, can_edit, can_delete in roles_permissions:
            c.execute('''INSERT OR IGNORE INTO permissions 
                        (role, module, can_view, can_edit, can_delete)
                        VALUES (?, ?, ?, ?, ?)''',
                     (role, module, can_view, can_edit, can_delete))
        
        # Crear usuario admin por defecto si no existe - SIN 2FA
        c.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if c.fetchone()[0] == 0:
            # Hash de la contraseña admin123
            password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            c.execute('''INSERT INTO users 
                        (username, email, password_hash, role, is_active, 
                         created_at, two_factor_secret)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     ('admin', 'admin@sistema.pyme', password_hash, 'admin', 1,
                      datetime.now(), None))  # two_factor_secret = None para admin
        
        self.conn.commit()
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_user(self, username, email, password, role='user'):
        c = self.conn.cursor()
        
        # Generar secreto para 2FA
        two_factor_secret = pyotp.random_base32()
        
        try:
            c.execute('''INSERT INTO users 
                        (username, email, password_hash, role, is_active, 
                         created_at, two_factor_secret)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (username, email, self.hash_password(password), role, 1,
                      datetime.now(), two_factor_secret))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username, password):
        c = self.conn.cursor()
        c.execute('''SELECT id, username, password_hash, role, two_factor_secret 
                     FROM users WHERE username = ? AND is_active = 1''', (username,))
        user = c.fetchone()
        
        if user and self.verify_password(password, user[2]):
            # Actualizar último login
            c.execute('''UPDATE users SET last_login = ? WHERE id = ?''',
                     (datetime.now(), user[0]))
            self.conn.commit()
            
            user_data = {
                'id': user[0],
                'username': user[1],
                'role': user[3],
                'two_factor_secret': user[4]
            }
            
            # ✅ EXCEPCIÓN: Si es admin, saltar 2FA automáticamente
            if username == 'admin':
                # Crear sesión inmediatamente para admin
                session_token = self.create_session(user_data['id'])
                return {**user_data, 'skip_2fa': True, 'session_token': session_token}
            
            return user_data
        return None
    
    def generate_2fa_qr(self, secret, username):
        """Generar código QR para 2FA"""
        try:
            # Generar URL de autenticación
            totp = pyotp.TOTP(secret)
            auth_url = totp.provisioning_uri(
                name=username,
                issuer_name='Sistema PYME'
            )
            
            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(auth_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a bytes para Streamlit
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            st.error(f"Error generando QR: {str(e)}")
            return None
    
    def verify_2fa(self, secret, token):
        try:
            return pyotp.TOTP(secret).verify(token)
        except:
            return False
    
    def create_session(self, user_id):
        c = self.conn.cursor()
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        c.execute('''INSERT INTO sessions 
                    (user_id, session_token, created_at, expires_at)
                    VALUES (?, ?, ?, ?)''',
                 (user_id, session_token, datetime.now(), expires_at))
        self.conn.commit()
        
        return session_token
    
    def validate_session(self, session_token):
        c = self.conn.cursor()
        c.execute('''SELECT user_id, expires_at FROM sessions 
                     WHERE session_token = ? AND expires_at > ?''',
                 (session_token, datetime.now()))
        session = c.fetchone()
        
        if session:
            return session[0]  # user_id
        return None
    
    def has_permission(self, user_role, module, action):
        c = self.conn.cursor()
        c.execute(f'''SELECT {action} FROM permissions 
                     WHERE role = ? AND module = ?''', (user_role, module))
        result = c.fetchone()
        return result and result[0] == 1
    
    def get_user_role(self, user_id):
        c = self.conn.cursor()
        c.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        return result[0] if result else 'user'

def render_login_register(auth_system):
    """Renderizar interfaz de login/registro"""
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar Sesión")
            
            if submitted:
                user = auth_system.authenticate_user(username, password)
                if user:
                    # ✅ Si es admin, acceder directamente
                    if user.get('skip_2fa', False):
                        st.session_state.auth_token = user['session_token']
                        st.session_state.user = {
                            'id': user['id'],
                            'username': user['username'],
                            'role': user['role']
                        }
                        st.rerun()
                    else:
                        # Verificación 2FA para usuarios normales
                        if '2fa_verified' not in st.session_state:
                            st.session_state['2fa_user'] = user
                            st.session_state['show_2fa'] = True
                            st.rerun()
                else:
                    st.error("Credenciales inválidas")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Nuevo usuario")
            new_email = st.text_input("Email")
            new_password = st.text_input("Nueva contraseña", type="password")
            confirm_password = st.text_input("Confirmar contraseña", type="password")
            submitted = st.form_submit_button("Registrarse")
            
            if submitted:
                if new_password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                elif auth_system.create_user(new_username, new_email, new_password):
                    st.success("Usuario creado exitosamente")
                else:
                    st.error("El usuario ya existe")
    
    # Modal para 2FA - Solo para usuarios que no son admin
    if st.session_state.get('show_2fa', False):
        user = st.session_state.get('2fa_user', {})
        
        # Verificar que no sea admin
        if user.get('username') != 'admin':
            st.write("## 🔐 Verificación en Dos Pasos")
            
            # Mostrar instrucciones claras
            st.info("""
            **Para acceder, necesitas verificación en dos pasos:**
            1. Escanea el código QR con Google Authenticator, Authy o Microsoft Authenticator
            2. Ingresa el código de 6 dígitos que aparece en tu app
            3. Los códigos NO se envían por email/SMS
            """)
            
            # Generar y mostrar QR inmediatamente
            if 'qr_generated' not in st.session_state:
                qr_image = auth_system.generate_2fa_qr(
                    user.get('two_factor_secret', ''), 
                    user.get('username', '')
                )
                st.session_state.qr_image = qr_image
                st.session_state.qr_generated = True
            
            if st.session_state.get('qr_image'):
                st.image(st.session_state.qr_image, caption="Escanee con su app de autenticación")
            else:
                st.error("No se pudo generar el código QR")
            
            # Input para el código
            token = st.text_input("Código de 6 dígitos", max_chars=6, key="2fa_token")
            
            if st.button("✅ Verificar Código", key="verify_2fa"):
                if user and token and len(token) == 6:
                    if auth_system.verify_2fa(user.get('two_factor_secret', ''), token):
                        # Autenticación exitosa
                        session_token = auth_system.create_session(user['id'])
                        st.session_state.auth_token = session_token
                        st.session_state.user = user
                        st.session_state.show_2fa = False
                        st.session_state.qr_generated = False
                        st.rerun()
                    else:
                        st.error("❌ Código inválido. Intenta nuevamente.")
                else:
                    st.error("⚠️ Por favor ingresa un código de 6 dígitos")
            
            # Opción para reintentar
            if st.button("🔄 Generar nuevo código QR", key="new_qr"):
                st.session_state.qr_generated = False
                st.rerun()