# sistema_pyme/plugins/base.py
import importlib
import inspect
import os
import json
from typing import Dict, List, Any, Optional, Type, Union
import sqlite3

class Plugin:
    """Clase base para todos los plugins"""
    def __init__(self, conn: sqlite3.Connection, config: Optional[Dict[str, Any]] = None):
        self.conn = conn
        self.config = config or {}
        self.name = self.__class__.__name__
        self.version = "1.0.0"  # ✅ Atributo de INSTANCIA
    
    def initialize(self) -> None:
        """Inicializar el plugin"""
        pass
    
    def cleanup(self) -> None:
        """Limpiar recursos del plugin"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Obtener información del plugin"""
        return {
            "name": self.name,
            "version": self.version,
            "description": getattr(self, "description", "Sin descripción")
        }

class PluginSystem:
    def __init__(self, conn: sqlite3.Connection, plugins_dir: str = "plugins"):
        self.conn = conn
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self.init_plugins_table()
    
    def init_plugins_table(self) -> None:
        """Crear tabla para registro de plugins"""
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS plugins
                    (id INTEGER PRIMARY KEY, name TEXT, version TEXT, 
                     enabled BOOLEAN, config TEXT)''')
        self.conn.commit()
    
    def load_plugins(self) -> None:
        """Cargar todos los plugins del directorio"""
        plugins_path = os.path.join(os.path.dirname(__file__), self.plugins_dir)
        if not os.path.exists(plugins_path):
            os.makedirs(plugins_path, exist_ok=True)
            return
        
        for file_name in os.listdir(plugins_path):
            if file_name.endswith('.py') and file_name != '__init__.py':
                plugin_name = file_name[:-3]  # Remove .py extension
                self.load_plugin(plugin_name)
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Cargar un plugin específico"""
        try:
            # ✅ Importación segura con manejo de errores
            try:
                module = importlib.import_module(f"plugins.{plugin_name}")
            except ImportError as e:
                print(f"Error importando plugin {plugin_name}: {e}")
                return False
            
            # Buscar clases que hereden de Plugin
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                print(f"No se encontró clase Plugin válida en {plugin_name}")
                return False
            
            # Verificar si el plugin está habilitado
            c = self.conn.cursor()
            c.execute('''SELECT enabled, config FROM plugins WHERE name = ?''',
                     (plugin_name,))
            result = c.fetchone()
            
            # ✅ Manejar resultado que puede ser None
            enabled = True
            config_data = "{}"
            
            if result is not None:
                enabled = bool(result[0])
                config_data = result[1] if result[1] is not None else "{}"
            
            if not enabled:
                print(f"Plugin {plugin_name} está deshabilitado")
                return False
            
            # ✅ Cargar configuración de forma segura
            config_dict = {}
            try:
                config_dict = json.loads(config_data) if config_data else {}
            except json.JSONDecodeError:
                print(f"Configuración inválida para plugin {plugin_name}, usando configuración por defecto")
                config_dict = {}
            
            # Instanciar el plugin
            plugin_instance = plugin_class(self.conn, config_dict)
            self.plugins[plugin_name] = plugin_instance
            
            # ✅ Inicializar plugin de forma segura
            try:
                plugin_instance.initialize()
                print(f"Plugin {plugin_name} cargado exitosamente")
                return True
            except Exception as e:
                print(f"Error inicializando plugin {plugin_name}: {e}")
                del self.plugins[plugin_name]
                return False
            
        except Exception as e:
            print(f"Error cargando plugin {plugin_name}: {e}")
            return False
    
    def register_plugin(self, plugin_name: str, plugin_class: Type[Plugin], enabled: bool = True) -> bool:
        """Registrar un nuevo plugin"""
        try:
            # ✅ Crear instancia temporal para obtener la versión
            temp_instance = plugin_class(self.conn, {})
            version = temp_instance.version  # ✅ Acceder a version desde la INSTANCIA
            
            c = self.conn.cursor()
            c.execute('''INSERT OR REPLACE INTO plugins (name, version, enabled, config)
                        VALUES (?, ?, ?, ?)''',
                     (plugin_name, version, enabled, "{}"))
            self.conn.commit()
            
            # ✅ Crear instancia solo si está habilitado
            if enabled:
                plugin_instance = plugin_class(self.conn, {})
                self.plugins[plugin_name] = plugin_instance
                plugin_instance.initialize()
            
            return True
        except Exception as e:
            print(f"Error registrando plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Habilitar un plugin"""
        try:
            # ✅ Verificar si el plugin ya está cargado
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                plugin.initialize()
            else:
                # Intentar cargar el plugin si no está en memoria
                if not self.load_plugin(plugin_name):
                    return False
            
            # ✅ Actualizar base de datos
            c = self.conn.cursor()
            c.execute('''UPDATE plugins SET enabled = TRUE WHERE name = ?''',
                     (plugin_name,))
            self.conn.commit()
            
            return c.rowcount > 0
            
        except Exception as e:
            print(f"Error habilitando plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Deshabilitar un plugin"""
        try:
            # ✅ Limpiar plugin si está cargado
            if plugin_name in self.plugins:
                plugin = self.plugins[plugin_name]
                plugin.cleanup()
                del self.plugins[plugin_name]
            
            # ✅ Actualizar base de datos
            c = self.conn.cursor()
            c.execute('''UPDATE plugins SET enabled = FALSE WHERE name = ?''',
                     (plugin_name,))
            self.conn.commit()
            
            return c.rowcount > 0
            
        except Exception as e:
            print(f"Error deshabilitando plugin {plugin_name}: {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Obtener un plugin por nombre"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """Listar todos los plugins"""
        plugins_info = []
        for name, plugin in self.plugins.items():
            plugins_info.append(plugin.get_info())
        return plugins_info
    
    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """Obtener estado detallado de un plugin"""
        try:
            c = self.conn.cursor()
            c.execute('''SELECT enabled, config FROM plugins WHERE name = ?''',
                     (plugin_name,))
            result = c.fetchone()
            
            plugin_info = {
                "name": plugin_name,
                "loaded": plugin_name in self.plugins,
                "enabled": False,
                "config": {}
            }
            
            if result is not None:
                plugin_info["enabled"] = bool(result[0])
                try:
                    plugin_info["config"] = json.loads(result[1] or "{}")
                except json.JSONDecodeError:
                    plugin_info["config"] = {}
            
            if plugin_name in self.plugins:
                plugin_info.update(self.plugins[plugin_name].get_info())
            
            return plugin_info
            
        except Exception as e:
            return {
                "name": plugin_name,
                "error": str(e),
                "loaded": False,
                "enabled": False
            }