-- ============================================================
-- MetroHub — Esquema inicial de base de datos
-- PostgreSQL 14+
-- Cubre RF01 (Auth) hasta RF06 (Dashboard) según SRS v2.0
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "citext";

-- ============================================================
-- ENUMS — tipos enumerados
-- ============================================================

DO $$ BEGIN
    CREATE TYPE rol_usuario AS ENUM ('admin_atu', 'supervisor');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE disponibilidad_chofer AS ENUM ('disponible', 'descanso', 'baja_temporal');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE turno_horario AS ENUM ('manana', 'tarde', 'noche');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE estado_unidad AS ENUM ('operativa', 'mantenimiento', 'fuera_servicio');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE estado_horario AS ENUM ('borrador', 'aprobado', 'cancelado');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE tipo_alerta AS ENUM ('licencia_vencida', 'licencia_por_vencer',
                                      'conflicto_horario', 'horas_excedidas',
                                      'unidad_mantenimiento');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE severidad_alerta AS ENUM ('info', 'warning', 'critical');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE estado_propuesta AS ENUM ('generada', 'revisada', 'aprobada', 'rechazada');
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- ============================================================
-- 1. CONCESIONARIOS — Empresas operadoras
-- ============================================================
CREATE TABLE IF NOT EXISTS concesionarios (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(150) UNIQUE NOT NULL,
    ruc             VARCHAR(11) UNIQUE,
    contacto_email  CITEXT,
    contacto_telefono VARCHAR(20),
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 2. USUARIOS — RF01 (Login + roles + bloqueo)
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id                    SERIAL PRIMARY KEY,
    email                 CITEXT UNIQUE NOT NULL,
    password_hash         VARCHAR(255) NOT NULL,
    nombre                VARCHAR(120) NOT NULL,
    rol                   rol_usuario NOT NULL,
    concesionario_id      INTEGER REFERENCES concesionarios(id) ON DELETE SET NULL,
    activo                BOOLEAN NOT NULL DEFAULT TRUE,
    intentos_fallidos     INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta       TIMESTAMPTZ,
    ultimo_acceso         TIMESTAMPTZ,
    creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_supervisor_concesionario
        CHECK (rol = 'admin_atu' OR concesionario_id IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol   ON usuarios(rol);

-- ============================================================
-- 3. INTENTOS_LOGIN — RF01 (Auditoría de accesos)
-- ============================================================
CREATE TABLE IF NOT EXISTS intentos_login (
    id          SERIAL PRIMARY KEY,
    email       CITEXT NOT NULL,
    exitoso     BOOLEAN NOT NULL,
    ip          INET,
    user_agent  VARCHAR(255),
    intentado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_intentos_email_fecha
    ON intentos_login(email, intentado_en DESC);

-- ============================================================
-- 4. ESTACIONES — RF02 (Paraderos)
-- ============================================================
CREATE TABLE IF NOT EXISTS estaciones (
    id                  SERIAL PRIMARY KEY,
    nombre              VARCHAR(120) UNIQUE NOT NULL,
    latitud             NUMERIC(9, 6),
    longitud            NUMERIC(9, 6),
    capacidad_operativa INTEGER NOT NULL DEFAULT 0,
    hora_apertura       TIME NOT NULL DEFAULT '05:00',
    hora_cierre         TIME NOT NULL DEFAULT '23:00',
    dias_servicio       VARCHAR(20) NOT NULL DEFAULT 'L,M,X,J,V,S,D',
    activa              BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 5. RUTAS — RF02
-- ============================================================
CREATE TABLE IF NOT EXISTS rutas (
    id                  SERIAL PRIMARY KEY,
    codigo              VARCHAR(30) UNIQUE NOT NULL,
    nombre              VARCHAR(150) NOT NULL,
    estacion_inicio_id  INTEGER NOT NULL REFERENCES estaciones(id),
    estacion_fin_id     INTEGER NOT NULL REFERENCES estaciones(id),
    frecuencia_base     INTEGER NOT NULL CHECK (frecuencia_base > 0),
    concesionario_id    INTEGER NOT NULL REFERENCES concesionarios(id),
    activa              BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_estaciones_diferentes CHECK (estacion_inicio_id <> estacion_fin_id)
);
CREATE INDEX IF NOT EXISTS idx_rutas_codigo ON rutas(codigo);
CREATE INDEX IF NOT EXISTS idx_rutas_concesionario ON rutas(concesionario_id);

-- ============================================================
-- 6. RUTAS_PARADEROS — RF02 (paraderos intermedios)
-- ============================================================
CREATE TABLE IF NOT EXISTS rutas_paraderos (
    id                   SERIAL PRIMARY KEY,
    ruta_id              INTEGER NOT NULL REFERENCES rutas(id) ON DELETE CASCADE,
    estacion_id          INTEGER NOT NULL REFERENCES estaciones(id),
    orden                INTEGER NOT NULL,
    tiempo_estimado_min  INTEGER NOT NULL DEFAULT 0,
    UNIQUE (ruta_id, orden),
    UNIQUE (ruta_id, estacion_id)
);

-- ============================================================
-- 7. UNIDADES — RF03 (Flota de buses)
-- ============================================================
CREATE TABLE IF NOT EXISTS unidades (
    id                SERIAL PRIMARY KEY,
    placa             VARCHAR(10) UNIQUE NOT NULL,
    modelo            VARCHAR(100),
    capacidad         INTEGER NOT NULL CHECK (capacidad > 0),
    concesionario_id  INTEGER NOT NULL REFERENCES concesionarios(id),
    estado            estado_unidad NOT NULL DEFAULT 'operativa',
    creado_en         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 8. CHOFERES — RF04
-- ============================================================
CREATE TABLE IF NOT EXISTS choferes (
    id                    SERIAL PRIMARY KEY,
    nombre                VARCHAR(100) NOT NULL,
    apellido              VARCHAR(100) NOT NULL,
    dni                   VARCHAR(8) UNIQUE NOT NULL,
    licencia              VARCHAR(20) UNIQUE NOT NULL,
    tipo_licencia         VARCHAR(5) NOT NULL,
    vencimiento_licencia  DATE NOT NULL,
    concesionario_id      INTEGER NOT NULL REFERENCES concesionarios(id),
    disponibilidad        disponibilidad_chofer NOT NULL DEFAULT 'disponible',
    telefono              VARCHAR(20),
    email                 CITEXT,
    creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_choferes_concesionario ON choferes(concesionario_id);
CREATE INDEX IF NOT EXISTS idx_choferes_disponibilidad ON choferes(disponibilidad);
CREATE INDEX IF NOT EXISTS idx_choferes_venc_licencia ON choferes(vencimiento_licencia);

-- ============================================================
-- 9. HORARIOS — RF03 (Slots de programación)
-- ============================================================
CREATE TABLE IF NOT EXISTS horarios (
    id              SERIAL PRIMARY KEY,
    ruta_id         INTEGER NOT NULL REFERENCES rutas(id),
    chofer_id       INTEGER NOT NULL REFERENCES choferes(id),
    unidad_id       INTEGER REFERENCES unidades(id),
    fecha           DATE NOT NULL,
    hora_salida     TIME NOT NULL,
    hora_llegada    TIME NOT NULL,
    turno           turno_horario NOT NULL,
    estado          estado_horario NOT NULL DEFAULT 'borrador',
    conflicto       BOOLEAN NOT NULL DEFAULT FALSE,
    motivo_conflicto VARCHAR(255),
    creado_por      INTEGER REFERENCES usuarios(id),
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_horas_validas CHECK (hora_llegada > hora_salida)
);
CREATE INDEX IF NOT EXISTS idx_horarios_fecha       ON horarios(fecha);
CREATE INDEX IF NOT EXISTS idx_horarios_ruta_fecha  ON horarios(ruta_id, fecha);
CREATE INDEX IF NOT EXISTS idx_horarios_chofer_fecha ON horarios(chofer_id, fecha);
CREATE INDEX IF NOT EXISTS idx_horarios_conflicto   ON horarios(conflicto) WHERE conflicto = TRUE;

-- ============================================================
-- 10. ALERTAS — RF06 (Dashboard)
-- ============================================================
CREATE TABLE IF NOT EXISTS alertas (
    id            SERIAL PRIMARY KEY,
    tipo          tipo_alerta NOT NULL,
    severidad     severidad_alerta NOT NULL DEFAULT 'warning',
    mensaje       VARCHAR(500) NOT NULL,
    entidad_tipo  VARCHAR(30),
    entidad_id    INTEGER,
    leida         BOOLEAN NOT NULL DEFAULT FALSE,
    resuelta      BOOLEAN NOT NULL DEFAULT FALSE,
    creado_en     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_alertas_no_leidas
    ON alertas(creado_en DESC) WHERE leida = FALSE;

-- ============================================================
-- 11. PROPUESTAS_IA — RF05 (Optimizador)
-- ============================================================
CREATE TABLE IF NOT EXISTS propuestas_ia (
    id                  SERIAL PRIMARY KEY,
    fecha_inicio        DATE NOT NULL,
    fecha_fin           DATE NOT NULL,
    parametros          JSONB NOT NULL,
    resultado           JSONB,
    metrica_costo       NUMERIC(12, 2),
    metrica_conflictos  INTEGER,
    estado              estado_propuesta NOT NULL DEFAULT 'generada',
    generada_por        INTEGER REFERENCES usuarios(id),
    aprobada_por        INTEGER REFERENCES usuarios(id),
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aprobada_en         TIMESTAMPTZ,
    CONSTRAINT chk_rango_fechas CHECK (fecha_fin >= fecha_inicio)
);

-- ============================================================
-- TRIGGER — actualizar columnas actualizado_en automáticamente
-- ============================================================
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_usuarios_updated ON usuarios;
CREATE TRIGGER trg_usuarios_updated
    BEFORE UPDATE ON usuarios FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trg_rutas_updated ON rutas;
CREATE TRIGGER trg_rutas_updated
    BEFORE UPDATE ON rutas FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trg_choferes_updated ON choferes;
CREATE TRIGGER trg_choferes_updated
    BEFORE UPDATE ON choferes FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trg_horarios_updated ON horarios;
CREATE TRIGGER trg_horarios_updated
    BEFORE UPDATE ON horarios FOR EACH ROW
    EXECUTE FUNCTION actualizar_timestamp();
