"""
Fixtures compartidos para la suite de tests de MetroHub.

Override de la base de datos a SQLite en memoria para tests rápidos y aislados.
Las features que requieren Postgres (vistas, triggers) deben marcarse con
@pytest.mark.postgres y se omitirán aquí.
"""
import os
import sys
from pathlib import Path

# Variables de entorno mínimas ANTES de importar la app
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
os.environ.setdefault("MAX_LOGIN_ATTEMPTS", "5")
os.environ.setdefault("LOCKOUT_MINUTES", "15")
# Postgres dummy — no se conecta porque hacemos override
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app as fastapi_app
import app.models  # noqa: F401 — registra modelos
from app.models.area_operativa import AreaOperativa
from app.models.usuario import Usuario
from app.models.chofer import Chofer
from app.models.acceso_chofer import AccesoChofer
from app.services import auth_service


# ── Engine SQLite en memoria compartido ───────────────────
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_engine):
    """TestClient con get_db sobreescrito a SQLite."""
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def _override_get_db():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()


# ── Datos seed mínimos ────────────────────────────────────
@pytest.fixture
def area_norte(db_session) -> AreaOperativa:
    area = AreaOperativa(id=1, nombre="Operaciones Norte", nombre_corto="Op. Norte", activo=True)
    db_session.add(area)
    db_session.commit()
    db_session.refresh(area)
    return area


@pytest.fixture
def area_sur(db_session) -> AreaOperativa:
    area = AreaOperativa(id=2, nombre="Operaciones Sur", nombre_corto="Op. Sur", activo=True)
    db_session.add(area)
    db_session.commit()
    db_session.refresh(area)
    return area


@pytest.fixture
def usuario_admin(db_session) -> Usuario:
    u = Usuario(
        email="admin.atu@metrohub.gob.pe",
        password_hash=auth_service.hash_password("admin123"),
        nombre="Admin",
        apellidos="ATU",
        dni="10000001",
        rol="admin_atu",
        area_id=None,
        activo=True,
        intentos_fallidos=0,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def usuario_supervisor_norte(db_session, area_norte) -> Usuario:
    u = Usuario(
        email="sup.norte@metrohub.gob.pe",
        password_hash=auth_service.hash_password("norte123"),
        nombre="Supervisor",
        apellidos="Norte",
        dni="10000002",
        rol="supervisor_area",
        area_id=area_norte.id,
        activo=True,
        intentos_fallidos=0,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def chofer_norte(db_session, area_norte) -> Chofer:
    from datetime import date
    c = Chofer(
        dni="44156789",
        nombres="Juan Manuel",
        apellidos="Huamán Flores",
        fecha_nacimiento=date(1985, 5, 1),
        area_id=area_norte.id,
        numero_licencia="LIC-44156789",
        tipo_licencia="A-IIIB",
        fec_vence_licencia=date(2027, 1, 1),
        fec_vence_certif_prot=date(2027, 1, 1),
        estado="activo",
    )
    db_session.add(c)
    db_session.commit()
    db_session.refresh(c)
    return c


@pytest.fixture
def acceso_chofer_norte(db_session, chofer_norte) -> AccesoChofer:
    a = AccesoChofer(
        chofer_id=chofer_norte.id,
        email="jhuaman@metrohub.gob.pe",
        password_hash=auth_service.hash_password("44156789"),
        activo=True,
        debe_cambiar_password=False,
        intentos_fallidos=0,
    )
    db_session.add(a)
    db_session.commit()
    db_session.refresh(a)
    return a


# ── Helpers de auth: emiten tokens sin pasar por /login ───
def _token_for(email: str, rol: str, *, nombre: str = "Test", chofer_id=None, area_id=None) -> str:
    return auth_service.crear_token({
        "sub": email,
        "rol": rol,
        "nombre": nombre,
        "chofer_id": chofer_id,
        "area_id": area_id,
    })


@pytest.fixture
def auth_admin_headers(usuario_admin) -> dict:
    token = _token_for(usuario_admin.email, "admin_atu", nombre=usuario_admin.nombre)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_supervisor_norte_headers(usuario_supervisor_norte) -> dict:
    token = _token_for(
        usuario_supervisor_norte.email,
        "supervisor_area",
        nombre=usuario_supervisor_norte.nombre,
        area_id=usuario_supervisor_norte.area_id,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_chofer_headers(acceso_chofer_norte) -> dict:
    token = _token_for(
        acceso_chofer_norte.email,
        "chofer",
        nombre="Juan Manuel",
        chofer_id=acceso_chofer_norte.chofer_id,
    )
    return {"Authorization": f"Bearer {token}"}
