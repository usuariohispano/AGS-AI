# sistema_pyme/backup/backup_system.py
import sqlite3
import os
import shutil
import zipfile
from datetime import datetime
import schedule
import time
from threading import Thread

class BackupSystem:
    def __init__(self, db_path: str, backup_dir: str = "data/backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, backup_type: str = "manual") -> str:
        """Crear un backup de la base de datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}_{backup_type}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Conectar y hacer backup
            conn = sqlite3.connect(self.db_path)
            with open(backup_path, 'w') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
            conn.close()
            
            # Comprimir backup
            zip_path = f"{backup_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, os.path.basename(backup_path))
            
            # Eliminar archivo sin comprimir
            os.remove(backup_path)
            
            # Registrar en log
            self._log_backup(backup_type, zip_path, True, "Backup completado exitosamente")
            
            return zip_path
            
        except Exception as e:
            error_msg = f"Error al crear backup: {str(e)}"
            self._log_backup(backup_type, "", False, error_msg)
            raise Exception(error_msg)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restaurar desde un backup"""
        try:
            # Verificar que el backup existe
            if not os.path.exists(backup_path):
                raise Exception("Archivo de backup no encontrado")
            
            # Crear conexión temporal
            temp_db = "data/restore_temp.db"
            if os.path.exists(temp_db):
                os.remove(temp_db)
            
            conn = sqlite3.connect(temp_db)
            conn.close()
            
            # Restaurar datos
            os.remove(temp_db)
            shutil.copy2(backup_path, self.db_path)
            
            self._log_restore(backup_path, True, "Restauración completada exitosamente")
            return True
            
        except Exception as e:
            error_msg = f"Error al restaurar backup: {str(e)}"
            self._log_restore(backup_path, False, error_msg)
            return False
    
    def list_backups(self) -> list:
        """Listar todos los backups disponibles"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, file)
                file_time = os.path.getmtime(file_path)
                backups.append({
                    'name': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'created': datetime.fromtimestamp(file_time)
                })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def _log_backup(self, backup_type: str, backup_path: str, success: bool, message: str):
        """Registrar operación de backup en log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'backup',
            'backup_type': backup_type,
            'backup_path': backup_path,
            'success': success,
            'message': message
        }
        
        # Guardar en archivo de log
        log_file = os.path.join(self.backup_dir, 'backup_log.json')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _log_restore(self, backup_path: str, success: bool, message: str):
        """Registrar operación de restauración en log"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'restore',
            'backup_path': backup_path,
            'success': success,
            'message': message
        }
        
        # Guardar en archivo de log
        log_file = os.path.join(self.backup_dir, 'backup_log.json')
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def start_automatic_backups(self, interval_hours: int = 24):
        """Iniciar backups automáticos programados"""
        def backup_job():
            self.create_backup("automatic")
        
        # Programar backup diario
        schedule.every(interval_hours).hours.do(backup_job)
        
        # Ejecutar en segundo plano
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(3600)  # Revisar cada hora
        
        Thread(target=run_scheduler, daemon=True).start()