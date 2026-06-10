-- Migración: separar credenciales de choferes en accesos_chofer
-- Ejecutar si la BD tenía choferes mezclados en la tabla usuarios.

CREATE TABLE IF NOT EXISTS accesos_chofer (
    id                  SERIAL PRIMARY KEY,
    chofer_id           INTEGER NOT NULL UNIQUE,
    email               VARCHAR(100) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,
    activo              BOOLEAN NOT NULL DEFAULT TRUE,
    intentos_fallidos   SMALLINT NOT NULL DEFAULT 0,
    bloqueado_hasta     TIMESTAMP,
    ultimo_login        TIMESTAMP,
    creado_por          INTEGER,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_acceso_chofer
        FOREIGN KEY (chofer_id) REFERENCES choferes(id) ON DELETE CASCADE,
    CONSTRAINT fk_acceso_creado_por
        FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_accesos_chofer_email ON accesos_chofer(email);
CREATE INDEX IF NOT EXISTS idx_accesos_chofer_chofer ON accesos_chofer(chofer_id);

-- Migrar cuentas chofer que estuvieran en usuarios
INSERT INTO accesos_chofer (chofer_id, email, password_hash, activo, intentos_fallidos, bloqueado_hasta, ultimo_login, creado_por)
SELECT u.chofer_id, u.email, u.password_hash, u.activo, u.intentos_fallidos, u.bloqueado_hasta, u.ultimo_login, NULL
FROM usuarios u
WHERE u.rol = 'chofer' AND u.chofer_id IS NOT NULL
ON CONFLICT (chofer_id) DO NOTHING;

DELETE FROM usuarios WHERE rol = 'chofer';

-- Restaurar usuarios solo para personal ATU/supervisores
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS fk_usuario_chofer;
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS chk_rol_concesionario_chofer;
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS chk_supervisor_tiene_concesionario;
ALTER TABLE usuarios DROP CONSTRAINT IF EXISTS chk_rol_valido;

ALTER TABLE usuarios DROP COLUMN IF EXISTS chofer_id;

ALTER TABLE usuarios ADD CONSTRAINT chk_rol_valido
    CHECK (rol IN ('admin_atu', 'supervisor_concesionario'));

ALTER TABLE usuarios ADD CONSTRAINT chk_supervisor_tiene_concesionario
    CHECK (
        (rol = 'admin_atu' AND concesionario_id IS NULL) OR
        (rol = 'supervisor_concesionario' AND concesionario_id IS NOT NULL)
    );

DROP INDEX IF EXISTS idx_usuarios_chofer;

-- Semillas demo si aún no existen accesos
INSERT INTO accesos_chofer (chofer_id, email, password_hash, creado_por)
SELECT 1, 'jhuaman@metrohub.gob.pe', '$2b$12$tGuyPseyX10WFRjikZJEk.CANmzW1TRtDZAQHGUm79ujaypT3KpW.', 2
WHERE NOT EXISTS (SELECT 1 FROM accesos_chofer WHERE email = 'jhuaman@metrohub.gob.pe');

INSERT INTO accesos_chofer (chofer_id, email, password_hash, creado_por)
SELECT 2, 'rcastillo@metrohub.gob.pe', '$2b$12$tGuyPseyX10WFRjikZJEk.CANmzW1TRtDZAQHGUm79ujaypT3KpW.', 2
WHERE NOT EXISTS (SELECT 1 FROM accesos_chofer WHERE email = 'rcastillo@metrohub.gob.pe');

INSERT INTO accesos_chofer (chofer_id, email, password_hash, creado_por)
SELECT 6, 'mtorres@metrohub.gob.pe', '$2b$12$tGuyPseyX10WFRjikZJEk.CANmzW1TRtDZAQHGUm79ujaypT3KpW.', 3
WHERE NOT EXISTS (SELECT 1 FROM accesos_chofer WHERE email = 'mtorres@metrohub.gob.pe');
