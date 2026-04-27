# MetroHub 🚌

**Plataforma web de movilidad inteligente para el Metropolitano de Lima**

> Proyecto universitario — Universidad Nacional de Ingeniería  
> Facultad de Ciencias · Escuela Profesional de Ciencia de la Computación  
> Versión 1.0 · Abril 2026

---

## Tabla de contenidos

- [Descripción general](#descripción-general)
- [Características](#características)
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

MetroHub es una **aplicación web moderna y responsiva** que mejora significativamente la experiencia de los usuarios del Metropolitano de Lima proporcionando:

- **Información en tiempo real** sobre aglomeración de estaciones
- **Rutas inteligentes** filtradas por hora y ubicación
- **Predicción de tiempos de viaje** usando inteligencia artificial (Prophet)
- **Dashboard administrativo** para gestión de rutas y horarios

### Usuarios del sistema

| Perfil | Descripción |
|--------|-------------|
| **Pasajeros** | Consultan aglomeración, rutas disponibles y predicen tiempos de viaje sin necesidad de registro |
| **Administrador ATU** | Acceso con credenciales institucionales. Gestiona rutas, horarios y visualiza indicadores clave |

---

## Características

### 🗺️ Mapa de Aglomeración en Tiempo Real (RF01)
- Visualiza todas las estaciones con indicadores de color según ocupación
- **Verde:** Bajo (< 40%) | **Amarillo:** Medio (40–70%) | **Naranja:** Alto (70–90%) | **Rojo:** Crítico (> 90%)
- Actualización automática cada 5 minutos sin recargar
- Mapa interactivo con Leaflet + OpenStreetMap
- Sidebar con lista de estaciones y búsqueda

### 🚌 Rutas Disponibles (RF02)
- Detecta ubicación y muestra rutas activas en tiempo real
- Filtrado por hora actual, ubicación y estación
- Visualización de próximos horarios de salida
- Panel de detalles con estadísticas de cada ruta
- Integración con predictor de viaje

### ⏱️ Predicción de Viaje con IA (RF03)
- Modelo **Prophet** entrenado con datos históricos
- Estima tiempo entre dos estaciones considerando:
  - Hora del día
  - Día de semana
  - Aglomeración actual
- Muestra porcentaje de confianza del modelo
- Sugiere rutas alternativas con transbordo
- Visualización de recorrido en tiempo real

### 🔐 Autenticación y Dashboard (RF04-RF06)
- Login seguro con correo institucional (@atu.gob.pe)
- JWT con sesión de 8 horas
- Bloqueo automático tras 5 intentos fallidos
- **Dashboard administrativo con:**
  - Gestión de rutas (CRUD)
  - Configuración de horarios y estaciones
  - KPIs en tiempo real
  - Exportación de reportes (PDF/XLSX)

### 🎨 Diseño Estilo Apple
- Interfaz minimalista y elegante
- Transiciones fluidas y animaciones suaves
- Dark mode integrado
- Totalmente responsivo (móvil, tablet, desktop)
- Cumple WCAG 2.1 nivel AA

---

## Equipo

| Integrante | Código | Rol |
|------------|--------|-----|
| Erick Daniel Ortega Moran | 20210209H | Líder / Backend Dev |
| Cesar Abrahan Correa Mullisaca | 20220305J | Frontend Dev / UX |
| Isaac Antonio Martel Balvin | 20231462D | Data Eng. / Docs |
| Diego Torres Picho | 20204113B | Colaborador Frontend |
| Ivett Marinella Mera Amado | 20191471H | Colaboradora Docs |

**Docente:** Prof. Manuel Quispe Torres

---

## Tecnologías

### Frontend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 18+ | Framework UI (SPA) |
| Vite | 5+ | Bundler y dev server |
| React Router | 6+ | Navegación entre páginas |
| Leaflet | 1.9+ | Mapa interactivo |
| Axios | 1.4+ | Cliente HTTP |
| CSS3 | — | Animaciones y transiciones |

### Backend *(en desarrollo)*
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.10+ | Lenguaje principal |
| FastAPI | 0.110+ | API REST |
| PostgreSQL | 14+ | Base de datos |
| Prophet | — | Predicción IA |
| JWT + bcrypt | — | Autenticación segura |

### DevOps
| Tecnología | Uso |
|------------|-----|
| Docker + Docker Compose | Contenedores para despliegue |
| GitHub | Control de versiones |
| Jira | Gestión de sprints (Scrum) |

---

## Arquitectura

### Monorepo Structure
```
┌─────────────────────────────────────────┐
│        CAPA DE PRESENTACIÓN             │
│   React SPA — Usuarios Públicos         │
│              Administrador ATU          │
└────────────────────┬────────────────────┘
                     │ HTTPS / API REST
┌────────────────────▼────────────────────┐
│         CAPA DE NEGOCIO                 │
│   FastAPI — Lógica de rutas             │
│           — Validación                  │
│           — Autenticación JWT           │
└──────────┬──────────────────────┬───────┘
           │                      │
┌──────────▼──────────┐  ┌───────▼───────┐
│  CAPA DE IA Y DATOS │  │     CACHÉ      │
│  Prophet + OR-Tools │  │     Redis      │
│  PostgreSQL         │  └───────────────┘
└─────────────────────┘
```

### Comunicación
- **Frontend → Backend:** HTTP REST con Axios
- **Autenticación:** JWT (Bearer token)
- **Tiempo real:** Polling cada 5 minutos para estaciones
- **Validación:** Input en frontend + validación en backend

---

## Requisitos funcionales

### RF01 — Mapa de Aglomeración en Tiempo Real
- ✅ Visualización interactiva de estaciones
- ✅ Indicadores de color por nivel de ocupación
- ✅ Actualización cada 5 minutos
- ✅ Sidebar con búsqueda de estaciones
- ✅ Popup con información al hacer clic

### RF02 — Rutas Disponibles
- ✅ Listado dinámico de rutas activas
- ✅ Filtrado por hora y ubicación
- ✅ Panel de detalles con estadísticas
- ✅ Próximos horarios de salida
- ✅ Integración con predictor

### RF03 — Predicción de Viaje con IA
- ✅ Formulario origen/destino/hora/día
- ✅ Modelo Prophet para estimación
- ✅ Muestra confianza del modelo
- ✅ Sugerencias de rutas alternativas
- ✅ Visualización del recorrido

### RF04 — Autenticación y Control de Roles
- ✅ Login con correo y contraseña
- ✅ JWT con expiración (8 horas)
- ✅ Bloqueo tras 5 intentos fallidos
- ✅ Rol Administrador ATU
- 🔲 Rol Supervisor (próximamente)

### RF05 — Gestión de Rutas (Admin)
- 🔲 CRUD de rutas
- 🔲 Activar/desactivar rutas
- 🔲 Edición de paraderos
- 🔲 Gestión de frecuencias

### RF06 — Dashboard de Indicadores
- 🔲 KPIs en tiempo real
- 🔲 Cobertura por ruta
- 🔲 Panel de alertas
- 🔲 Exportación PDF/XLSX

---

## Requisitos no funcionales

| ID | Nombre | Descripción clave |
|----|--------|-------------------|
| RNF01 | Usabilidad | Interface intuitiva, accesible en 2 clics. WCAG 2.1 AA. |
| RNF02 | Seguridad | HTTPS, JWT, bcrypt ≥12, OWASP Top 10, Ley 29733. |
| RNF03 | Desempeño | API ≤2s, Mapa ≤3s, IA ≤30s. Soporta 100 usuarios. |
| RNF04 | Disponibilidad | 99% uptime (07:00–19:00, lun–sáb). RTO ≤30min. |
| RNF05 | Mantenibilidad | ≥70% cobertura tests. PEP 8, ESLint. Arquitectura modular. |
| RNF06 | Portabilidad | Chrome 90+, Firefox 88+, Edge 90+, Safari 14+. Responsivo 360px–1920px. |

---

## Estructura del proyecto

```
MetroHub/
├── frontend/                      # React + Vite
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx        # Landing page estilo Apple
│   │   │   ├── Landing.css
│   │   │   ├── Login.jsx          # RF04 — Autenticación
│   │   │   ├── Login.css
│   │   │   ├── MapPage.jsx        # RF01 — Mapa
│   │   │   ├── Routes.jsx         # RF02 — Rutas
│   │   │   ├── Predict.jsx        # RF03 — Predicción
│   │   │   └── Dashboard.jsx      # RF05-RF06 — Admin
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ServiceCard.jsx
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js            # Cliente HTTP con Axios
│   │   ├── App.jsx               # Router principal
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                       # FastAPI (en desarrollo)
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py           # RF04 — JWT + bcrypt
│   │   │   ├── estaciones.py     # RF01 — Datos estaciones
│   │   │   ├── rutas.py          # RF02 — Gestión rutas
│   │   │   ├── prediccion.py     # RF03 — Prophet IA
│   │   │   └── dashboard.py      # RF06 — KPIs
│   │   ├── models/
│   │   │   ├── usuario.py
│   │   │   ├── ruta.py
│   │   │   └── estacion.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml
├── package.json                   # Scripts para todo el monorepo
├── .gitignore
└── README.md
```

---

## Instalación y ejecución

### Prerrequisitos
- Node.js 18+
- npm 9+
- Git
- Python 3.10+ *(para backend, opcional)*

### Frontend (desarrollo local)

```bash
# 1. Clonar el repositorio
git clone https://github.com/MetroSmart/Metrohub.git
cd Metrohub

# 2. Instalar dependencias del frontend
cd frontend
npm install

# 3. Iniciar servidor de desarrollo
npm run dev
```

La aplicación estará disponible en **`http://localhost:5173`**

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

### Para Pasajeros

1. **Landing Page** — Explora los servicios disponibles
2. **Mapa** — Visualiza la aglomeración en tiempo real
3. **Rutas** — Descubre rutas activas cerca de ti
4. **Predictor** — Estima tu tiempo de viaje con IA

### Para Administradores

1. **Login** — Accede con credenciales institucionales (@atu.gob.pe)
2. **Dashboard** — Visualiza KPIs y alertas
3. **Gestión** — Administra rutas, horarios y estaciones
4. **Reportes** — Exporta datos en PDF o Excel

---

## Gestión del proyecto — Scrum

El proyecto usa **Scrum** con sprints de 2 semanas.

### Repositorio
- **GitHub:** [MetroSmart/Metrohub](https://github.com/MetroSmart/Metrohub)
- **Rama principal:** `main`
- **Rama de desarrollo:** `version1`

### Sprints

#### Sprint 1 — Inicialización y Landing (27 abr – 10 may)
| Ticket | Tarea | Estado |
|--------|-------|--------|
| SCRUM-30 | Landing page estilo Apple | ✅ En progreso |
| SCRUM-31 | Login moderna | ✅ En progreso |
| SCRUM-32 | Arquitectura Frontend | ✅ Completado |

#### Sprint 2 — Funcionalidades Públicas (11 may – 24 may)
| Ticket | Tarea | Estado |
|--------|-------|--------|
| SCRUM-33 | RF01 — Mapa interactivo | 🔲 Por hacer |
| SCRUM-34 | RF02 — Rutas disponibles | 🔲 Por hacer |
| SCRUM-35 | RF03 — Predicción IA | 🔲 Por hacer |

#### Sprint 3 — Backend y Admin (25 may – 7 jun)
| Ticket | Tarea | Estado |
|--------|-------|--------|
| SCRUM-36 | Backend FastAPI setup | 🔲 Por hacer |
| SCRUM-37 | API REST endpoints | 🔲 Por hacer |
| SCRUM-38 | RF04 — Autenticación | 🔲 Por hacer |

#### Sprint 4 — Dashboard Admin (8 jun – 21 jun)
| Ticket | Tarea | Estado |
|--------|-------|--------|
| SCRUM-39 | RF05 — Gestión rutas | 🔲 Por hacer |
| SCRUM-40 | RF06 — Dashboard KPIs | 🔲 Por hacer |
| SCRUM-41 | Reportes PDF/XLSX | 🔲 Por hacer |

---

## Estado actual del sprint

**Sprint 1** — Inicialización y Landing  
**Período:** 27 abril – 10 mayo 2026  
**Objetivo:** Arquitectura base + Landing page estilo Apple operativa

### Progreso
- ✅ **Monorepo structure** completada
- ✅ **Frontend React + Vite** configurado
- ✅ **Landing page** con servicios y animaciones
- ✅ **Login page** moderna
- 🔲 Backend API (próximo sprint)

### Próximos pasos
1. Integrar React Router completamente
2. Crear componentes reutilizables
3. Implementar mapa interactivo (Leaflet)
4. Comenzar desarrollo del backend

---

## Estándares de código

### Frontend
- **Linter:** ESLint
- **Formato:** Prettier
- **Naming:** camelCase para variables, PascalCase para componentes
- **Estructura:** Funcionales + Hooks

### Backend
- **Linter:** PEP 8
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Documentación:** Docstrings en español

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
- Describe qué cambios haces
- Referencia el ticket Scrum
- Solicita review de un compañero

---

## Referencias

- IEEE Std 830-1998 — Recommended Practice for Software Requirements Specifications
- ISO/IEC/IEEE 29148:2011 — Systems and Software Engineering: Requirements Engineering
- [Datos públicos del Metropolitano de Lima — ATU](https://www.atu.gob.pe)
- Ley N.° 29733 — Ley de Protección de Datos Personales del Perú
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [React Documentation](https://react.dev)

---

*MetroHub v1.0 · Universidad Nacional de Ingeniería · Lima, Perú · 2026*