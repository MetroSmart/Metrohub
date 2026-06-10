"""Unit tests para app.services.auth_service (RF01)."""
from datetime import datetime, timedelta

import pytest
from jose import JWTError

from app.services import auth_service


# ── hash / verify ──────────────────────────────────────────
def test_hash_password_genera_hash_bcrypt():
    h = auth_service.hash_password("clave-segura-123")
    assert h.startswith("$2b$") or h.startswith("$2a$")
    assert h != "clave-segura-123"


def test_verificar_password_correcta():
    h = auth_service.hash_password("clave")
    assert auth_service.verificar_password("clave", h) is True


def test_verificar_password_incorrecta():
    h = auth_service.hash_password("clave")
    assert auth_service.verificar_password("otra", h) is False


# ── tokens ─────────────────────────────────────────────────
def test_crear_y_decodificar_token_admin():
    token = auth_service.crear_token({
        "sub": "admin.atu@metrohub.gob.pe",
        "rol": "admin_atu",
        "nombre": "Admin ATU",
        "chofer_id": None,
        "area_id": None,
    })
    decoded = auth_service.decodificar_token(token)
    assert decoded["email"] == "admin.atu@metrohub.gob.pe"
    assert decoded["rol"] == "admin_atu"
    assert decoded["area_id"] is None


def test_token_supervisor_incluye_area_id():
    token = auth_service.crear_token({
        "sub": "sup.norte@metrohub.gob.pe",
        "rol": "supervisor_area",
        "nombre": "Sup Norte",
        "chofer_id": None,
        "area_id": 1,
    })
    decoded = auth_service.decodificar_token(token)
    assert decoded["area_id"] == 1
    assert decoded["rol"] == "supervisor_area"


def test_token_invalido_lanza_jwterror():
    with pytest.raises(JWTError):
        auth_service.decodificar_token("token.invalido.xxx")


def test_token_sin_sub_lanza_jwterror():
    from jose import jwt
    payload = {"rol": "admin_atu", "exp": datetime.utcnow() + timedelta(minutes=5)}
    token = jwt.encode(payload, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM)
    with pytest.raises(JWTError):
        auth_service.decodificar_token(token)


# ── autenticación contra DB ────────────────────────────────
def test_autenticar_admin_ok(db_session, usuario_admin):
    sesion = auth_service.autenticar(db_session, "admin.atu@metrohub.gob.pe", "admin123")
    assert sesion is not None
    assert sesion["rol"] == "admin_atu"
    assert sesion["area_id"] is None
    assert sesion["chofer_id"] is None


def test_autenticar_supervisor_devuelve_area_id(db_session, usuario_supervisor_norte):
    sesion = auth_service.autenticar(db_session, "sup.norte@metrohub.gob.pe", "norte123")
    assert sesion is not None
    assert sesion["rol"] == "supervisor_area"
    assert sesion["area_id"] == 1


def test_autenticar_chofer_devuelve_chofer_id(db_session, acceso_chofer_norte):
    sesion = auth_service.autenticar(db_session, "jhuaman@metrohub.gob.pe", "44156789")
    assert sesion is not None
    assert sesion["rol"] == "chofer"
    assert sesion["chofer_id"] == acceso_chofer_norte.chofer_id


def test_autenticar_password_incorrecta(db_session, usuario_admin):
    assert auth_service.autenticar(db_session, "admin.atu@metrohub.gob.pe", "wrong") is None


def test_autenticar_email_inexistente(db_session):
    assert auth_service.autenticar(db_session, "nadie@nada.com", "x") is None


def test_bloqueo_tras_max_intentos(db_session, usuario_admin):
    for _ in range(auth_service.MAX_ATTEMPTS):
        auth_service.autenticar(db_session, usuario_admin.email, "mala")
    db_session.refresh(usuario_admin)
    assert usuario_admin.bloqueado_hasta is not None
    assert usuario_admin.bloqueado_hasta > datetime.utcnow()
    # incluso con password correcta queda bloqueado
    assert auth_service.autenticar(db_session, usuario_admin.email, "admin123") is None


# ── cambio de contraseña primer ingreso ────────────────────
def test_cambiar_password_primer_ingreso_ok(db_session, chofer_norte):
    from app.models.acceso_chofer import AccesoChofer
    acceso = AccesoChofer(
        chofer_id=chofer_norte.id,
        email="nuevo@metrohub.gob.pe",
        password_hash=auth_service.hash_password(chofer_norte.dni),
        activo=True,
        debe_cambiar_password=True,
    )
    db_session.add(acceso)
    db_session.commit()

    actualizado = auth_service.cambiar_password_primer_ingreso(
        db_session, "nuevo@metrohub.gob.pe", chofer_norte.dni, "nueva-clave-segura"
    )
    assert actualizado.debe_cambiar_password is False
    assert auth_service.verificar_password("nueva-clave-segura", actualizado.password_hash)


def test_cambiar_password_rechaza_password_igual_a_dni(db_session, chofer_norte):
    from app.models.acceso_chofer import AccesoChofer
    acceso = AccesoChofer(
        chofer_id=chofer_norte.id,
        email="nuevo2@metrohub.gob.pe",
        password_hash=auth_service.hash_password(chofer_norte.dni),
        activo=True,
        debe_cambiar_password=True,
    )
    db_session.add(acceso)
    db_session.commit()

    with pytest.raises(ValueError, match="DNI"):
        auth_service.cambiar_password_primer_ingreso(
            db_session, "nuevo2@metrohub.gob.pe", chofer_norte.dni, chofer_norte.dni
        )


def test_cambiar_password_rechaza_corta(db_session, chofer_norte):
    from app.models.acceso_chofer import AccesoChofer
    acceso = AccesoChofer(
        chofer_id=chofer_norte.id,
        email="nuevo3@metrohub.gob.pe",
        password_hash=auth_service.hash_password(chofer_norte.dni),
        activo=True,
        debe_cambiar_password=True,
    )
    db_session.add(acceso)
    db_session.commit()

    with pytest.raises(ValueError, match="8 caracteres"):
        auth_service.cambiar_password_primer_ingreso(
            db_session, "nuevo3@metrohub.gob.pe", chofer_norte.dni, "corta"
        )
