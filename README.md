# MetroHub 🚌

**Plataforma web de programación inteligente de horarios y asignación de choferes para el Metropolitano de Lima**

> Proyecto universitario — Universidad Nacional de Ingeniería  
> Facultad de Ciencias · Escuela Profesional de Ciencia de la Computación  
> Versión 2.0 · Abril 2026

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
- [Estado actual del sprint](#estado-actual-del-sprint)

---

## Descripción general

MetroHub es una aplicación web de uso interno restringido orientada a los administradores de la **Autoridad de Transporte Urbano (ATU)** y a los supervisores de los concesionarios de buses del Metropolitano de Lima.

Reemplaza el flujo manual basado en hojas de cálculo (Excel / Google Sheets) con el que la ATU programa horarios de servicio y asigna choferes por ruta y estación. El sistema incorpora un módulo de **Inteligencia Artificial** que genera propuestas de programación óptimas usando modelos de optimización y predicción de demanda.

### Usuarios del sistema

| Perfil | Descripción |
|--------|-------------|
| **Administrador ATU** | Planifica y aprueba la programación global de rutas, horarios y choferes. Acceso total. |
| **Supervisor de Concesionario** | Registra disponibilidad de su flota y choferes. Visualiza su programación aprobada. Acceso limitado a su concesionario. |

> El sistema **no** tiene interfaz para pasajeros en esta versión.

---

## Equipo

| Integrante | Código | Rol |
|------------|--------|-----|
| Erick Daniel Ortega Moran | 20210209H | Líder / Backend Dev — Arquitectura, API REST, módulo IA |
| Cesar Abrahan Correa Mullisaca | 20220305J | Frontend Dev / UX — Interfaz web y dashboard |
| Isaac Antonio Martel Balvin | 20231462D | Data Eng. / Docs — Pipeline de datos, SRS, pruebas de integración |
| Diego Torres Picho | 20204113B | Colaborador — Soporte frontend y testing manual |
| Ivett Marinella Mera Amado | 20191471H | Colaborador — Documentación y diseño de BD |

**Docente:** Prof. Manuel Quispe Torres

---

## Tecnologías

### Frontend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 18+ | Framework UI (SPA) |
| Vite | 5+ | Bundler y dev server |
| React Router | 6+ | Navegación entre páginas |
| DM Sans + Space Mono | — | Tipografía del sistema |

### Backend *(en desarrollo)*
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.11+ | Lenguaje principal |
| FastAPI | 0.110+ | API REST |
| JWT (PyJWT) | — | Autenticación y sesiones |
| bcrypt | — | Hash de contraseñas (factor ≥ 12) |

### Base de datos y caché
| Tecnología | Versión | Uso |
|------------|---------|-----|
| PostgreSQL | 14+ | Base de datos principal |
| Redis | 7+ | Caché de consultas frecuentes |

### Módulo IA
| Tecnología | Uso |
|------------|-----|
| OR-Tools / PuLP | Optimización de asignación (programación lineal entera) |
| Prophet | Predicción de demanda por ruta, hora y día |

### DevOps
| Tecnología | Uso |
|------------|-----|
| Docker + Docker Compose | Contenedores para despliegue del backend |
| GitHub | Control de versiones y gestión de ramas |
| Jira (Scrum) | Gestión de sprints y backlog |

---

## Arquitectura

El sistema se organiza en tres capas:

```
┌─────────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN              │
│   SPA React — Administrador ATU             │
│              Supervisor de Concesionario    │
└────────────────────┬────────────────────────┘
                     │ HTTPS / API REST
┌────────────────────▼────────────────────────┐
│            CAPA DE NEGOCIO                  │
│   FastAPI — Lógica de programación          │
│           — Validación de conflictos        │
│           — Autenticación JWT               │
└──────────┬──────────────────────┬───────────┘
           │                      │
┌──────────▼──────────┐  ┌───────▼───────────┐
│  CAPA DE IA Y DATOS │  │       CACHÉ        │
│  OR-Tools + Prophet │  │       Redis        │
│  PostgreSQL         │  └───────────────────┘
└─────────────────────┘
```

---

## Requisitos funcionales

### RF01 — Autenticación y Control de Roles
- Login con correo institucional y contraseña
- Hash bcrypt con factor ≥ 12
- Sesión con token JWT, expira a las 8 horas de inactividad
- Bloqueo de cuenta tras **5 intentos fallidos consecutivos**
- Dos roles: **Administrador ATU** (acceso total) y **Supervisor** (acceso limitado a su concesionario)

### RF02 — Gestión de Rutas y Estaciones
- CRUD completo de rutas: código, nombre, estaciones inicio/fin, paraderos intermedios, frecuencia base y concesionario
- CRUD de estaciones: nombre, ubicación geográfica, capacidad operativa, horario de apertura/cierre por día de semana
- Activar y desactivar rutas
- Los cambios impactan inmediatamente en el módulo de programación (RF03)

### RF03 — Programación de Horarios de Servicio
- Grilla visual interactiva que reemplaza las hojas de cálculo
- Selección de ruta y rango de fechas para definir slots de salida
- Cada celda representa: hora de salida, unidad asignada y chofer
- Validación en tiempo real de:
  - Solapamiento de turnos
  - Disponibilidad del chofer
  - Disponibilidad de la unidad
  - Respeto de horas máximas de conducción (8 h)
- Conflictos resaltados en rojo, bloquean confirmación hasta resolverse
- Programación aprobada visible para supervisores de concesionario

### RF04 — Gestión de Choferes y Asignación de Turnos
- Registro de choferes: datos personales, licencia, tipo de licencia, disponibilidad semanal
- Estados del chofer: disponible / en descanso / baja temporal
- Control automático de horas máximas por jornada (8 h), días mínimos de descanso y vencimiento de licencia
- Alertas con sugerencias de reemplazo ante conflictos

### RF05 — Optimización con IA
- **Sub-componente 1 — Predicción de demanda:** modelo Prophet entrenado con datos históricos de ocupación; estima carga por ruta, hora y día de la semana
- **Sub-componente 2 — Optimización de asignación:** solver OR-Tools que asigna choferes y unidades minimizando conflictos, horas extra y costo operativo
- El resultado es una propuesta que el Admin ATU puede revisar, ajustar y aprobar o rechazar
- El motor se ejecuta **bajo demanda**, no en tiempo real continuo

### RF06 — Dashboard de Indicadores y Reportes
- Actualización cada 5 minutos de:
  - Cobertura de rutas activas vs. programadas
  - % de choferes asignados vs. disponibles por concesionario
  - Conflictos de programación pendientes
  - Alertas de vencimiento de licencia
- Exportación en **PDF** y **XLSX**: programación semanal por ruta, listado de choferes, historial de conflictos, resumen ejecutivo de KPIs

---

## Requisitos no funcionales

| ID | Nombre | Descripción clave |
|----|--------|-------------------|
| RNF01 | Usabilidad | Programación semanal completa en < 15 min. Dashboard accesible en ≤ 2 niveles de menú. Cumple WCAG 2.1 nivel AA. |
| RNF02 | Seguridad | HTTPS (TLS 1.2+), bcrypt ≥ 12, protección OWASP Top 10 (SQLi, XSS, CSRF), aislamiento de datos por concesionario, Ley N.° 29733. |
| RNF03 | Desempeño | API REST ≤ 2 s (p95) para CRUD. Validación de grilla ≤ 1 s. Propuesta IA ≤ 30 s para semana completa. Soporta 100 usuarios concurrentes. |
| RNF04 | Disponibilidad | 99 % uptime en horario laboral (07:00–19:00, lun–sáb). RTO ante caída ≤ 30 min. El sistema opera aunque falle el módulo IA. |
| RNF05 | Mantenibilidad | Cobertura de pruebas unitarias ≥ 70 % en módulos críticos. PEP 8 (backend), ESLint (frontend). Arquitectura por capas intercambiables. |
| RNF06 | Portabilidad | Chrome 90+, Firefox 88+, Edge 90+, Safari 14+. Responsivo desde 768 px hasta 1920 px. Backend en Docker + Docker Compose. |

---

## Estructura del proyecto

```
MetroHub/
├── frontend/                   # React + Vite
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── AlertPanel.jsx  # Panel de alertas activas
│   │   │   ├── KpiCard.jsx     # Tarjeta de indicador KPI
│   │   │   ├── RouteBar.jsx    # Barra de cobertura por ruta
│   │   │   └── Sidebar.jsx     # Menú lateral de navegación
│   │   ├── pages/
│   │   │   ├── Login.jsx       # RF01 — Autenticación
│   │   │   ├── Dashboard.jsx   # RF06 — KPIs y alertas
│   │   │   └── Grilla.jsx      # RF03 — Programación de horarios
│   │   ├── App.jsx             # Router principal
│   │   ├── App.css             # Estilos globales y design tokens
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                    # FastAPI (en desarrollo)
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py         # RF01 — JWT + bcrypt
│   │   │   ├── rutas.py        # RF02 — CRUD rutas y estaciones
│   │   │   ├── horarios.py     # RF03 — Programación
│   │   │   ├── choferes.py     # RF04 — Gestión de choferes
│   │   │   └── dashboard.py    # RF06 — KPIs
│   │   ├── ia/
│   │   │   ├── prediccion.py   # RF05 — Prophet
│   │   │   └── optimizador.py  # RF05 — OR-Tools
│   │   ├── models/             # Modelos PostgreSQL (SQLAlchemy)
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## Instalación y ejecución

### Prerrequisitos

- Node.js 18+
- npm 9+
- Git

### Frontend (desarrollo local)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-org/metrohub.git
cd metrohub

# 2. Entrar a la carpeta del frontend
cd frontend

# 3. Instalar dependencias
npm install

# 4. Iniciar servidor de desarrollo
npm run dev
```

El servidor estará disponible en `http://localhost:5173`

### Credenciales de demo

| Campo | Valor |
|-------|-------|
| Correo | cualquier correo `@atu.gob.pe` |
| Contraseña | cualquier valor |
| Bloqueo | tras 5 intentos fallidos |

> En producción las credenciales se validan contra la API FastAPI con bcrypt.

### Build para producción

```bash
cd frontend
npm run build
# Los archivos estáticos quedan en /frontend/dist
```

### Backend con Docker *(próximamente)*

```bash
# Desde la raíz del proyecto
docker-compose up --build
```

---

## Uso del sistema

### 1. Login
Accede con tu correo institucional y selecciona tu rol. La sesión expira tras 8 horas de inactividad.

### 2. Dashboard
Vista principal con los 4 KPIs operativos, cobertura por ruta y panel de alertas activas. Se actualiza cada 5 minutos.

### 3. Grilla de horarios (RF03)
- Selecciona una ruta y una semana
- Visualiza todos los slots de salida con su estado
- Los conflictos aparecen en rojo con botón "Resolver"
- Guarda el borrador o aprueba la programación completa

### 4. Gestión de rutas *(en desarrollo — RF02)*
Alta, edición y desactivación de rutas y estaciones.

### 5. Gestión de choferes *(en desarrollo — RF04)*
Registro de choferes y asignación a turnos/rutas.

### 6. Optimizador IA *(en desarrollo — RF05)*
Solicita una propuesta automática, revísala y aprueba o ajusta.

---

## Gestión del proyecto — Scrum

El proyecto se gestiona con metodología **Scrum** usando Jira y GitHub.

- **Jira:** [metrohub-proyecto.atlassian.net](https://metrohub-proyecto.atlassian.net)
- **GitHub:** *(enlace al repositorio)*

### Product Backlog

| Ticket | Historia | Épica | Fecha objetivo |
|--------|----------|-------|----------------|
| SCRUM-29 | Login con JWT y expiración por inactividad | RF01 | 27 abr |
| SCRUM-28 | Autorización por roles (Admin ATU vs Supervisor) | RF01 | 1 may |
| SCRUM-27 | Bloqueo de cuenta por intentos fallidos y bcrypt | RF01 | 2 may |
| SCRUM-2  | RF02: Gestión de Rutas y Estaciones (CRUD) | RF02 | 4 may |
| SCRUM-23 | CRUD de rutas con atributos completos | RF02 | 6 may |
| SCRUM-24 | Gestión de estaciones (ubicación, capacidad y horarios) | RF02 | 9 may |
| SCRUM-22 | Activar/desactivar rutas | RF02 | 12 may |
| SCRUM-19 | Grilla de programación por ruta y rango de fechas | RF03 | 16 may |
| SCRUM-18 | Validación en tiempo real de conflictos en la grilla | RF03 | 19 may |
| SCRUM-17 | Publicación de programación aprobada para Supervisores | RF03 | 22 may |
| SCRUM-14 | Registro y mantenimiento de choferes por concesionario | RF04 | 26 may |
| SCRUM-16 | Asignación de choferes a turnos/rutas con reglas | RF04 | 29 may |
| SCRUM-15 | Alertas y sugerencias de reemplazo ante conflictos | RF04 | 1 jun |
| SCRUM-20 | Predicción de demanda por ruta/hora/día (Prophet) | RF05 | 6 jun |
| SCRUM-21 | Optimizador de asignación (OR-Tools) y propuesta revisable | RF05 | 11 jun |
| SCRUM-25 | Dashboard de KPIs con actualización cada 5 minutos | RF06 | 17 jun |
| SCRUM-26 | Exportación de reportes PDF/XLSX | RF06 | 22 jun |

---

## Estado actual del sprint

### Sprint 1 — Inicialización y Autenticación
**Período:** 27 abril – 10 mayo 2026  
**Objetivo:** Arquitectura base del frontend operativa + módulo de autenticación (RF01)

| Ticket | Tarea | Responsable | Estado |
|--------|-------|-------------|--------|
| SCRUM-30 | Inicialización arquitectura Frontend React | Cesar Correa | ✅ En progreso |
| SCRUM-29 | Login con JWT y expiración por inactividad | Erick Ortega | 🔲 Por hacer |
| SCRUM-28 | Autorización por roles | Erick Ortega | 🔲 Por hacer |
| SCRUM-27 | Bloqueo por intentos fallidos + bcrypt | Isaac Martel | 🔲 Por hacer |
| SCRUM-2  | Gestión de Rutas y Estaciones CRUD | Diego Torres | 🔲 Por hacer |

---

## Referencias

- IEEE Std 830-1998 — Recommended Practice for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2011 — Systems and Software Engineering: Requirements Engineering
- [Datos públicos del Metropolitano de Lima — ATU](https://www.atu.gob.pe)
- Ley N.° 29733 — Ley de Protección de Datos Personales del Perú
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [OR-Tools — Google](https://developers.google.com/optimization)
- [Prophet — Meta](https://facebook.github.io/prophet/)

---

*MetroHub v2.0 · Universidad Nacional de Ingeniería · Lima, Perú · 2026*