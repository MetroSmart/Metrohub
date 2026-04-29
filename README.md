# MetroHub

Plataforma web de movilidad inteligente para el Metropolitano de Lima

> Proyecto universitario — Universidad Nacional de Ingeniería  
> Facultad de Ciencias · Escuela Profesional de Ciencia de la Computación  
> Versión 1.0 · Abril 2026

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

MetroHub es una aplicación web moderna y responsiva que proporciona herramientas inteligentes para mejorar la experiencia de usuarios y administradores del Metropolitano de Lima.

**Para pasajeros:** acceso a información en tiempo real sobre aglomeración de estaciones, rutas disponibles y predicción de tiempos de viaje usando inteligencia artificial.

**Para administradores ATU:** dashboard de gestión de rutas, horarios, indicadores clave y exportación de reportes operacionales.

El sistema reemplaza procesos manuales basados en hojas de cálculo con una plataforma integrada, escalable y segura, operando de forma paralela con los sistemas existentes.

### Usuarios del sistema

| Perfil | Descripción |
|--------|-------------|
| **Pasajeros** | Consultan aglomeración, rutas disponibles y predicen tiempos de viaje sin necesidad de registro. Acceso público total. |
| **Administrador ATU** | Accede con credenciales institucionales. Gestiona rutas, horarios, indicadores y exporta reportes. Acceso restringido y auditado. |

---

## Equipo

| Integrante | Código | Rol |
|------------|--------|-----|
| Erick Daniel Ortega Moran | 20210209H | Líder / Backend Dev — Arquitectura, API REST, módulo IA |
| Cesar Abrahan Correa Mullisaca | 20220305J | Frontend Dev / UX — Interfaz web y experiencia de usuario |
| Isaac Antonio Martel Balvin | 20231462D | Data Eng. / Docs — Pipeline de datos, documentación, pruebas |
| Diego Torres Picho | 20204113B | Colaborador — Soporte frontend y testing manual |
| Ivett Marinella Mera Amado | 20191471H | Colaboradora — Documentación y diseño de arquitectura |

Docente: Prof. Manuel Quispe Torres

---

## Tecnologías

### Frontend
| Tecnología | Versión | Uso |
|------------|---------|-----|
| React | 18+ | Framework UI (SPA) |
| Vite | 5+ | Bundler y dev server |
| React Router | 6+ | Navegación entre páginas |
| Leaflet | 1.9+ | Mapas interactivos |
| Axios | 1.4+ | Cliente HTTP |
| CSS3 | — | Animaciones y transiciones |

### Backend *(en desarrollo)*
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.11+ | Lenguaje principal |
| FastAPI | 0.110+ | API REST |
| PostgreSQL | 14+ | Base de datos principal |
| Prophet | — | Predicción de demanda IA |
| JWT (PyJWT) | — | Autenticación y sesiones |
| bcrypt | — | Hash de contraseñas (factor >= 12) |

### Base de datos y caché
| Tecnología | Versión | Uso |
|------------|---------|-----|
| PostgreSQL | 14+ | Base de datos relacional |
| Redis | 7+ | Caché de consultas frecuentes |

### Módulo IA
| Tecnología | Uso |
|------------|-----|
| OR-Tools / PuLP | Optimización de asignación (programación lineal entera) |
| Prophet | Predicción de demanda por ruta, hora y día de la semana |

### DevOps
| Tecnología | Uso |
|------------|-----|
| Docker + Docker Compose | Contenedores para despliegue |
| GitHub | Control de versiones y gestión de ramas |
| Jira (Scrum) | Gestión de sprints y backlog |

---

## Arquitectura

El sistema se organiza en tres capas principales:

```
Capa de Presentación
├── React SPA
├── Landing page pública
└── Dashboard administrativo

        HTTPS / API REST

Capa de Negocio
├── FastAPI
├── Lógica de rutas
├── Validación de datos
└── Autenticación JWT

        Conexiones internas

Capa de Datos e Inteligencia Artificial
├── PostgreSQL (almacenamiento)
├── Prophet (predicciones IA)
├── OR-Tools (optimización)
└── Redis (caché)
```

### Patrón de Monorepo

Frontend y Backend coexisten en la misma estructura de repositorio, permitiendo:
- Desarrollo paralelo sincronizado
- Testing de integración simplificado
- Deploy coordinado mediante Docker Compose
- Versionado compartido

---

## Requisitos funcionales

### RF01 — Mapa de Aglomeración en Tiempo Real
- Visualización interactiva de estaciones del Metropolitano con Leaflet
- Indicadores de color según ocupación
- Actualización cada 5 minutos sin recargar la página
- Sidebar con búsqueda y filtrado de estaciones
- Información detallada al hacer clic en marcadores
- Geolocalización opcional del usuario

### RF02 — Rutas Disponibles
- Listado dinámico de rutas activas en tiempo real
- Filtrado por hora actual y ubicación del usuario
- Panel de detalles con estadísticas de cada ruta
- Visualización de próximos horarios de salida
- Información de frecuencia de servicio
- Integración directa con predictor de viaje

### RF03 — Predicción de Viaje con IA
- Modelo Prophet entrenado con datos históricos del Metropolitano
- Estima tiempo considerando hora del día, día de semana, aglomeración actual
- Visualización de porcentaje de confianza del modelo
- Sugerencias de rutas alternativas con información de transbordo
- Gráfico del recorrido estimado
- Hora de llegada predicha

### RF04 — Autenticación y Control de Roles
- Login con correo institucional y contraseña
- Hash bcrypt con factor >= 12
- Sesión con token JWT, expira a las 8 horas de inactividad
- Bloqueo de cuenta tras 5 intentos fallidos consecutivos
- Rol de Administrador ATU con acceso total
- Recuperación segura de contraseña

### RF05 — Gestión de Rutas (Administrador)
- CRUD completo de rutas: código, nombre, estaciones, paraderos, frecuencia
- CRUD de estaciones: ubicación geográfica, capacidad, horarios por día
- Activar y desactivar rutas
- Los cambios impactan inmediatamente en el módulo de programación

### RF06 — Dashboard de Indicadores y Reportes
- Actualización cada 5 minutos de KPIs operativos
- Cobertura de rutas activas vs programadas
- Porcentaje de choferes asignados vs disponibles
- Conflictos de programación pendientes
- Alertas de vencimiento de licencia
- Exportación en PDF y XLSX

---

## Requisitos no funcionales

| ID | Nombre | Descripción clave |
|----|--------|-------------------|
| RNF01 | Usabilidad | Landing accesible en <= 2 clics. Dashboard <= 2 niveles de menú. WCAG 2.1 AA. |
| RNF02 | Seguridad | HTTPS (TLS 1.2+), bcrypt >= 12, protección OWASP Top 10, aislamiento de datos, Ley 29733. |
| RNF03 | Desempeño | API REST <= 2 s (p95). Mapa <= 3 s. Propuesta IA <= 30 s. 100 usuarios concurrentes. |
| RNF04 | Disponibilidad | 99% uptime horario laboral (07:00-19:00, lun-sáb). RTO <= 30 min. Funcional sin módulo IA. |
| RNF05 | Mantenibilidad | >= 70% cobertura pruebas en módulos críticos. PEP 8 (backend), ESLint (frontend). Arquitectura modular. |
| RNF06 | Portabilidad | Chrome 90+, Firefox 88+, Edge 90+ en escritorios y tablets. Responsivo 360px-1920px. Backend en Docker. |

---

## Estructura del proyecto

```
MetroHub/
├── frontend/                      # React + Vite
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── ServiceCard.jsx
│   │   ├── pages/
│   │   │   ├── Landing.jsx       # RF01 — Landing page
│   │   │   ├── Landing.css
│   │   │   ├── Login.jsx         # RF04 — Autenticación
│   │   │   ├── Login.css
│   │   │   ├── MapPage.jsx       # RF01 — Mapa aglomeración
│   │   │   ├── Routes.jsx        # RF02 — Rutas disponibles
│   │   │   ├── Predict.jsx       # RF03 — Predicción IA
│   │   │   └── Dashboard.jsx     # RF05-RF06 — Admin
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                       # FastAPI (en desarrollo)
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py           # RF04 — JWT + bcrypt
│   │   │   ├── estaciones.py     # RF01 — Datos estaciones
│   │   │   ├── rutas.py          # RF02-RF05 — CRUD rutas
│   │   │   ├── prediccion.py     # RF03 — Prophet
│   │   │   └── dashboard.py      # RF06 — KPIs
│   │   ├── ia/
│   │   │   ├── prediccion.py
│   │   │   └── optimizador.py
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
├── package.json
├── .gitignore
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
git clone https://github.com/MetroSmart/Metrohub.git
cd Metrohub

# 2. Instalar dependencias
cd frontend
npm install

# 3. Iniciar servidor de desarrollo
npm run dev
```

El servidor estará disponible en `http://localhost:5173`

### Credenciales de demo

| Campo | Valor |
|-------|-------|
| Correo | Cualquier correo `@atu.gob.pe` |
| Contraseña | Cualquier valor |
| Bloqueo | Tras 5 intentos fallidos |

En producción las credenciales se validan contra la API FastAPI con bcrypt.

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

### 1. Landing page
Explora los servicios disponibles en la plataforma: mapa de aglomeración, rutas inteligentes, predicción con IA y dashboard administrativo.

### 2. Mapa (RF01)
Visualiza en tiempo real la aglomeración de todas las estaciones del Metropolitano. Busca estaciones específicas y obtén información detallada.

### 3. Rutas (RF02)
Descubre rutas activas cercanas a ti según tu hora actual. Visualiza próximos horarios y estadísticas de cada ruta.

### 4. Predictor (RF03)
Selecciona origen, destino, hora y día para obtener una estimación de tiempo de viaje con IA. Visualiza rutas alternativas.

### 5. Login (RF04)
Accede con tu correo institucional para usar el dashboard administrativo. La sesión expira tras 8 horas de inactividad.

### 6. Dashboard admin *(en desarrollo — RF05-RF06)*
- Gestión de rutas y horarios
- Visualización de indicadores clave
- Exportación de reportes en PDF/XLSX

---

## Gestión del proyecto — Scrum

El proyecto se gestiona con metodología Scrum con sprints de 2 semanas.

- GitHub: https://github.com/MetroSmart/Metrohub
- Rama principal: main
- Rama de desarrollo: version1

### Product Backlog

| Ticket | Historia | Épica | Fecha objetivo |
|--------|----------|-------|----------------|
| SCRUM-30 | Landing page estilo Apple | RF01 | 27 abr |
| SCRUM-31 | Login moderna y segura | RF04 | 1 may |
| SCRUM-32 | Arquitectura Frontend Monorepo | — | 3 may |
| SCRUM-33 | Mapa interactivo con Leaflet | RF01 | 10 may |
| SCRUM-34 | Listado dinámico de rutas | RF02 | 17 may |
| SCRUM-35 | Predicción de demanda (Prophet) | RF03 | 24 may |
| SCRUM-36 | Backend FastAPI setup | — | 31 may |
| SCRUM-37 | API REST endpoints | — | 7 jun |
| SCRUM-38 | Integración frontend-backend | — | 14 jun |
| SCRUM-39 | Gestión de rutas (CRUD) | RF05 | 21 jun |
| SCRUM-40 | Dashboard de KPIs | RF06 | 28 jun |
| SCRUM-41 | Exportación PDF/XLSX | RF06 | 5 jul |

---

## Estado actual del sprint

### Sprint 1 — Inicialización y Landing

Período: 27 abril – 10 mayo 2026
Objetivo: Arquitectura base Frontend operativa + Landing page estilo Apple

| Ticket | Tarea | Responsable | Estado |
|--------|-------|-------------|--------|
| SCRUM-30 | Landing page estilo Apple | Cesar Correa | En progreso |
| SCRUM-31 | Login moderna | Cesar Correa | En progreso |
| SCRUM-32 | Arquitectura Monorepo | Erick Ortega | Completado |
| SCRUM-33 | Setup React Router | Cesar Correa | Por hacer |
| SCRUM-34 | Componentes reutilizables | Diego Torres | Por hacer |

---

## Estándares de código

### Frontend
- Linter: ESLint
- Formato: Prettier
- Naming: camelCase (variables), PascalCase (componentes)
- Estructura: Funcionales con Hooks

### Backend
- Linter: PEP 8
- Framework: FastAPI
- ORM: SQLAlchemy
- Documentación: Docstrings en español

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
- Datos públicos del Metropolitano de Lima — ATU
- Ley No. 29733 — Ley de Protección de Datos Personales del Perú
- FastAPI Documentation (https://fastapi.tiangolo.com)
- OR-Tools — Google (https://developers.google.com/optimization)
- Prophet — Meta (https://facebook.github.io/prophet/)

---

MetroHub v1.0 · Universidad Nacional de Ingeniería · Lima, Perú · 2026