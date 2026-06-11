"""SCRUM-QA-29: pruebas de integración de /api/areas/* (catálogos internos).

Lectura para cualquier autenticado; escritura solo admin_atu.
"""


def test_listar_areas_admin_ok(client, auth_admin_headers, area_norte, area_sur):
    resp = client.get("/api/areas/", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    nombres = {a["nombre_corto"] for a in body["areas"]}
    assert nombres == {"Op. Norte", "Op. Sur"}


def test_listar_areas_supervisor_ok(client, auth_supervisor_norte_headers, area_sur):
    resp = client.get("/api/areas/", headers=auth_supervisor_norte_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 2  # area_norte (del supervisor) + area_sur


def test_listar_areas_solo_activos(client, auth_admin_headers, area_norte, area_sur, db_session):
    area_sur.activo = False
    db_session.commit()

    resp = client.get("/api/areas/?solo_activos=true", headers=auth_admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["areas"][0]["nombre_corto"] == "Op. Norte"


def test_listar_areas_sin_token_401(client, area_norte):
    resp = client.get("/api/areas/")
    assert resp.status_code == 401


def test_obtener_area_ok(client, auth_admin_headers, area_norte):
    resp = client.get(f"/api/areas/{area_norte.id}", headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Operaciones Norte"


def test_obtener_area_404(client, auth_admin_headers):
    resp = client.get("/api/areas/999", headers=auth_admin_headers)
    assert resp.status_code == 404


def test_crear_area_admin_201(client, auth_admin_headers):
    resp = client.post("/api/areas/",
                       json={"nombre": "Operaciones Este", "nombre_corto": "Op. Este",
                             "descripcion": "Nueva zona de expansión"},
                       headers=auth_admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["nombre_corto"] == "Op. Este"
    assert body["activo"] is True


def test_crear_area_supervisor_403(client, auth_supervisor_norte_headers):
    resp = client.post("/api/areas/",
                       json={"nombre": "Operaciones Este", "nombre_corto": "Op. Este"},
                       headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403


def test_actualizar_area_admin_ok(client, auth_admin_headers, area_norte):
    resp = client.patch(f"/api/areas/{area_norte.id}",
                        json={"descripcion": "Cobertura ampliada"},
                        headers=auth_admin_headers)
    assert resp.status_code == 200
    assert resp.json()["descripcion"] == "Cobertura ampliada"


def test_actualizar_area_sin_campos_400(client, auth_admin_headers, area_norte):
    resp = client.patch(f"/api/areas/{area_norte.id}", json={}, headers=auth_admin_headers)
    assert resp.status_code == 400


def test_actualizar_area_404(client, auth_admin_headers):
    resp = client.patch("/api/areas/999", json={"nombre": "X"}, headers=auth_admin_headers)
    assert resp.status_code == 404


def test_actualizar_area_supervisor_403(client, auth_supervisor_norte_headers, area_norte):
    resp = client.patch(f"/api/areas/{area_norte.id}", json={"nombre": "Hackeada"},
                        headers=auth_supervisor_norte_headers)
    assert resp.status_code == 403
