## tests/test_auth.py
# Valida autenticación y comprobación de permisos sobre el servicio de auth.
from services.auth_service import AuthService
from models.usuario import Usuario, Rol


def test_autenticacion_y_permisos(db_session):
    rol = Rol(nombre="admin", permisos="crear_pedido,ver_corte")
    user = Usuario(username="demo", nombre="Demo", pass_hash="secret", rol=rol)
    db_session.add_all([rol, user])
    db_session.commit()

    auth = AuthService(db_session)
    assert auth.autenticar("demo", "secret") is not None
    assert auth.requiere_permiso(user.id, "crear_pedido") is True
    assert auth.requiere_permiso(user.id, "borrar") is False
