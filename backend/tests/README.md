# Tests — Backend MetroHub

Suite de tests con **pytest + httpx + SQLite en memoria**.

## Instalación

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Correr la suite

```bash
# Todos los tests
pytest

# Verbose
pytest -v

# Con cobertura
pytest --cov=app --cov-report=term-missing --cov-report=html

# Solo unit
pytest tests/unit

# Solo integration
pytest tests/integration

# Excluir los que requieren Postgres real
pytest -m "not postgres"
```

## Estructura

```
tests/
├── conftest.py          # fixtures: db_session, client, auth_*_headers, seed mínimos
├── unit/
│   └── services/        # tests aislados de la lógica de negocio
└── integration/         # tests de endpoints contra TestClient
```

## Fixtures principales (`conftest.py`)

- `db_engine` / `db_session` — SQLite en memoria por test
- `client` — `TestClient` con `get_db` sobreescrito
- `area_norte`, `area_sur` — áreas operativas
- `usuario_admin`, `usuario_supervisor_norte` — usuarios staff
- `chofer_norte`, `acceso_chofer_norte` — chofer y su acceso
- `auth_admin_headers`, `auth_supervisor_norte_headers`, `auth_chofer_headers` — headers con JWT listos

## Convenciones

- Un test = un comportamiento. Nombres en español, `test_<que>_<condicion>`.
- Cada test es **independiente**: la DB se recrea en cada test (fixture `function` scope).
- Tests que requieran vistas/triggers Postgres → marcar con `@pytest.mark.postgres`.

## Cobertura objetivo (RNF05)

≥ 70 % en módulos críticos:
- `app/services/auth_service.py`
- `app/services/horario_validacion.py`
- `app/services/conflicto_service.py`
- `app/services/chofer_service.py`
- `app/routers/auth.py`, `horarios.py`, `choferes.py`
