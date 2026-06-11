"""SCRUM-QA-23: pruebas de integración de /api/reportes/exportar (RF06).

Verifica MIME correcto, contenido no vacío y permisos por rol.
"""
import pytest

MIME_PDF = "application/pdf"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.fixture(autouse=True)
def sin_redis(monkeypatch):
    monkeypatch.setattr("app.services.dashboard_service.get_redis", lambda: None)


def test_exportar_pdf_admin(client, auth_admin_headers):
    resp = client.post("/api/reportes/exportar",
                       json={"formato": "pdf", "usar_familia_atu": True},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == MIME_PDF
    assert len(resp.content) > 0
    assert resp.content[:4] == b"%PDF"
    assert 'filename="metrohub_reporte_atu.pdf"' in resp.headers["content-disposition"]


def test_exportar_xlsx_admin(client, auth_admin_headers):
    resp = client.post("/api/reportes/exportar",
                       json={"formato": "xlsx", "usar_familia_atu": True},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == MIME_XLSX
    assert len(resp.content) > 0
    assert resp.content[:2] == b"PK"
    assert 'filename="metrohub_reporte_atu.xlsx"' in resp.headers["content-disposition"]


def test_exportar_pdf_sin_familia_atu(client, auth_admin_headers):
    resp = client.post("/api/reportes/exportar",
                       json={"formato": "pdf", "usar_familia_atu": False},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.content[:4] == b"%PDF"


def test_exportar_con_extras(client, auth_admin_headers):
    resp = client.post("/api/reportes/exportar",
                       json={"formato": "pdf", "extras": {"observaciones": "reporte de prueba"}},
                       headers=auth_admin_headers)
    assert resp.status_code == 200
    assert len(resp.content) > 0


def test_exportar_supervisor_permitido(client, auth_supervisor_norte_headers):
    resp = client.post("/api/reportes/exportar", json={"formato": "xlsx"},
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"


def test_exportar_chofer_403(client, auth_chofer_headers):
    resp = client.post("/api/reportes/exportar", json={"formato": "pdf"},
                       headers=auth_chofer_headers)
    assert resp.status_code == 403


def test_exportar_sin_token_401(client):
    resp = client.post("/api/reportes/exportar", json={"formato": "pdf"})
    assert resp.status_code == 401


def test_exportar_formato_invalido_400(client, auth_admin_headers):
    resp = client.post("/api/reportes/exportar", json={"formato": "csv"},
                       headers=auth_admin_headers)
    assert resp.status_code == 400
    assert "no soportada" in resp.json()["detail"] or "no soportado" in resp.json()["detail"]
