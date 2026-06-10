# MetroHub

Plataforma web de programación inteligente de horarios y asignación de choferes para el Metropolitano de Lima

> Proyecto universitario — Universidad Nacional de Ingeniería  
> Facultad de Ciencias · Escuela Profesional de Ciencia de la Computación  
> **Versión 2.0 (V2)** · Junio 2026

---

## Tabla de contenidos

- [Descripción general](#descripción-general)
- [Equipo](#equipo)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Requisitos funcionales](#requisitos-funcionales)
- [Requisitos no funcionales](#requisitos-no-funcionales)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Uso del sistema](#uso-del-sistema)
- [Gestión del proyecto — Scrum](#gestión-del-proyecto--scrum)
- [Estado actual — Sprint 2 (V2)](#estado-actual--sprint-2-v2)
- [Roadmap — Sprint 3 (Módulo IA)](#roadmap--sprint-3-módulo-ia)
- [Patrones creacionales](#patrones-creacionales)

---

## Descripción general

MetroHub es una aplicación web de uso **interno y restringido** diseñada para la Autoridad de Transporte Urbano (ATU) de Lima. Reemplaza el flujo manual basado en hojas de cálculo con el que actualmente la ATU programa los horarios del Metropolitano y asigna choferes por ruta y turno.

El sistema **no está orientado al pasajero final** y no expone funcionalidades públicas. El acceso está restringido a redes internas autorizadas o VPN.

### Usuarios del sistema

| Perfil | Rol en BD | Descripción |
|--------|-----------|-------------|
| **Administrador ATU** | `admin_atu` | Configura rutas y estaciones, aprueba programaciones, gestiona áreas operativas, usuarios y flota. Visualiza KPIs globales y genera reportes. Acceso total. |
| **Supervisor de Área** | `supervisor_area` | Gestiona choferes, buses y disponibilidades de su área operativa. Asigna choferes en la grilla (solo su área). Lectura global del sistema; escritura restringida por `area_id`. |
| **Chofer** | `chofer` *(tabla `accesos_chofer`)* | Accede al portal con credenciales personales. Visualiza sus rutas y turnos asignados. Contraseña inicial = DNI; cambio obligatorio en primer ingreso. |

### Áreas operativas (V2)

En la versión 2 el modelo de **concesionarios privados** fue reemplazado por **áreas operativas internas** del Metropolitano:

| ID | Área | Nombre corto |
|----|------|--------------|
| 1 | Operaciones Norte | Op. Norte |
| 2 | Operaciones Sur | Op. Sur |
| 3 | Mantenimiento de Flota | Mantenimiento |
| 4 | Turnos y Guardias | Turnos |

---

## Equipo

| Integrante | Código | Rol |
|------------|--------|-----|
| Erick Daniel Ortega Moran | 20210209H | Líder / Business Analyst — Requisitos, frontend, gestión de backlog |
| Cesar Abrahan Correa Mullisaca | 20220305J | Dev — Backend y fusión frontend-backend |
| Isaac Antonio Martel Balvin | 20231462D | Dev — Backend e integración del sistema |
| Diego Torres Picho | 20204113B | Creacion de DB, QA — Datos de prueba y testing manual |
| Ivett Marinella Mera Amado | 20191471H | QA — Investigación de datos del Metropolitano y testing |

Docente: Prof. Manuel Quispe Torres

---

## Tecnologías

### Frontend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 19 | Framework UI (SPA) |
| Vite | 8 | Bundler y dev server |
| Fetch API (`api.js`) | nativa | Cliente HTTP centralizado con inyección JWT |
| DM Sans + Space Mono | — | Tipografía del sistema |

### Backend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.11+ | Lenguaje principal |
| FastAPI | 0.111+ | API REST (versión API **2.0.0**) |
| SQLAlchemy | 2.0 | ORM conectado a PostgreSQL |
| python-jose | 3.3+ | Autenticación JWT y sesiones |
| passlib + bcrypt | 1.7+ | Hash de contraseñas (factor >= 12) |
| Alembic | 1.13+ | Migraciones de base de datos |

### Base de datos y caché
| Tecnología | Versión | Uso |
|------------|---------|-----|
| PostgreSQL | 16 | Base de datos principal |
| Redis | 7+ | Caché de consultas frecuentes |

### Módulo IA *(planificado — Sprint 3)*
| Tecnología | Uso |
|------------|-----|
| OR-Tools / PuLP | Optimización de asignación de choferes (programación lineal entera) |
| Prophet | Predicción de demanda por ruta, hora y día de la semana |

### DevOps
| Tecnología | Uso |
|------------|-----|
| Docker + Docker Compose | 4 contenedores: backend, frontend, db, redis |
| GitHub | Control de versiones y gestión de ramas |
| Jira (Scrum) | Gestión de sprints y backlog |

---

## Arquitectura

El sistema se organiza en tres capas:

```
Capa de Presentación
├── React 19 SPA (uso interno — red ATU o VPN)
├── Panel Administrador ATU
├── Panel Supervisor de Área
└── Portal Chofer (Mis Rutas)

        HTTPS / API REST

Capa de Negocio
├── FastAPI 2.0 (patrón MVC)
├── Routers: auth, rutas, horarios, choferes, areas, buses, usuarios,
│            dashboard, conflictos, programaciones, disponibilidad, reportes
├── Services: lógica de negocio y queries SQLAlchemy
└── Autenticación JWT + control de roles (admin_atu | supervisor_area | chofer)

        Conexiones internas

Capa de Datos e Inteligencia Artificial
├── PostgreSQL 16 (tablas, triggers, vista v_dashboard_kpis)
├── OR-Tools (optimización de asignación — Sprint 3)
├── Prophet (predicción de demanda — Sprint 3)
└── Redis (caché)
```

### Patrón de Monorepo

Frontend y Backend coexisten en el mismo repositorio, permitiendo:
- Desarrollo paralelo sincronizado
- Testing de integración simplificado
- Deploy coordinado mediante Docker Compose
- Versionado compartido

---

## Requisitos funcionales

### RF01 — Autenticación y Control de Roles
- Login con correo institucional y contraseña (staff) o correo de acceso chofer
- Hash bcrypt con factor >= 12
- Sesión con token JWT (`area_id` incluido para supervisores), expira a las 8 horas
- Bloqueo de cuenta tras 5 intentos fallidos consecutivos
- **Administrador ATU:** acceso total al sistema
- **Supervisor de Área:** lectura global; escritura solo en su `area_id`
- **Chofer:** acceso independiente vía tabla `accesos_chofer`; cambio de contraseña en primer ingreso

### RF02 — Gestión de Rutas y Estaciones
- CRUD completo de rutas: código, nombre, tipo, frecuencia base y horario de operación
- CRUD de estaciones: ubicación geográfica (GPS), tramo y orden troncal
- Activar y desactivar rutas
- Los cambios impactan inmediatamente en el módulo de programación

### RF03 — Programación de Horarios
- Grilla visual interactiva de horarios por ruta, fecha y programación
- Validación en tiempo real: solapamiento de turnos, disponibilidad del chofer, horas máximas (8 h)
- Resolución interactiva de conflictos desde la UI (Administrador ATU)
- Asignación de choferes y buses por turno (admin y supervisor de área)
- Duplicar semana (patrón Prototype) hacia otra fecha de inicio

### RF04 — Gestión de Choferes y Asignación
- Registro de choferes con datos personales, licencia tipo A-III y certificación Protransporte
- Creación automática de acceso al portal (`accesos_chofer`) al registrar un chofer
- Asignación a turnos y rutas con control de horas máximas (8 h/jornada)
- Alertas automáticas de documentos por vencer (licencia y certificación Protransporte)
- Control de disponibilidad e indisponibilidades (descanso, vacaciones, médico, etc.)
- Vista **Mis Rutas** para el chofer con sus asignaciones del día

### RF05 — Optimización con IA *(planificado — Sprint 3)*
- Predicción de demanda por ruta, hora y día con modelo Prophet
- Optimización de asignación de choferes y buses con OR-Tools
- Propuesta automática revisable y aprobable por el Administrador ATU

### RF06 — Dashboard de Indicadores y Reportes
- KPIs operativos actualizados desde la BD: rutas activas, choferes disponibles, buses operativos, conflictos pendientes, certificaciones por vencer en 30 días
- Exportación de reportes en PDF y XLSX (stubs implementados con patrones creacionales)

---

## Requisitos no funcionales

| ID | Nombre | Descripción clave |
|----|--------|-------------------|
| RNF01 | Usabilidad | Programación semanal en <= 15 min. Dashboard <= 2 niveles de menú. WCAG 2.1 AA. |
| RNF02 | Seguridad | HTTPS (TLS 1.2+), bcrypt >= 12, OWASP Top 10, aislamiento por área operativa, Ley 29733. |
| RNF03 | Desempeño | API REST <= 2 s (p95). Validación de conflictos <= 1 s. Propuesta IA <= 30 s. 100 usuarios concurrentes. |
| RNF04 | Disponibilidad | 99% uptime horario operativo (07:00-19:00, lun-sáb). RTO <= 30 min. Funcional sin módulo IA. |
| RNF05 | Mantenibilidad | >= 70% cobertura en módulos críticos. PEP 8 (backend), ESLint (frontend). Arquitectura MVC modular. |
| RNF06 | Portabilidad | Chrome 90+, Firefox 88+, Edge 90+. Responsivo 768px-1920px. Backend en Docker. |

---

## Estructura del proyecto

```
MetroHub/
├── frontend/                          # React 19 + Vite 8
│   ├── src/
│   │   ├── api.js                    # Cliente HTTP centralizado (Fetch + JWT)
│   │   ├── components/
│   │   │   ├── Sidebar.jsx           # Menú lateral por rol
│   │   │   ├── KpiCard.jsx
│   │   │   ├── RouteBar.jsx
│   │   │   ├── AlertPanel.jsx
│   │   │   └── CambioPasswordPrimerIngreso.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx             # RF01 — Autenticación
│   │   │   ├── Dashboard.jsx         # RF06 — KPIs
│   │   │   ├── Grilla.jsx            # RF03 — Horarios + asignaciones
│   │   │   ├── Rutas.jsx             # RF02 — Catálogo de rutas
│   │   │   ├── Choferes.jsx          # RF04 — Choferes + disponibilidad
│   │   │   ├── MisRutas.jsx          # RF04 — Portal chofer
│   │   │   ├── Buses.jsx             # Flota por área operativa
│   │   │   ├── Areas.jsx             # CRUD áreas operativas (admin)
│   │   │   ├── Usuarios.jsx          # Gestión de usuarios staff (admin)
│   │   │   └── Reportes.jsx          # RF06 — Exportación PDF/XLSX
│   │   ├── App.jsx                   # Router SPA + sesión JWT + portal chofer
│   │   └── main.jsx
│   └── Dockerfile
│
├── backend/                           # FastAPI 2.0 + SQLAlchemy
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py               # JWT + login staff/chofer
│   │   │   ├── rutas.py              # RF02
│   │   │   ├── estaciones.py
│   │   │   ├── horarios.py           # RF03 — Programación + asignaciones
│   │   │   ├── programaciones.py
│   │   │   ├── choferes.py           # RF04 + GET /me/asignaciones
│   │   │   ├── disponibilidad.py
│   │   │   ├── buses.py
│   │   │   ├── areas.py              # Áreas operativas
│   │   │   ├── usuarios.py
│   │   │   ├── dashboard.py          # RF06
│   │   │   ├── conflictos.py
│   │   │   └── reportes.py           # RF06
│   │   ├── services/
│   │   ├── models/
│   │   │   ├── area_operativa.py
│   │   │   ├── usuario.py
│   │   │   ├── acceso_chofer.py      # Auth independiente choferes
│   │   │   ├── chofer.py, bus.py, ruta.py, estacion.py
│   │   │   ├── programacion.py, horario_servicio.py
│   │   │   ├── asignacion.py, conflicto.py
│   │   │   └── disponibilidad_chofer.py
│   │   ├── builders/                 # Patrón Builder — RF03
│   │   ├── prototypes/               # Patrón Prototype — RF03
│   │   ├── export/                   # Patrón Factory Method — RF06
│   │   ├── factories/                # Patrón Abstract Factory — RF06
│   │   └── main.py                   # API v2.0.0
│   ├── db/
│   │   ├── schema.sql
│   │   ├── seed.sql                  # Datos demo Metropolitano (jun 2026)
│   │   └── migrations/               # 002_accesos_chofer, 003_debe_cambiar_password
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## Instalación y ejecución

### Prerrequisitos

- Docker Desktop (recomendado)
- O bien: Node.js 20+, Python 3.11+, PostgreSQL 16, Redis 7

### Opción A — Con Docker Compose (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/MetroSmart/Metrohub.git
cd Metrohub

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Levantar todos los servicios
docker compose up --build
```

> **Nota V2:** Si migras desde una versión anterior con concesionarios, recrea el volumen de PostgreSQL:
> `docker compose down -v && docker compose up --build`

Los servicios quedan disponibles en:

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

La base de datos se inicializa automáticamente con `schema.sql` y `seed.sql` al primer arranque.

### Opción B — Solo frontend en desarrollo local

```bash
cd frontend
npm install
npm run dev
```

### Credenciales de demo

| Correo | Contraseña | Rol |
|--------|------------|-----|
| admin.atu@metrohub.gob.pe | admin123 | Administrador ATU |
| sup.norte@metrohub.gob.pe | norte123 | Supervisor — Operaciones Norte |
| sup.sur@metrohub.gob.pe | sur123 | Supervisor — Operaciones Sur |
| sup.mantenimiento@metrohub.gob.pe | mantenimiento123 | Supervisor — Mantenimiento de Flota |
| sup.turnos@metrohub.gob.pe | turnos123 | Supervisor — Turnos y Guardias |

> La cuenta se bloquea tras 5 intentos fallidos consecutivos (RF01).

### Credenciales choferes demo

| Correo | Contraseña | Chofer |
|--------|------------|--------|
| jhuaman@metrohub.gob.pe | 44156789 | Juan Manuel Huamán Flores |
| rcastillo@metrohub.gob.pe | 45892314 | Roberto Castillo Vera |
| mtorres@metrohub.gob.pe | 43678912 | Miguel Ángel Torres Huanca |

> La contraseña inicial del chofer es su DNI. Los choferes demo no requieren cambio de contraseña. Los choferes **nuevos** registrados desde el panel deben cambiarla en su primer ingreso.

---

## Uso del sistema

### 1. Login (RF01)
Accede con tu correo desde la red interna ATU o VPN. El token JWT se almacena localmente y restaura la sesión al recargar. Tres perfiles: Admin ATU, Supervisor de Área y Chofer.

### 2. Dashboard (RF06)
KPIs operativos en tiempo real: rutas activas, choferes disponibles, buses operativos, conflictos pendientes y certificaciones por vencer.

### 3. Rutas (RF02)
Catálogo de rutas del Metropolitano (Regulares A/B/C, Expresos, Nocturna) con tipo, horario y frecuencia.

### 4. Programación / Grilla (RF03)
Visualiza horarios por ruta y fecha. Admin y supervisores pueden asignar choferes y buses. Admin puede resolver conflictos y duplicar semanas.

### 5. Choferes (RF04)
Registro de choferes con alertas de documentos, indisponibilidades y creación automática de acceso al portal. Supervisores gestionan solo choferes de su área.

### 6. Buses
Flota por área operativa. Admin gestiona toda la flota; supervisores gestionan buses de su área.

### 7. Áreas Operativas *(solo Admin)*
CRUD de las divisiones internas del Metropolitano (Operaciones Norte/Sur, Mantenimiento, Turnos).

### 8. Usuarios *(solo Admin)*
Gestión de cuentas staff (`admin_atu` y `supervisor_area`).

### 9. Mis Rutas *(solo Chofer)*
Portal del chofer con sus asignaciones del día (ruta, horario, bus).

### 10. Reportes (RF06)
Exportación PDF/XLSX desde KPIs del dashboard.

### 11. Optimizador IA *(RF05 — Sprint 3)*
Propuestas automáticas de programación con Prophet y OR-Tools. **No implementado en V2.**

---

## Gestión del proyecto — Scrum

El proyecto se gestiona con metodología Scrum con sprints semanales.

- GitHub: https://github.com/MetroSmart/Metrohub
- Rama activa de desarrollo: `fixv2`
- Gestión de backlog: Jira (proyecto SCRUM)

### Product Backlog (resumen)

| Ticket | Historia | Épica | Estado V2 |
|--------|----------|-------|-----------|
| SCRUM-29/28/27 | Autenticación JWT, roles, bloqueo | RF01 | Completado |
| SCRUM-23/22 | CRUD rutas, activar/desactivar | RF02 | Completado |
| SCRUM-19/18 | Grilla, conflictos | RF03 | Completado |
| SCRUM-14/16/15 | Choferes, asignación, alertas | RF04 | Completado |
| SCRUM-25 | Dashboard KPIs | RF06 | Completado |
| SCRUM-26 | Exportación PDF/XLSX | RF06 | Parcial (stubs) |
| SCRUM-20/21 | Prophet + OR-Tools | RF05 | **Sprint 3** |
| — | Portal chofer + áreas operativas | RF01/RF04 | Completado (V2) |

---

## Estado actual — Sprint 2 (V2)

**Versión entregada:** MetroHub **V2.0**  
**Período:** Mayo – Junio 2026  
**Objetivo:** Consolidar roles, portal chofer y modelo de áreas operativas

### Entregables completados en V2

| Módulo | Descripción |
|--------|-------------|
| **Áreas operativas** | Reemplazo de concesionarios por 4 áreas internas ATU |
| **Rol `supervisor_area`** | Permisos por `area_id` en JWT; lectura global, escritura acotada |
| **Portal chofer** | Tabla `accesos_chofer`, vista `MisRutas`, cambio de contraseña en primer ingreso |
| **Gestión ampliada** | Páginas Buses, Usuarios, Áreas Operativas |
| **Grilla** | Supervisores pueden asignar/quitar choferes en su área |
| **Registro chofer** | Campo correo opcional; acceso automático al portal |

### Avance Sprint 2

**17 de 19 ítems core completados — ~89 %**  
Pendientes menores: exportación PDF/XLSX completa, estaciones (parcial).

---

## Roadmap — Sprint 3 (Módulo IA)

**Período planificado:** Junio – Julio 2026  
**Objetivo:** Implementar el módulo de Inteligencia Artificial (RF05) sobre la base operativa de V2

### Alcance planificado

| Componente | Tecnología | Descripción |
|------------|------------|-------------|
| **Predicción de demanda** | Prophet (Meta) | Forecast de pasajeros por ruta, hora y día de la semana |
| **Optimizador de asignación** | OR-Tools (Google) | Propuesta automática de choferes y buses respetando restricciones laborales |
| **API de propuestas** | FastAPI | Endpoints para generar, revisar y aprobar propuestas IA |
| **UI Optimizador** | React | Pantalla para que el Admin ATU revise y aplique propuestas a la grilla |

### Restricciones que el optimizador respetará

- Máximo 8 horas de jornada por chofer
- Sin solapamiento de turnos
- Chofer disponible (sin indisponibilidad registrada)
- Licencia y certificación Protransporte vigentes
- Coherencia chofer–bus–área operativa

### Criterios de aceptación Sprint 3

- [ ] Modelo Prophet entrenado con datos históricos de demanda (seed + datos simulados)
- [ ] Optimizador OR-Tools genera propuesta en <= 30 s (RNF03)
- [ ] Admin puede aprobar o rechazar propuesta desde la UI
- [ ] Sistema funcional sin módulo IA activo (RNF04 — degradación graceful)

> El módulo IA **no forma parte de V2**. La versión actual opera de forma completa sin dependencia de modelos de ML.

---

## Patrones creacionales

Integrados en el backend para el curso de patrones de diseño:

| Patrón | RF | Carpeta | API |
|--------|-----|---------|-----|
| **Builder** | RF03 | `app/builders/` | `POST /api/horarios/programacion-completa` |
| **Prototype** | RF03 | `app/prototypes/` | `POST /api/horarios/duplicar-semana` |
| **Factory Method** | RF06 | `app/export/` | `POST /api/reportes/exportar` |
| **Abstract Factory** | RF06 | `app/factories/` | export con familia ATU |

Detalle técnico: [`backend/docs/PATRONES_CREACIONALES.md`](backend/docs/PATRONES_CREACIONALES.md).

---

## Estándares de código

### Frontend
- Linter: ESLint
- Naming: camelCase (variables), PascalCase (componentes)
- Estructura: funcionales con Hooks
- HTTP: módulo centralizado `api.js` — sin llamadas directas en componentes

### Backend
- Linter: PEP 8
- Framework: FastAPI con patrón MVC
- ORM: SQLAlchemy 2.0
- Documentación: docstrings en español

---

## Contribución

### Rama de trabajo
```bash
git checkout -b SCRUM-XX-descripcion-corta
git add .
git commit -m "SCRUM-XX: descripción clara del cambio"
git push origin SCRUM-XX-descripcion-corta
```

### Pull Request
- Describe qué cambios realizas
- Referencia el ticket Scrum
- Solicita review de un compañero

---

## Referencias

- IEEE Std 830-1998 — Recommended Practice for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2011 — Systems and Software Engineering: Requirements Engineering
- Datos públicos del Metropolitano de Lima — ATU (https://www.atu.gob.pe)
- Ley No. 29733 — Ley de Protección de Datos Personales del Perú
- FastAPI Documentation (https://fastapi.tiangolo.com)
- SQLAlchemy Documentation (https://docs.sqlalchemy.org)
- OR-Tools — Google (https://developers.google.com/optimization)
- Prophet — Meta (https://facebook.github.io/prophet/)

---

MetroHub **V2.0** · Universidad Nacional de Ingeniería · Lima, Perú · 2026
