# sistema_pyme/templates/email_templates.py
from jinja2 import Template
import os
from typing import Dict, Any

class EmailTemplateSystem:
    def __init__(self, templates_dir: str = "templates/emails"):
        self.templates_dir = templates_dir
        os.makedirs(templates_dir, exist_ok=True)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Cargar plantillas desde el directorio"""
        templates = {}
        for file_name in os.listdir(self.templates_dir):
            if file_name.endswith('.j2'):
                with open(os.path.join(self.templates_dir, file_name), 'r', encoding='utf-8') as f:
                    template_name = file_name[:-3]  # Remove .j2 extension
                    templates[template_name] = f.read()
        return templates
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renderizar una plantilla con el contexto proporcionado"""
        if template_name in self.templates:
            template = Template(self.templates[template_name])
            return template.render(context)
        raise ValueError(f"Plantilla '{template_name}' no encontrada")
    
    def create_template(self, template_name: str, content: str):
        """Crear una nueva plantilla"""
        template_path = os.path.join(self.templates_dir, f"{template_name}.j2")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.templates[template_name] = content
    
    def get_template_list(self) -> list[str]:
        """Obtener lista de plantillas disponibles"""
        return list(self.templates.keys())

# Plantillas predefinidas
DEFAULT_TEMPLATES = {
    "welcome_email": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Bienvenido a {{ business_name }}</title>
</head>
<body>
    <h1>¡Bienvenido a {{ business_name }}!</h1>
    <p>Hola {{ user_name }},</p>
    <p>Gracias por unirte a nuestro sistema de gestión. Estamos aquí para ayudarte a gestionar tu negocio de manera más eficiente.</p>
    <p>Tu cuenta ha sido configurada con el rol: <strong>{{ user_role }}</strong></p>
    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
    <br>
    <p>Saludos,<br>El equipo de {{ business_name }}</p>
</body>
</html>
""",
    
    "invoice_email": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Factura de {{ business_name }}</title>
</head>
<body>
    <h1>Factura #{{ invoice_number }}</h1>
    <p>Hola {{ customer_name }},</p>
    <p>Adjunto encontrarás la factura por los servicios/productos proporcionados.</p>
    <p><strong>Total: {{ amount }}</strong></p>
    <p>Fecha de vencimiento: {{ due_date }}</p>
    <br>
    <p>Saludos,<br>{{ business_name }}</p>
</body>
</html>
""",
    
    "alert_email": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Alerta del Sistema - {{ business_name }}</title>
</head>
<body>
    <h2>Alerta del Sistema</h2>
    <p><strong>Tipo:</strong> {{ alert_type }}</p>
    <p><strong>Prioridad:</strong> {{ priority }}</p>
    <p><strong>Mensaje:</strong> {{ message }}</p>
    <p><strong>Fecha:</strong> {{ timestamp }}</p>
    <br>
    <p>Por favor, revisa esta alerta en el sistema.</p>
</body>
</html>
"""
}