import re
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator


def validate_strong_password(password):
    """Validador de contraseña fuerte"""
    if len(password) < 8:
        raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('La contraseña debe contener al menos una mayúscula.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('La contraseña debe contener al menos una minúscula.')
    
    if not re.search(r'\d', password):
        raise ValidationError('La contraseña debe contener al menos un número.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('La contraseña debe contener al menos un carácter especial.')
    
    # Verificar patrones comunes débiles
    weak_patterns = [
        r'123456', r'password', r'admin', r'qwerty',
        r'abc123', r'111111', r'000000'
    ]
    
    for pattern in weak_patterns:
        if re.search(pattern, password.lower()):
            raise ValidationError('La contraseña contiene patrones débiles comunes.')


def validate_email_domain(email):
    """Validador de dominio de email"""
    allowed_domains = [
        'gmail.com', 'outlook.com', 'hotmail.com', 'yahoo.com',
        'empresa.com'  # Agregar dominios corporativos permitidos
    ]
    
    domain = email.split('@')[1].lower()
    if domain not in allowed_domains:
        raise ValidationError(f'Dominio de email no permitido: {domain}')


def validate_safe_filename(filename):
    """Validador de nombres de archivo seguros"""
    # Caracteres permitidos: letras, números, guiones, puntos
    safe_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
    
    if not safe_pattern.match(filename):
        raise ValidationError('El nombre de archivo contiene caracteres no permitidos.')
    
    # Extensiones peligrosas
    dangerous_extensions = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
        '.vbs', '.js', '.jar', '.php', '.asp', '.jsp'
    ]
    
    file_extension = '.' + filename.split('.')[-1].lower()
    if file_extension in dangerous_extensions:
        raise ValidationError('Tipo de archivo no permitido.')


# Validadores regex
alphanumeric_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9]+$',
    message='Solo se permiten caracteres alfanuméricos.'
)

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message='Formato de teléfono inválido.'
)

tax_id_validator = RegexValidator(
    regex=r'^\d{11}$',
    message='CUIT debe tener 11 dígitos.'
)