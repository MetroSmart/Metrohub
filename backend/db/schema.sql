-- =============================================================================
-- MetroSmart v2.0 - Script de Creación de Base de Datos
-- Universidad Nacional de Ingeniería - EPCC
-- Motor: PostgreSQL 14+
-- Versión del esquema: v3 (sin módulo IA, con tabla buses)
-- =============================================================================

-- Limpieza si se re-ejecuta
DROP TABLE IF EXISTS conflictos CASCADE;
DROP TABLE IF EXISTS asignaciones CASCADE;
DROP TABLE IF EXISTS horarios_servicio CASCADE;
DROP TABLE IF EXISTS programaciones CASCADE;
DROP TABLE IF EXISTS disponibilidad_chofer CASCADE;
DROP TABLE IF EXISTS buses CASCADE;
DROP TABLE IF EXISTS choferes CASCADE;
DROP TABLE IF EXISTS ruta_estacion CASCADE;
DROP TABLE IF EXISTS estaciones CASCADE;
DROP TABLE IF EXISTS rutas CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS concesionarios CASCADE;

-- =============================================================================
-- DOMINIO 1: IDENTIDAD Y ACCESO (RF01)
-- =============================================================================

CREATE TABLE concesionarios (
    id              SERIAL PRIMARY KEY,
    ruc             VARCHAR(11) NOT NULL UNIQUE,
    razon_social    VARCHAR(150) NOT NULL,
    nombre_corto    VARCHAR(50) NOT NULL,
    telefono        VARCHAR(20),
    email_contacto  VARCHAR(100),
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_ruc_longitud CHECK (LENGTH(ruc) = 11)
);

COMMENT ON TABLE concesionarios IS 'Empresas privadas que operan buses del Metropolitano por contrato con ATU';

CREATE TABLE usuarios (
    id                  SERIAL PRIMARY KEY,
    email               VARCHAR(100) NOT NULL UNIQUE,
    password_hash       VARCHAR(255) NOT NULL,
    nombre              VARCHAR(100) NOT NULL,
    apellidos           VARCHAR(100) NOT NULL,
    dni                 VARCHAR(8) NOT NULL UNIQUE,
    rol                 VARCHAR(30) NOT NULL,
    concesionario_id    INTEGER,
    activo              BOOLEAN NOT NULL DEFAULT TRUE,
    intentos_fallidos   SMALLINT NOT NULL DEFAULT 0,
    bloqueado_hasta     TIMESTAMP,
    ultimo_login        TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_concesionario
        FOREIGN KEY (concesionario_id) REFERENCES concesionarios(id) ON DELETE RESTRICT,
    CONSTRAINT chk_rol_valido
        CHECK (rol IN ('admin_atu', 'supervisor_concesionario')),
    CONSTRAINT chk_supervisor_tiene_concesionario
        CHECK (
            (rol = 'admin_atu' AND concesionario_id IS NULL) OR
            (rol = 'supervisor_concesionario' AND concesionario_id IS NOT NULL)
        ),
    CONSTRAINT chk_dni_longitud CHECK (LENGTH(dni) = 8)
);

COMMENT ON TABLE usuarios IS 'Usuarios con acceso al sistema: Admin ATU o Supervisor de Concesionario (RF01)';
COMMENT ON COLUMN usuarios.password_hash IS 'bcrypt con factor >= 12 (RNF02)';
COMMENT ON COLUMN usuarios.bloqueado_hasta IS 'Se activa tras 5 intentos fallidos (RF01)';

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_rol ON usuarios(rol);
CREATE INDEX idx_usuarios_concesionario ON usuarios(concesionario_id);

-- =============================================================================
-- DOMINIO 2: CATÁLOGO OPERATIVO - RUTAS Y ESTACIONES (RF02)
-- =============================================================================

CREATE TABLE estaciones (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(20) NOT NULL UNIQUE,
    nombre          VARCHAR(100) NOT NULL,
    tipo            VARCHAR(20) NOT NULL,
    tramo           VARCHAR(20) NOT NULL,
    orden_troncal   SMALLINT,
    latitud         DECIMAL(10, 8),
    longitud        DECIMAL(11, 8),
    activa          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_tipo_estacion
        CHECK (tipo IN ('terminal', 'intermedia', 'transferencia')),
    CONSTRAINT chk_tramo
        CHECK (tramo IN ('norte', 'centro', 'sur'))
);

COMMENT ON TABLE estaciones IS 'Estaciones del corredor troncal del Metropolitano';

CREATE INDEX idx_estaciones_tramo ON estaciones(tramo);
CREATE INDEX idx_estaciones_activa ON estaciones(activa);

CREATE TABLE rutas (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(10) NOT NULL UNIQUE,
    nombre          VARCHAR(100) NOT NULL,
    tipo            VARCHAR(20) NOT NULL,
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME NOT NULL,
    frecuencia_min  SMALLINT NOT NULL,
    activa          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_tipo_ruta
        CHECK (tipo IN ('regular', 'expreso', 'nocturna')),
    CONSTRAINT chk_frecuencia
        CHECK (frecuencia_min BETWEEN 2 AND 60)
);

COMMENT ON TABLE rutas IS 'Rutas troncales: Regulares (A, B, C) + Expresos (1-14) + Nocturna';

CREATE INDEX idx_rutas_tipo ON rutas(tipo);
CREATE INDEX idx_rutas_activa ON rutas(activa);

CREATE TABLE ruta_estacion (
    ruta_id         INTEGER NOT NULL,
    estacion_id     INTEGER NOT NULL,
    orden           SMALLINT NOT NULL,
    tiempo_est_min  SMALLINT,
    PRIMARY KEY (ruta_id, estacion_id),
    CONSTRAINT fk_re_ruta FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE CASCADE,
    CONSTRAINT fk_re_estacion FOREIGN KEY (estacion_id) REFERENCES estaciones(id) ON DELETE RESTRICT,
    CONSTRAINT uk_ruta_orden UNIQUE (ruta_id, orden)
);

COMMENT ON TABLE ruta_estacion IS 'Tabla puente: resuelve la relación N:M entre rutas y estaciones con orden';

CREATE INDEX idx_re_ruta ON ruta_estacion(ruta_id);
CREATE INDEX idx_re_estacion ON ruta_estacion(estacion_id);

-- =============================================================================
-- DOMINIO 3: PERSONAL Y FLOTA (RF04)
-- =============================================================================

CREATE TABLE choferes (
    id                      SERIAL PRIMARY KEY,
    dni                     VARCHAR(8) NOT NULL UNIQUE,
    nombres                 VARCHAR(100) NOT NULL,
    apellidos               VARCHAR(100) NOT NULL,
    fecha_nacimiento        DATE NOT NULL,
    telefono                VARCHAR(20),
    email                   VARCHAR(100),
    concesionario_id        INTEGER NOT NULL,
    numero_licencia         VARCHAR(20) NOT NULL UNIQUE,
    tipo_licencia           VARCHAR(10) NOT NULL,
    fec_vence_licencia      DATE NOT NULL,
    fec_vence_certif_prot   DATE NOT NULL,
    estado                  VARCHAR(20) NOT NULL DEFAULT 'activo',
    anios_experiencia       SMALLINT,
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chofer_concesionario
        FOREIGN KEY (concesionario_id) REFERENCES concesionarios(id) ON DELETE RESTRICT,
    CONSTRAINT chk_tipo_licencia
        CHECK (tipo_licencia IN ('A-IIIA', 'A-IIIB', 'A-IIIC')),
    CONSTRAINT chk_estado_chofer
        CHECK (estado IN ('activo', 'suspendido', 'licencia_medica', 'vacaciones', 'inactivo')),
    CONSTRAINT chk_dni_chofer_longitud CHECK (LENGTH(dni) = 8)
);

COMMENT ON TABLE choferes IS 'Choferes de los concesionarios. Requiere licencia profesional A-III + certificación Protransporte anual';
COMMENT ON COLUMN choferes.tipo_licencia IS 'Licencia profesional peruana: A-IIIA/B/C';
COMMENT ON COLUMN choferes.fec_vence_certif_prot IS 'Certificación Protransporte (vigencia 1 año)';

CREATE INDEX idx_choferes_concesionario ON choferes(concesionario_id);
CREATE INDEX idx_choferes_estado ON choferes(estado);
CREATE INDEX idx_choferes_certif ON choferes(fec_vence_certif_prot);

-- Tabla buses: placa como PK (identificador natural, único por diseño vehicular)
CREATE TABLE buses (
    placa               VARCHAR(10) PRIMARY KEY,
    concesionario_id    INTEGER NOT NULL,
    tipo                VARCHAR(20) NOT NULL,
    anio                SMALLINT,
    capacidad_pasajeros SMALLINT,
    estado              VARCHAR(20) NOT NULL DEFAULT 'operativo',
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_bus_concesionario
        FOREIGN KEY (concesionario_id) REFERENCES concesionarios(id) ON DELETE RESTRICT,
    CONSTRAINT chk_tipo_bus
        CHECK (tipo IN ('articulado', 'convencional')),
    CONSTRAINT chk_estado_bus
        CHECK (estado IN ('operativo', 'mantenimiento', 'baja', 'reparacion')),
    CONSTRAINT chk_anio_razonable
        CHECK (anio BETWEEN 1990 AND 2100),
    CONSTRAINT chk_placa_formato
        CHECK (LENGTH(placa) BETWEEN 6 AND 10)
);

COMMENT ON TABLE buses IS 'Flota de buses del Metropolitano. Placa como PK (identificador natural)';
COMMENT ON COLUMN buses.placa IS 'Placa vehicular peruana (formato C1J-999 o similar)';

CREATE INDEX idx_buses_concesionario ON buses(concesionario_id);
CREATE INDEX idx_buses_estado ON buses(estado);
CREATE INDEX idx_buses_tipo ON buses(tipo);

CREATE TABLE disponibilidad_chofer (
    id              SERIAL PRIMARY KEY,
    chofer_id       INTEGER NOT NULL,
    fecha           DATE NOT NULL,
    hora_desde      TIME NOT NULL,
    hora_hasta      TIME NOT NULL,
    motivo          VARCHAR(30) NOT NULL,
    observaciones   TEXT,
    registrado_por  INTEGER NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_disp_chofer
        FOREIGN KEY (chofer_id) REFERENCES choferes(id) ON DELETE CASCADE,
    CONSTRAINT fk_disp_usuario
        FOREIGN KEY (registrado_por) REFERENCES usuarios(id) ON DELETE RESTRICT,
    CONSTRAINT chk_motivo_disp
        CHECK (motivo IN ('descanso', 'vacaciones', 'medico', 'capacitacion', 'personal', 'otro')),
    CONSTRAINT chk_rango_horario
        CHECK (hora_desde < hora_hasta)
);

COMMENT ON TABLE disponibilidad_chofer IS 'Bloques horarios donde el chofer NO está disponible para asignación';

CREATE INDEX idx_disp_chofer_fecha ON disponibilidad_chofer(chofer_id, fecha);

-- =============================================================================
-- DOMINIO 4: PROGRAMACIÓN DE SERVICIO (RF03)
-- =============================================================================

CREATE TABLE programaciones (
    id                  SERIAL PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL,
    fecha_inicio        DATE NOT NULL,
    fecha_fin           DATE NOT NULL,
    estado              VARCHAR(20) NOT NULL DEFAULT 'borrador',
    creado_por          INTEGER NOT NULL,
    aprobado_por        INTEGER,
    fecha_aprobacion    TIMESTAMP,
    observaciones       TEXT,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_prog_creador
        FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE RESTRICT,
    CONSTRAINT fk_prog_aprobador
        FOREIGN KEY (aprobado_por) REFERENCES usuarios(id) ON DELETE RESTRICT,
    CONSTRAINT chk_estado_prog
        CHECK (estado IN ('borrador', 'revision', 'aprobada', 'archivada')),
    CONSTRAINT chk_rango_fechas
        CHECK (fecha_fin >= fecha_inicio)
);

COMMENT ON TABLE programaciones IS 'Contenedor semanal de horarios y asignaciones. Flujo: borrador -> revision -> aprobada';

CREATE INDEX idx_prog_fechas ON programaciones(fecha_inicio, fecha_fin);
CREATE INDEX idx_prog_estado ON programaciones(estado);

CREATE TABLE horarios_servicio (
    id                  SERIAL PRIMARY KEY,
    programacion_id     INTEGER NOT NULL,
    ruta_id             INTEGER NOT NULL,
    fecha               DATE NOT NULL,
    hora_salida         TIME NOT NULL,
    turno               VARCHAR(10) NOT NULL,
    duracion_est_min    SMALLINT NOT NULL,
    activo              BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_hs_programacion
        FOREIGN KEY (programacion_id) REFERENCES programaciones(id) ON DELETE CASCADE,
    CONSTRAINT fk_hs_ruta
        FOREIGN KEY (ruta_id) REFERENCES rutas(id) ON DELETE RESTRICT,
    CONSTRAINT chk_turno
        CHECK (turno IN ('manana', 'tarde', 'noche')),
    CONSTRAINT chk_duracion
        CHECK (duracion_est_min BETWEEN 15 AND 240),
    CONSTRAINT uk_ruta_fecha_hora UNIQUE (ruta_id, fecha, hora_salida)
);

COMMENT ON TABLE horarios_servicio IS 'Slots de salida por ruta y fecha. La grilla visual de RF03 se construye sobre esta tabla.';

CREATE INDEX idx_hs_programacion ON horarios_servicio(programacion_id);
CREATE INDEX idx_hs_ruta_fecha ON horarios_servicio(ruta_id, fecha);
CREATE INDEX idx_hs_fecha_turno ON horarios_servicio(fecha, turno);

CREATE TABLE asignaciones (
    id                  SERIAL PRIMARY KEY,
    horario_id          INTEGER NOT NULL,
    chofer_id           INTEGER NOT NULL,
    bus_placa           VARCHAR(10),
    concesionario_id    INTEGER NOT NULL,
    estado              VARCHAR(15) NOT NULL DEFAULT 'propuesta',
    asignado_por        INTEGER NOT NULL,
    notas               TEXT,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_asig_horario
        FOREIGN KEY (horario_id) REFERENCES horarios_servicio(id) ON DELETE CASCADE,
    CONSTRAINT fk_asig_chofer
        FOREIGN KEY (chofer_id) REFERENCES choferes(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asig_bus
        FOREIGN KEY (bus_placa) REFERENCES buses(placa)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_asig_concesionario
        FOREIGN KEY (concesionario_id) REFERENCES concesionarios(id) ON DELETE RESTRICT,
    CONSTRAINT fk_asig_usuario
        FOREIGN KEY (asignado_por) REFERENCES usuarios(id) ON DELETE RESTRICT,
    CONSTRAINT chk_estado_asig
        CHECK (estado IN ('propuesta', 'confirmada', 'cancelada', 'reemplazada')),
    CONSTRAINT uk_horario_chofer UNIQUE (horario_id, chofer_id)
);

COMMENT ON TABLE asignaciones IS 'Vínculo chofer <-> horario <-> bus. Una asignación puede existir sin bus al inicio.';
COMMENT ON COLUMN asignaciones.bus_placa IS 'FK a buses.placa. NULL permitido hasta confirmar el bus. ON UPDATE CASCADE.';

CREATE INDEX idx_asig_horario ON asignaciones(horario_id);
CREATE INDEX idx_asig_chofer ON asignaciones(chofer_id);
CREATE INDEX idx_asig_bus ON asignaciones(bus_placa);
CREATE INDEX idx_asig_estado ON asignaciones(estado);

CREATE TABLE conflictos (
    id                  SERIAL PRIMARY KEY,
    asignacion_id       INTEGER NOT NULL,
    tipo                VARCHAR(30) NOT NULL,
    severidad           VARCHAR(10) NOT NULL DEFAULT 'media',
    descripcion         TEXT NOT NULL,
    resuelto            BOOLEAN NOT NULL DEFAULT FALSE,
    resuelto_por        INTEGER,
    fecha_resolucion    TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_conf_asignacion
        FOREIGN KEY (asignacion_id) REFERENCES asignaciones(id) ON DELETE CASCADE,
    CONSTRAINT fk_conf_usuario
        FOREIGN KEY (resuelto_por) REFERENCES usuarios(id) ON DELETE SET NULL,
    CONSTRAINT chk_tipo_conflicto
        CHECK (tipo IN (
            'solapamiento_turno',
            'exceso_8h_dia',
            'chofer_no_disponible',
            'licencia_vencida',
            'certif_prot_vencida',
            'descanso_insuficiente',
            'concesionario_incorrecto',
            'bus_no_operativo',
            'otro'
        )),
    CONSTRAINT chk_severidad
        CHECK (severidad IN ('baja', 'media', 'alta', 'critica'))
);

COMMENT ON TABLE conflictos IS 'Conflictos detectados por validación automática del sistema';

CREATE INDEX idx_conf_asignacion ON conflictos(asignacion_id);
CREATE INDEX idx_conf_resuelto ON conflictos(resuelto);

-- =============================================================================
-- TRIGGERS: Auto-actualización de updated_at
-- =============================================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_concesionarios_updated BEFORE UPDATE ON concesionarios
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_usuarios_updated BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_estaciones_updated BEFORE UPDATE ON estaciones
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_rutas_updated BEFORE UPDATE ON rutas
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_choferes_updated BEFORE UPDATE ON choferes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_buses_updated BEFORE UPDATE ON buses
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_prog_updated BEFORE UPDATE ON programaciones
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_hs_updated BEFORE UPDATE ON horarios_servicio
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_asig_updated BEFORE UPDATE ON asignaciones
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- =============================================================================
-- VISTA para el Dashboard (RF06)
-- =============================================================================

CREATE OR REPLACE VIEW v_dashboard_kpis AS
SELECT
    CURRENT_DATE AS fecha,
    (SELECT COUNT(*) FROM rutas WHERE activa = TRUE) AS rutas_activas,
    (SELECT COUNT(*) FROM choferes WHERE estado = 'activo') AS choferes_activos,
    (SELECT COUNT(*) FROM buses WHERE estado = 'operativo') AS buses_operativos,
    (SELECT COUNT(*) FROM asignaciones a
        JOIN horarios_servicio h ON a.horario_id = h.id
        WHERE h.fecha = CURRENT_DATE AND a.estado = 'confirmada') AS asignaciones_hoy,
    (SELECT COUNT(*) FROM conflictos WHERE resuelto = FALSE) AS conflictos_abiertos,
    (SELECT COUNT(*) FROM choferes
        WHERE fec_vence_certif_prot <= CURRENT_DATE + INTERVAL '30 days'
        AND estado = 'activo') AS certif_por_vencer_30d;

COMMENT ON VIEW v_dashboard_kpis IS 'KPIs para el dashboard ejecutivo (RF06). Consulta cada 5 min desde frontend.';

-- =============================================================================
-- FIN DEL SCRIPT DE ESQUEMA
-- =============================================================================
