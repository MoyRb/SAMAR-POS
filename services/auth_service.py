# services/auth_service.py
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from models.usuario import Usuario
from utils.logger import log_event


class AuthService:
    """Servicio de autenticación y control de acceso."""

    def __init__(self, db: Session):
        self.db = db

    def autenticar(self, username: str, password: str):
        """Valida las credenciales de un usuario activo."""
        user = (
            self.db.query(Usuario)
            .filter(Usuario.username == username, Usuario.activo == True)
            .first()
        )

        if not user:
            log_event(None, "LOGIN_FAIL", f"Usuario no encontrado: {username}")
            return None

        # Verifica la contraseña con bcrypt
        try:
            valido = bcrypt.verify(password, user.pass_hash)
        except ValueError:
            # Permite fallback a contraseñas sin hash en entornos de prueba
            valido = user.pass_hash == password

        if not valido:
            log_event(user.id, "LOGIN_FAIL", "Contraseña incorrecta")
            return None

        # Login exitoso
        log_event(user.id, "LOGIN_OK", "Acceso correcto")

        # Convertir a dict antes de devolverlo
        user_data = {
            "id": user.id,
            "nombre": user.nombre,
            "username": user.username,
            "rol_id": user.rol_id,
            "activo": user.activo,
        }

        return user_data

    def requiere_permiso(self, user_id: int, permiso: str) -> bool:
        usuario = self.db.query(Usuario).get(user_id)
        if not usuario:
            return False
        tiene = usuario.tiene_permiso(permiso)
        if not tiene:
            log_event(user_id, "PERMISO_DENEGADO", f"Falta permiso: {permiso}")
        return tiene
