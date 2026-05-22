--
-- PostgreSQL database dump
--

-- Dumped from database version 17.0
-- Dumped by pg_dump version 17.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.set_updated_at() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: asignaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.asignaciones (
    id integer NOT NULL,
    horario_id integer NOT NULL,
    chofer_id integer NOT NULL,
    bus_placa character varying(10),
    concesionario_id integer NOT NULL,
    estado character varying(15) DEFAULT 'propuesta'::character varying NOT NULL,
    asignado_por integer NOT NULL,
    notas text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_estado_asig CHECK (((estado)::text = ANY ((ARRAY['propuesta'::character varying, 'confirmada'::character varying, 'cancelada'::character varying, 'reemplazada'::character varying])::text[])))
);


ALTER TABLE public.asignaciones OWNER TO postgres;

--
-- Name: TABLE asignaciones; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.asignaciones IS 'Vínculo chofer <-> horario <-> bus. Una asignación puede existir sin bus al inicio.';


--
-- Name: COLUMN asignaciones.bus_placa; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.asignaciones.bus_placa IS 'FK a buses.placa. NULL permitido hasta confirmar el bus. ON UPDATE CASCADE.';


--
-- Name: asignaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.asignaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asignaciones_id_seq OWNER TO postgres;

--
-- Name: asignaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.asignaciones_id_seq OWNED BY public.asignaciones.id;


--
-- Name: buses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.buses (
    placa character varying(10) NOT NULL,
    concesionario_id integer NOT NULL,
    tipo character varying(20) NOT NULL,
    anio smallint,
    capacidad_pasajeros smallint,
    estado character varying(20) DEFAULT 'operativo'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_anio_razonable CHECK (((anio >= 1990) AND (anio <= 2100))),
    CONSTRAINT chk_estado_bus CHECK (((estado)::text = ANY ((ARRAY['operativo'::character varying, 'mantenimiento'::character varying, 'baja'::character varying, 'reparacion'::character varying])::text[]))),
    CONSTRAINT chk_placa_formato CHECK (((length((placa)::text) >= 6) AND (length((placa)::text) <= 10))),
    CONSTRAINT chk_tipo_bus CHECK (((tipo)::text = ANY ((ARRAY['articulado'::character varying, 'convencional'::character varying])::text[])))
);


ALTER TABLE public.buses OWNER TO postgres;

--
-- Name: TABLE buses; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.buses IS 'Flota de buses del Metropolitano. Placa como PK (identificador natural)';


--
-- Name: COLUMN buses.placa; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.buses.placa IS 'Placa vehicular peruana (formato C1J-999 o similar)';


--
-- Name: choferes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.choferes (
    id integer NOT NULL,
    dni character varying(8) NOT NULL,
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    fecha_nacimiento date NOT NULL,
    telefono character varying(20),
    email character varying(100),
    concesionario_id integer NOT NULL,
    numero_licencia character varying(20) NOT NULL,
    tipo_licencia character varying(10) NOT NULL,
    fec_vence_licencia date NOT NULL,
    fec_vence_certif_prot date NOT NULL,
    estado character varying(20) DEFAULT 'activo'::character varying NOT NULL,
    anios_experiencia smallint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_dni_chofer_longitud CHECK ((length((dni)::text) = 8)),
    CONSTRAINT chk_estado_chofer CHECK (((estado)::text = ANY ((ARRAY['activo'::character varying, 'suspendido'::character varying, 'licencia_medica'::character varying, 'vacaciones'::character varying, 'inactivo'::character varying])::text[]))),
    CONSTRAINT chk_tipo_licencia CHECK (((tipo_licencia)::text = ANY ((ARRAY['A-IIIA'::character varying, 'A-IIIB'::character varying, 'A-IIIC'::character varying])::text[])))
);


ALTER TABLE public.choferes OWNER TO postgres;

--
-- Name: TABLE choferes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.choferes IS 'Choferes de los concesionarios. Requiere licencia profesional A-III + certificación Protransporte anual';


--
-- Name: COLUMN choferes.tipo_licencia; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.choferes.tipo_licencia IS 'Licencia profesional peruana: A-IIIA/B/C';


--
-- Name: COLUMN choferes.fec_vence_certif_prot; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.choferes.fec_vence_certif_prot IS 'Certificación Protransporte (vigencia 1 año)';


--
-- Name: choferes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.choferes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.choferes_id_seq OWNER TO postgres;

--
-- Name: choferes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.choferes_id_seq OWNED BY public.choferes.id;


--
-- Name: concesionarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.concesionarios (
    id integer NOT NULL,
    ruc character varying(11) NOT NULL,
    razon_social character varying(150) NOT NULL,
    nombre_corto character varying(50) NOT NULL,
    telefono character varying(20),
    email_contacto character varying(100),
    activo boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_ruc_longitud CHECK ((length((ruc)::text) = 11))
);


ALTER TABLE public.concesionarios OWNER TO postgres;

--
-- Name: TABLE concesionarios; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.concesionarios IS 'Empresas privadas que operan buses del Metropolitano por contrato con ATU';


--
-- Name: concesionarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.concesionarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.concesionarios_id_seq OWNER TO postgres;

--
-- Name: concesionarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.concesionarios_id_seq OWNED BY public.concesionarios.id;


--
-- Name: conflictos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conflictos (
    id integer NOT NULL,
    asignacion_id integer NOT NULL,
    tipo character varying(30) NOT NULL,
    severidad character varying(10) DEFAULT 'media'::character varying NOT NULL,
    descripcion text NOT NULL,
    resuelto boolean DEFAULT false NOT NULL,
    resuelto_por integer,
    fecha_resolucion timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_severidad CHECK (((severidad)::text = ANY ((ARRAY['baja'::character varying, 'media'::character varying, 'alta'::character varying, 'critica'::character varying])::text[]))),
    CONSTRAINT chk_tipo_conflicto CHECK (((tipo)::text = ANY ((ARRAY['solapamiento_turno'::character varying, 'exceso_8h_dia'::character varying, 'chofer_no_disponible'::character varying, 'licencia_vencida'::character varying, 'certif_prot_vencida'::character varying, 'descanso_insuficiente'::character varying, 'concesionario_incorrecto'::character varying, 'bus_no_operativo'::character varying, 'otro'::character varying])::text[])))
);


ALTER TABLE public.conflictos OWNER TO postgres;

--
-- Name: TABLE conflictos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.conflictos IS 'Conflictos detectados por validación automática del sistema';


--
-- Name: conflictos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conflictos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.conflictos_id_seq OWNER TO postgres;

--
-- Name: conflictos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conflictos_id_seq OWNED BY public.conflictos.id;


--
-- Name: disponibilidad_chofer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.disponibilidad_chofer (
    id integer NOT NULL,
    chofer_id integer NOT NULL,
    fecha date NOT NULL,
    hora_desde time without time zone NOT NULL,
    hora_hasta time without time zone NOT NULL,
    motivo character varying(30) NOT NULL,
    observaciones text,
    registrado_por integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_motivo_disp CHECK (((motivo)::text = ANY ((ARRAY['descanso'::character varying, 'vacaciones'::character varying, 'medico'::character varying, 'capacitacion'::character varying, 'personal'::character varying, 'otro'::character varying])::text[]))),
    CONSTRAINT chk_rango_horario CHECK ((hora_desde < hora_hasta))
);


ALTER TABLE public.disponibilidad_chofer OWNER TO postgres;

--
-- Name: TABLE disponibilidad_chofer; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.disponibilidad_chofer IS 'Bloques horarios donde el chofer NO está disponible para asignación';


--
-- Name: disponibilidad_chofer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.disponibilidad_chofer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.disponibilidad_chofer_id_seq OWNER TO postgres;

--
-- Name: disponibilidad_chofer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.disponibilidad_chofer_id_seq OWNED BY public.disponibilidad_chofer.id;


--
-- Name: estaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estaciones (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(100) NOT NULL,
    tipo character varying(20) NOT NULL,
    tramo character varying(20) NOT NULL,
    orden_troncal smallint,
    latitud numeric(10,8),
    longitud numeric(11,8),
    activa boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_tipo_estacion CHECK (((tipo)::text = ANY ((ARRAY['terminal'::character varying, 'intermedia'::character varying, 'transferencia'::character varying])::text[]))),
    CONSTRAINT chk_tramo CHECK (((tramo)::text = ANY ((ARRAY['norte'::character varying, 'centro'::character varying, 'sur'::character varying])::text[])))
);


ALTER TABLE public.estaciones OWNER TO postgres;

--
-- Name: TABLE estaciones; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.estaciones IS 'Estaciones del corredor troncal del Metropolitano';


--
-- Name: estaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estaciones_id_seq OWNER TO postgres;

--
-- Name: estaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estaciones_id_seq OWNED BY public.estaciones.id;


--
-- Name: horarios_servicio; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.horarios_servicio (
    id integer NOT NULL,
    programacion_id integer NOT NULL,
    ruta_id integer NOT NULL,
    fecha date NOT NULL,
    hora_salida time without time zone NOT NULL,
    turno character varying(10) NOT NULL,
    duracion_est_min smallint NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_duracion CHECK (((duracion_est_min >= 15) AND (duracion_est_min <= 240))),
    CONSTRAINT chk_turno CHECK (((turno)::text = ANY ((ARRAY['manana'::character varying, 'tarde'::character varying, 'noche'::character varying])::text[])))
);


ALTER TABLE public.horarios_servicio OWNER TO postgres;

--
-- Name: TABLE horarios_servicio; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.horarios_servicio IS 'Slots de salida por ruta y fecha. La grilla visual de RF03 se construye sobre esta tabla.';


--
-- Name: horarios_servicio_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.horarios_servicio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.horarios_servicio_id_seq OWNER TO postgres;

--
-- Name: horarios_servicio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.horarios_servicio_id_seq OWNED BY public.horarios_servicio.id;


--
-- Name: programaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.programaciones (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    estado character varying(20) DEFAULT 'borrador'::character varying NOT NULL,
    creado_por integer NOT NULL,
    aprobado_por integer,
    fecha_aprobacion timestamp without time zone,
    observaciones text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_estado_prog CHECK (((estado)::text = ANY ((ARRAY['borrador'::character varying, 'revision'::character varying, 'aprobada'::character varying, 'archivada'::character varying])::text[]))),
    CONSTRAINT chk_rango_fechas CHECK ((fecha_fin >= fecha_inicio))
);


ALTER TABLE public.programaciones OWNER TO postgres;

--
-- Name: TABLE programaciones; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.programaciones IS 'Contenedor semanal de horarios y asignaciones. Flujo: borrador -> revision -> aprobada';


--
-- Name: programaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.programaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.programaciones_id_seq OWNER TO postgres;

--
-- Name: programaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.programaciones_id_seq OWNED BY public.programaciones.id;


--
-- Name: ruta_estacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ruta_estacion (
    ruta_id integer NOT NULL,
    estacion_id integer NOT NULL,
    orden smallint NOT NULL,
    tiempo_est_min smallint
);


ALTER TABLE public.ruta_estacion OWNER TO postgres;

--
-- Name: TABLE ruta_estacion; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.ruta_estacion IS 'Tabla puente: resuelve la relación N:M entre rutas y estaciones con orden';


--
-- Name: rutas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rutas (
    id integer NOT NULL,
    codigo character varying(10) NOT NULL,
    nombre character varying(100) NOT NULL,
    tipo character varying(20) NOT NULL,
    hora_inicio time without time zone NOT NULL,
    hora_fin time without time zone NOT NULL,
    frecuencia_min smallint NOT NULL,
    activa boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_frecuencia CHECK (((frecuencia_min >= 2) AND (frecuencia_min <= 60))),
    CONSTRAINT chk_tipo_ruta CHECK (((tipo)::text = ANY ((ARRAY['regular'::character varying, 'expreso'::character varying, 'nocturna'::character varying])::text[])))
);


ALTER TABLE public.rutas OWNER TO postgres;

--
-- Name: TABLE rutas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.rutas IS 'Rutas troncales: Regulares (A, B, C) + Expresos (1-14) + Nocturna';


--
-- Name: rutas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rutas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rutas_id_seq OWNER TO postgres;

--
-- Name: rutas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rutas_id_seq OWNED BY public.rutas.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    email character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    nombre character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    dni character varying(8) NOT NULL,
    rol character varying(30) NOT NULL,
    concesionario_id integer,
    activo boolean DEFAULT true NOT NULL,
    intentos_fallidos smallint DEFAULT 0 NOT NULL,
    bloqueado_hasta timestamp without time zone,
    ultimo_login timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_dni_longitud CHECK ((length((dni)::text) = 8)),
    CONSTRAINT chk_rol_valido CHECK (((rol)::text = ANY ((ARRAY['admin_atu'::character varying, 'supervisor_concesionario'::character varying])::text[]))),
    CONSTRAINT chk_supervisor_tiene_concesionario CHECK (((((rol)::text = 'admin_atu'::text) AND (concesionario_id IS NULL)) OR (((rol)::text = 'supervisor_concesionario'::text) AND (concesionario_id IS NOT NULL))))
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: TABLE usuarios; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.usuarios IS 'Usuarios con acceso al sistema: Admin ATU o Supervisor de Concesionario (RF01)';


--
-- Name: COLUMN usuarios.password_hash; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.usuarios.password_hash IS 'bcrypt con factor >= 12 (RNF02)';


--
-- Name: COLUMN usuarios.bloqueado_hasta; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.usuarios.bloqueado_hasta IS 'Se activa tras 5 intentos fallidos (RF01)';


--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_seq OWNER TO postgres;

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: v_dashboard_kpis; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_dashboard_kpis AS
 SELECT CURRENT_DATE AS fecha,
    ( SELECT count(*) AS count
           FROM public.rutas
          WHERE (rutas.activa = true)) AS rutas_activas,
    ( SELECT count(*) AS count
           FROM public.choferes
          WHERE ((choferes.estado)::text = 'activo'::text)) AS choferes_activos,
    ( SELECT count(*) AS count
           FROM public.buses
          WHERE ((buses.estado)::text = 'operativo'::text)) AS buses_operativos,
    ( SELECT count(*) AS count
           FROM (public.asignaciones a
             JOIN public.horarios_servicio h ON ((a.horario_id = h.id)))
          WHERE ((h.fecha = CURRENT_DATE) AND ((a.estado)::text = 'confirmada'::text))) AS asignaciones_hoy,
    ( SELECT count(*) AS count
           FROM public.conflictos
          WHERE (conflictos.resuelto = false)) AS conflictos_abiertos,
    ( SELECT count(*) AS count
           FROM public.choferes
          WHERE ((choferes.fec_vence_certif_prot <= (CURRENT_DATE + '30 days'::interval)) AND ((choferes.estado)::text = 'activo'::text))) AS certif_por_vencer_30d;


ALTER VIEW public.v_dashboard_kpis OWNER TO postgres;

--
-- Name: VIEW v_dashboard_kpis; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW public.v_dashboard_kpis IS 'KPIs para el dashboard ejecutivo (RF06). Consulta cada 5 min desde frontend.';


--
-- Name: asignaciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones ALTER COLUMN id SET DEFAULT nextval('public.asignaciones_id_seq'::regclass);


--
-- Name: choferes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.choferes ALTER COLUMN id SET DEFAULT nextval('public.choferes_id_seq'::regclass);


--
-- Name: concesionarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concesionarios ALTER COLUMN id SET DEFAULT nextval('public.concesionarios_id_seq'::regclass);


--
-- Name: conflictos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conflictos ALTER COLUMN id SET DEFAULT nextval('public.conflictos_id_seq'::regclass);


--
-- Name: disponibilidad_chofer id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disponibilidad_chofer ALTER COLUMN id SET DEFAULT nextval('public.disponibilidad_chofer_id_seq'::regclass);


--
-- Name: estaciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estaciones ALTER COLUMN id SET DEFAULT nextval('public.estaciones_id_seq'::regclass);


--
-- Name: horarios_servicio id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horarios_servicio ALTER COLUMN id SET DEFAULT nextval('public.horarios_servicio_id_seq'::regclass);


--
-- Name: programaciones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programaciones ALTER COLUMN id SET DEFAULT nextval('public.programaciones_id_seq'::regclass);


--
-- Name: rutas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rutas ALTER COLUMN id SET DEFAULT nextval('public.rutas_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: asignaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.asignaciones (id, horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas, created_at, updated_at) FROM stdin;
1	1	1	C1J-985	1	confirmada	2	Asignación manual por supervisor	2026-04-29 11:49:41.847588	2026-04-29 11:49:41.847588
2	2	2	C1J-986	1	confirmada	2	Asignación manual por supervisor	2026-04-29 11:49:41.847588	2026-04-29 11:49:41.847588
3	3	3	C1J-985	1	propuesta	2	Chofer Pedro Quispe con bus C1J-985 (rotación)	2026-04-29 11:49:41.847588	2026-04-29 11:49:41.847588
4	4	4	C2K-334	1	confirmada	2	Bus convencional asignado	2026-04-29 11:49:41.847588	2026-04-29 11:49:41.847588
5	5	5	\N	1	propuesta	2	Pendiente asignar bus operativo	2026-04-29 11:49:41.847588	2026-04-29 11:49:41.847588
\.


--
-- Data for Name: buses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.buses (placa, concesionario_id, tipo, anio, capacidad_pasajeros, estado, created_at, updated_at) FROM stdin;
C1J-985	1	articulado	2018	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C1J-986	1	articulado	2019	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C1K-112	1	articulado	2020	160	mantenimiento	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C2K-334	1	convencional	2017	80	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C1L-201	2	articulado	2018	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C1L-202	2	articulado	2019	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C1M-450	2	articulado	2021	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C2M-778	2	convencional	2016	80	reparacion	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C3A-001	3	articulado	2017	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C3A-002	3	articulado	2018	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C3B-123	3	articulado	2020	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C4B-556	3	convencional	2018	80	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C5D-701	4	articulado	2019	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C5D-702	4	articulado	2020	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C5E-890	4	articulado	2021	160	operativo	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
C6E-109	4	convencional	2017	80	mantenimiento	2026-04-29 11:49:41.841343	2026-04-29 11:49:41.841343
\.


--
-- Data for Name: choferes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.choferes (id, dni, nombres, apellidos, fecha_nacimiento, telefono, email, concesionario_id, numero_licencia, tipo_licencia, fec_vence_licencia, fec_vence_certif_prot, estado, anios_experiencia, created_at, updated_at) FROM stdin;
1	44156789	Juan Manuel	Huamán Flores	1985-03-12	987654321	jhuaman@limaviasexpress.pe	1	Q12345678	A-IIIA	2027-06-30	2026-08-15	activo	12	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
2	45892314	Roberto	Castillo Vera	1979-11-23	987123456	rcastillo@limaviasexpress.pe	1	Q23456789	A-IIIA	2026-12-15	2026-05-20	activo	15	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
3	46789012	Pedro	Quispe Mendoza	1988-07-04	986543210	pquispe@limaviasexpress.pe	1	Q34567890	A-IIIC	2027-03-10	2026-11-02	activo	8	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
4	42345678	Luis Alberto	Gonzales Pariona	1975-02-18	985432109	lgonzales@limaviasexpress.pe	1	Q45678901	A-IIIA	2026-09-25	2026-07-18	activo	20	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
5	47234567	Cinthia	Soldevilla Ríos	1986-09-15	984321098	csoldevilla@limaviasexpress.pe	1	Q56789012	A-IIIC	2028-01-20	2027-02-10	activo	6	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
6	43678912	Miguel Ángel	Torres Huanca	1982-05-30	983210987	mtorres@limabus.pe	2	Q67890123	A-IIIA	2026-11-12	2026-06-25	activo	14	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
7	44987654	Cesar	Ramos Vilca	1990-12-08	982109876	cramos@limabus.pe	2	Q78901234	A-IIIC	2027-08-05	2026-09-30	activo	5	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
8	45123698	Walter	Gálvez Mamani	1984-04-22	981098765	wgalvez@limabus.pe	2	Q89012345	A-IIIA	2027-05-18	2026-04-28	vacaciones	11	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
9	46456789	Arturo	Napa Marcos	1972-08-11	980987654	anapa@limabus.pe	2	Q90123456	A-IIIC	2026-10-30	2026-12-15	activo	22	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
10	43852147	Ricardo	Suárez Ccopa	1987-01-25	979876543	rsuarez@limabus.pe	2	Q01234567	A-IIIA	2027-11-08	2027-01-22	activo	9	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
11	44963852	Fernando	Huertas Ayala	1981-06-14	978765432	fhuertas@transvial.pe	3	Q11122233	A-IIIA	2026-08-22	2026-05-10	activo	13	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
12	45741963	Víctor	Mellado Ramírez	1976-10-02	977654321	vmellado@transvial.pe	3	Q22233344	A-IIIA	2027-02-14	2026-10-18	activo	18	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
13	46258147	Eduardo	Pérez Condori	1989-03-19	976543210	eperez@transvial.pe	3	Q33344455	A-IIIC	2027-07-26	2026-08-30	activo	7	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
14	43159753	Hugo	Valencia Chávez	1978-12-05	975432109	hvalencia@transvial.pe	3	Q44455566	A-IIIA	2026-07-11	2026-03-25	licencia_medica	16	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
15	47852963	Junior	Córdova Fernández	1991-08-28	974321098	jcordova@transvial.pe	3	Q55566677	A-IIIC	2028-04-03	2027-03-15	activo	4	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
16	44753159	Alberto	Paredes Yupanqui	1983-11-17	973210987	aparedes@perumasivo.pe	4	Q66677788	A-IIIA	2027-01-29	2026-06-12	activo	11	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
17	45951357	Daniel	Rojas Limachi	1986-02-09	972109876	drojas@perumasivo.pe	4	Q77788899	A-IIIA	2026-12-06	2026-09-05	activo	10	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
18	46357159	Raúl	Cárdenas Pérez	1980-07-21	971098765	rcardenas@perumasivo.pe	4	Q88899900	A-IIIC	2027-06-14	2026-04-08	activo	15	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
19	43951753	Enrique	Lozano Machaca	1974-05-06	970987654	elozano@perumasivo.pe	4	Q99900011	A-IIIA	2026-09-17	2026-11-25	activo	21	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
20	47159951	Jorge Luis	Tello Quiñones	1988-10-31	969876543	jtello@perumasivo.pe	4	Q00011122	A-IIIC	2027-12-22	2027-04-30	activo	7	2026-04-29 11:49:41.838009	2026-04-29 11:49:41.838009
\.


--
-- Data for Name: concesionarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.concesionarios (id, ruc, razon_social, nombre_corto, telefono, email_contacto, activo, created_at, updated_at) FROM stdin;
1	20513967720	Lima Vías Express S.A.	Lima Vías Express	014567890	contacto@limaviasexpress.pe	t	2026-04-29 11:49:41.819243	2026-04-29 11:49:41.819243
2	20524893451	Lima Bus Internacional S.A.	Lima Bus	014789012	operaciones@limabus.pe	t	2026-04-29 11:49:41.819243	2026-04-29 11:49:41.819243
3	20545678901	Transvial Lima S.A.C.	Transvial	014234567	contacto@transvial.pe	t	2026-04-29 11:49:41.819243	2026-04-29 11:49:41.819243
4	20556789234	Perú Masivo S.A.	Perú Masivo	014345678	info@perumasivo.pe	t	2026-04-29 11:49:41.819243	2026-04-29 11:49:41.819243
\.


--
-- Data for Name: conflictos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conflictos (id, asignacion_id, tipo, severidad, descripcion, resuelto, resuelto_por, fecha_resolucion, created_at) FROM stdin;
1	4	certif_prot_vencida	alta	La certificación Protransporte del chofer Luis Gonzales vence el 2026-07-18, dentro de 90 días.	f	\N	\N	2026-04-29 11:49:41.852236
\.


--
-- Data for Name: disponibilidad_chofer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.disponibilidad_chofer (id, chofer_id, fecha, hora_desde, hora_hasta, motivo, observaciones, registrado_por, created_at) FROM stdin;
1	8	2026-04-21	00:00:00	23:59:00	vacaciones	Vacaciones programadas Abr 18-25	3	2026-04-29 11:49:41.850887
2	8	2026-04-22	00:00:00	23:59:00	vacaciones	Vacaciones programadas Abr 18-25	3	2026-04-29 11:49:41.850887
\.


--
-- Data for Name: estaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.estaciones (id, codigo, nombre, tipo, tramo, orden_troncal, latitud, longitud, activa, created_at, updated_at) FROM stdin;
1	EST-CHO	Chimpu Ocllo	terminal	norte	1	-11.87480000	-77.02950000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
2	EST-LIN	Los Incas	intermedia	norte	2	-11.94800000	-77.05300000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
3	EST-UNI	Universidad	intermedia	norte	3	-11.98500000	-77.05800000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
4	EST-NAR	Naranjal	terminal	norte	4	-11.99100000	-77.06100000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
5	EST-IZA	Izaguirre	intermedia	norte	5	-11.99700000	-77.06400000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
6	EST-PAC	Pacífico	intermedia	norte	6	-12.00200000	-77.06000000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
7	EST-INA	Independencia	intermedia	norte	7	-12.00900000	-77.05700000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
8	EST-TV	Tomás Valle	intermedia	norte	8	-12.01500000	-77.05400000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
9	EST-CAQ	Caquetá	intermedia	centro	9	-12.02800000	-77.04800000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
10	EST-PP	Parque del Trabajo	intermedia	centro	10	-12.03500000	-77.04500000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
11	EST-RCA	Ramón Castilla	intermedia	centro	11	-12.04200000	-77.04100000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
12	EST-TAC	Tacna	intermedia	centro	12	-12.04800000	-77.03700000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
13	EST-JDU	Jirón de la Unión	intermedia	centro	13	-12.05100000	-77.03400000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
14	EST-COL	Colmena	intermedia	centro	14	-12.05400000	-77.03200000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
15	EST-CEN	Estación Central	transferencia	centro	15	-12.05800000	-77.03000000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
16	EST-ENA	Estadio Nacional	intermedia	centro	16	-12.06700000	-77.03200000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
17	EST-MEX	México	intermedia	centro	17	-12.07400000	-77.02900000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
18	EST-CAN	Canadá	intermedia	centro	18	-12.08100000	-77.02600000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
19	EST-JAV	Javier Prado	intermedia	sur	19	-12.09000000	-77.02100000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
20	EST-CYM	Canaval y Moreyra	intermedia	sur	20	-12.09700000	-77.02000000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
21	EST-ARA	Aramburú	intermedia	sur	21	-12.10400000	-77.01900000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
22	EST-DOM	Domingo Orué	intermedia	sur	22	-12.10900000	-77.02100000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
23	EST-ANG	Angamos	intermedia	sur	23	-12.11400000	-77.02300000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
24	EST-RPA	Ricardo Palma	intermedia	sur	24	-12.12000000	-77.02700000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
25	EST-BEN	Benavides	intermedia	sur	25	-12.12600000	-77.03100000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
26	EST-28J	28 de Julio	intermedia	sur	26	-12.13200000	-77.02900000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
27	EST-PFL	Plaza de Flores	intermedia	sur	27	-12.13800000	-77.02700000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
28	EST-MAT	Matellini	terminal	sur	28	-12.18100000	-77.01400000	t	2026-04-29 11:49:41.829595	2026-04-29 11:49:41.829595
\.


--
-- Data for Name: horarios_servicio; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.horarios_servicio (id, programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min, activo, created_at, updated_at) FROM stdin;
1	1	1	2026-04-21	05:00:00	manana	35	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
2	1	1	2026-04-21	05:30:00	manana	35	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
3	1	1	2026-04-21	06:00:00	manana	40	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
4	1	1	2026-04-21	06:30:00	manana	40	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
5	1	1	2026-04-21	07:00:00	manana	45	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
6	1	1	2026-04-21	13:00:00	tarde	40	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
7	1	1	2026-04-21	13:30:00	tarde	40	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
8	1	1	2026-04-21	14:00:00	tarde	40	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
9	1	1	2026-04-21	18:00:00	tarde	45	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
10	1	1	2026-04-21	18:30:00	tarde	45	t	2026-04-29 11:49:41.84502	2026-04-29 11:49:41.84502
\.


--
-- Data for Name: programaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.programaciones (id, nombre, fecha_inicio, fecha_fin, estado, creado_por, aprobado_por, fecha_aprobacion, observaciones, created_at, updated_at) FROM stdin;
1	Semana 17 - Abril 2026	2026-04-20	2026-04-26	borrador	1	\N	\N	Programación inicial para validación del sistema	2026-04-29 11:49:41.843554	2026-04-29 11:49:41.843554
\.


--
-- Data for Name: ruta_estacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.ruta_estacion (ruta_id, estacion_id, orden, tiempo_est_min) FROM stdin;
1	4	1	0
1	5	2	3
1	6	3	6
1	7	4	9
1	8	5	12
1	9	6	16
1	10	7	19
1	11	8	22
1	12	9	25
1	13	10	28
1	14	11	31
1	15	12	35
3	11	1	0
3	12	2	3
3	13	3	6
3	14	4	9
3	15	5	12
3	16	6	17
3	17	7	21
3	18	8	25
3	19	9	30
3	20	10	34
3	21	11	38
3	22	12	42
3	23	13	46
3	24	14	50
3	25	15	54
3	26	16	58
3	27	17	62
3	28	18	75
4	4	1	0
4	15	2	25
4	16	3	30
4	19	4	38
4	20	5	42
4	23	6	48
4	26	7	55
4	28	8	68
\.


--
-- Data for Name: rutas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.rutas (id, codigo, nombre, tipo, hora_inicio, hora_fin, frecuencia_min, activa, created_at, updated_at) FROM stdin;
1	A	Ruta A - Naranjal a Estación Central	regular	05:00:00	22:30:00	6	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
2	B	Ruta B - Naranjal a Plaza de Flores	regular	05:00:00	22:30:00	8	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
3	C	Ruta C - Ramón Castilla a Matellini	regular	05:00:00	22:30:00	8	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
4	EX1	Expreso 1 - Naranjal a Matellini	expreso	05:30:00	21:30:00	5	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
5	EX2	Expreso 2 - Naranjal a Ricardo Palma	expreso	05:30:00	21:30:00	6	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
6	EX5	Expreso 5 - Naranjal a Angamos	expreso	05:30:00	21:30:00	6	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
7	EX7	Expreso 7 - Tomás Valle a Angamos	expreso	06:00:00	21:00:00	8	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
8	EX8	Expreso 8 - Naranjal a Benavides	expreso	05:30:00	21:30:00	7	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
9	EX9	Expreso 9 - Naranjal a Benavides (semidirecto)	expreso	05:30:00	21:30:00	7	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
10	N	Ruta Nocturna - Naranjal a Matellini	nocturna	23:30:00	04:00:00	20	t	2026-04-29 11:49:41.832729	2026-04-29 11:49:41.832729
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id, email, password_hash, nombre, apellidos, dni, rol, concesionario_id, activo, intentos_fallidos, bloqueado_hasta, ultimo_login, created_at, updated_at) FROM stdin;
1	admin.atu@metrosmart.gob.pe	$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef	María	Quispe Rivera	72839401	admin_atu	\N	t	0	\N	\N	2026-04-29 11:49:41.824237	2026-04-29 11:49:41.824237
2	sup.limavias@metrosmart.gob.pe	$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef	Carlos	Ramírez Torres	45892013	supervisor_concesionario	1	t	0	\N	\N	2026-04-29 11:49:41.824237	2026-04-29 11:49:41.824237
3	sup.limabus@metrosmart.gob.pe	$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef	Lucía	Morales Salinas	41203987	supervisor_concesionario	2	t	0	\N	\N	2026-04-29 11:49:41.824237	2026-04-29 11:49:41.824237
4	sup.transvial@metrosmart.gob.pe	$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef	Jorge	Vega Mendoza	43897201	supervisor_concesionario	3	t	0	\N	\N	2026-04-29 11:49:41.824237	2026-04-29 11:49:41.824237
5	sup.perumasivo@metrosmart.gob.pe	$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef	Ana	Ccahuana Pérez	47123890	supervisor_concesionario	4	t	0	\N	\N	2026-04-29 11:49:41.824237	2026-04-29 11:49:41.824237
\.


--
-- Name: asignaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.asignaciones_id_seq', 5, true);


--
-- Name: choferes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.choferes_id_seq', 20, true);


--
-- Name: concesionarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.concesionarios_id_seq', 4, true);


--
-- Name: conflictos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.conflictos_id_seq', 1, true);


--
-- Name: disponibilidad_chofer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.disponibilidad_chofer_id_seq', 2, true);


--
-- Name: estaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.estaciones_id_seq', 28, true);


--
-- Name: horarios_servicio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.horarios_servicio_id_seq', 10, true);


--
-- Name: programaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.programaciones_id_seq', 1, true);


--
-- Name: rutas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.rutas_id_seq', 10, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 5, true);


--
-- Name: asignaciones asignaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones
    ADD CONSTRAINT asignaciones_pkey PRIMARY KEY (id);


--
-- Name: buses buses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.buses
    ADD CONSTRAINT buses_pkey PRIMARY KEY (placa);


--
-- Name: choferes choferes_dni_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.choferes
    ADD CONSTRAINT choferes_dni_key UNIQUE (dni);


--
-- Name: choferes choferes_numero_licencia_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.choferes
    ADD CONSTRAINT choferes_numero_licencia_key UNIQUE (numero_licencia);


--
-- Name: choferes choferes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.choferes
    ADD CONSTRAINT choferes_pkey PRIMARY KEY (id);


--
-- Name: concesionarios concesionarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concesionarios
    ADD CONSTRAINT concesionarios_pkey PRIMARY KEY (id);


--
-- Name: concesionarios concesionarios_ruc_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.concesionarios
    ADD CONSTRAINT concesionarios_ruc_key UNIQUE (ruc);


--
-- Name: conflictos conflictos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conflictos
    ADD CONSTRAINT conflictos_pkey PRIMARY KEY (id);


--
-- Name: disponibilidad_chofer disponibilidad_chofer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disponibilidad_chofer
    ADD CONSTRAINT disponibilidad_chofer_pkey PRIMARY KEY (id);


--
-- Name: estaciones estaciones_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estaciones
    ADD CONSTRAINT estaciones_codigo_key UNIQUE (codigo);


--
-- Name: estaciones estaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estaciones
    ADD CONSTRAINT estaciones_pkey PRIMARY KEY (id);


--
-- Name: horarios_servicio horarios_servicio_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horarios_servicio
    ADD CONSTRAINT horarios_servicio_pkey PRIMARY KEY (id);


--
-- Name: programaciones programaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programaciones
    ADD CONSTRAINT programaciones_pkey PRIMARY KEY (id);


--
-- Name: ruta_estacion ruta_estacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ruta_estacion
    ADD CONSTRAINT ruta_estacion_pkey PRIMARY KEY (ruta_id, estacion_id);


--
-- Name: rutas rutas_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rutas
    ADD CONSTRAINT rutas_codigo_key UNIQUE (codigo);


--
-- Name: rutas rutas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rutas
    ADD CONSTRAINT rutas_pkey PRIMARY KEY (id);


--
-- Name: asignaciones uk_horario_chofer; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones
    ADD CONSTRAINT uk_horario_chofer UNIQUE (horario_id, chofer_id);


--
-- Name: horarios_servicio uk_ruta_fecha_hora; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horarios_servicio
    ADD CONSTRAINT uk_ruta_fecha_hora UNIQUE (ruta_id, fecha, hora_salida);


--
-- Name: ruta_estacion uk_ruta_orden; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ruta_estacion
    ADD CONSTRAINT uk_ruta_orden UNIQUE (ruta_id, orden);


--
-- Name: usuarios usuarios_dni_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_dni_key UNIQUE (dni);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: idx_asig_bus; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_asig_bus ON public.asignaciones USING btree (bus_placa);


--
-- Name: idx_asig_chofer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_asig_chofer ON public.asignaciones USING btree (chofer_id);


--
-- Name: idx_asig_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_asig_estado ON public.asignaciones USING btree (estado);


--
-- Name: idx_asig_horario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_asig_horario ON public.asignaciones USING btree (horario_id);


--
-- Name: idx_buses_concesionario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_buses_concesionario ON public.buses USING btree (concesionario_id);


--
-- Name: idx_buses_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_buses_estado ON public.buses USING btree (estado);


--
-- Name: idx_buses_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_buses_tipo ON public.buses USING btree (tipo);


--
-- Name: idx_choferes_certif; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_choferes_certif ON public.choferes USING btree (fec_vence_certif_prot);


--
-- Name: idx_choferes_concesionario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_choferes_concesionario ON public.choferes USING btree (concesionario_id);


--
-- Name: idx_choferes_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_choferes_estado ON public.choferes USING btree (estado);


--
-- Name: idx_conf_asignacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_conf_asignacion ON public.conflictos USING btree (asignacion_id);


--
-- Name: idx_conf_resuelto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_conf_resuelto ON public.conflictos USING btree (resuelto);


--
-- Name: idx_disp_chofer_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_disp_chofer_fecha ON public.disponibilidad_chofer USING btree (chofer_id, fecha);


--
-- Name: idx_estaciones_activa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_estaciones_activa ON public.estaciones USING btree (activa);


--
-- Name: idx_estaciones_tramo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_estaciones_tramo ON public.estaciones USING btree (tramo);


--
-- Name: idx_hs_fecha_turno; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_hs_fecha_turno ON public.horarios_servicio USING btree (fecha, turno);


--
-- Name: idx_hs_programacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_hs_programacion ON public.horarios_servicio USING btree (programacion_id);


--
-- Name: idx_hs_ruta_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_hs_ruta_fecha ON public.horarios_servicio USING btree (ruta_id, fecha);


--
-- Name: idx_prog_estado; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prog_estado ON public.programaciones USING btree (estado);


--
-- Name: idx_prog_fechas; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prog_fechas ON public.programaciones USING btree (fecha_inicio, fecha_fin);


--
-- Name: idx_re_estacion; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_re_estacion ON public.ruta_estacion USING btree (estacion_id);


--
-- Name: idx_re_ruta; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_re_ruta ON public.ruta_estacion USING btree (ruta_id);


--
-- Name: idx_rutas_activa; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_rutas_activa ON public.rutas USING btree (activa);


--
-- Name: idx_rutas_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_rutas_tipo ON public.rutas USING btree (tipo);


--
-- Name: idx_usuarios_concesionario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_concesionario ON public.usuarios USING btree (concesionario_id);


--
-- Name: idx_usuarios_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: idx_usuarios_rol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_usuarios_rol ON public.usuarios USING btree (rol);


--
-- Name: asignaciones trg_asig_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_asig_updated BEFORE UPDATE ON public.asignaciones FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: buses trg_buses_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_buses_updated BEFORE UPDATE ON public.buses FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: choferes trg_choferes_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_choferes_updated BEFORE UPDATE ON public.choferes FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: concesionarios trg_concesionarios_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_concesionarios_updated BEFORE UPDATE ON public.concesionarios FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: estaciones trg_estaciones_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_estaciones_updated BEFORE UPDATE ON public.estaciones FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: horarios_servicio trg_hs_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_hs_updated BEFORE UPDATE ON public.horarios_servicio FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: programaciones trg_prog_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_prog_updated BEFORE UPDATE ON public.programaciones FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: rutas trg_rutas_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_rutas_updated BEFORE UPDATE ON public.rutas FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: usuarios trg_usuarios_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_usuarios_updated BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: asignaciones fk_asig_bus; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones
    ADD CONSTRAINT fk_asig_bus FOREIGN KEY (bus_placa) REFERENCES public.buses(placa) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: asignaciones fk_asig_chofer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones
    ADD CONSTRAINT fk_asig_chofer FOREIGN KEY (chofer_id) REFERENCES public.choferes(id) ON DELETE RESTRICT;


--
-- Name: asignaciones fk_asig_concesionario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones
    ADD CONSTRAINT fk_asig_concesionario FOREIGN KEY (concesionario_id) REFERENCES public.concesionarios(id) ON DELETE RESTRICT;


--
-- Name: asignaciones fk_asig_horario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones
    ADD CONSTRAINT fk_asig_horario FOREIGN KEY (horario_id) REFERENCES public.horarios_servicio(id) ON DELETE CASCADE;


--
-- Name: asignaciones fk_asig_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.asignaciones
    ADD CONSTRAINT fk_asig_usuario FOREIGN KEY (asignado_por) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- Name: buses fk_bus_concesionario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.buses
    ADD CONSTRAINT fk_bus_concesionario FOREIGN KEY (concesionario_id) REFERENCES public.concesionarios(id) ON DELETE RESTRICT;


--
-- Name: choferes fk_chofer_concesionario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.choferes
    ADD CONSTRAINT fk_chofer_concesionario FOREIGN KEY (concesionario_id) REFERENCES public.concesionarios(id) ON DELETE RESTRICT;


--
-- Name: conflictos fk_conf_asignacion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conflictos
    ADD CONSTRAINT fk_conf_asignacion FOREIGN KEY (asignacion_id) REFERENCES public.asignaciones(id) ON DELETE CASCADE;


--
-- Name: conflictos fk_conf_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conflictos
    ADD CONSTRAINT fk_conf_usuario FOREIGN KEY (resuelto_por) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: disponibilidad_chofer fk_disp_chofer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disponibilidad_chofer
    ADD CONSTRAINT fk_disp_chofer FOREIGN KEY (chofer_id) REFERENCES public.choferes(id) ON DELETE CASCADE;


--
-- Name: disponibilidad_chofer fk_disp_usuario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.disponibilidad_chofer
    ADD CONSTRAINT fk_disp_usuario FOREIGN KEY (registrado_por) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- Name: horarios_servicio fk_hs_programacion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horarios_servicio
    ADD CONSTRAINT fk_hs_programacion FOREIGN KEY (programacion_id) REFERENCES public.programaciones(id) ON DELETE CASCADE;


--
-- Name: horarios_servicio fk_hs_ruta; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.horarios_servicio
    ADD CONSTRAINT fk_hs_ruta FOREIGN KEY (ruta_id) REFERENCES public.rutas(id) ON DELETE RESTRICT;


--
-- Name: programaciones fk_prog_aprobador; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programaciones
    ADD CONSTRAINT fk_prog_aprobador FOREIGN KEY (aprobado_por) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- Name: programaciones fk_prog_creador; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programaciones
    ADD CONSTRAINT fk_prog_creador FOREIGN KEY (creado_por) REFERENCES public.usuarios(id) ON DELETE RESTRICT;


--
-- Name: ruta_estacion fk_re_estacion; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ruta_estacion
    ADD CONSTRAINT fk_re_estacion FOREIGN KEY (estacion_id) REFERENCES public.estaciones(id) ON DELETE RESTRICT;


--
-- Name: ruta_estacion fk_re_ruta; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ruta_estacion
    ADD CONSTRAINT fk_re_ruta FOREIGN KEY (ruta_id) REFERENCES public.rutas(id) ON DELETE CASCADE;


--
-- Name: usuarios fk_usuario_concesionario; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT fk_usuario_concesionario FOREIGN KEY (concesionario_id) REFERENCES public.concesionarios(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

