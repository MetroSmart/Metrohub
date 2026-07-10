# Tests — Frontend MetroHub

Suite con **Vitest + React Testing Library + MSW**.

## Instalación

```bash
cd frontend
npm install
```

## Correr la suite

```bash
# Una vez
npm test

# Modo watch
npm run test:watch

# Con cobertura
npm run test:coverage
```

## Estructura

```
src/
├── __tests__/
│   ├── components/      # nivel unitario: componentes aislados (mock de `api`)
│   ├── pages/            # nivel de integración: página + MSW mockeando /api
│   ├── system/            # nivel de sistema: subsistema completo (UI + api.js + MSW)
│   ├── acceptance/        # nivel de aceptación: escenarios Given/When/Then
│   └── README.md
└── test/
    ├── setup.js         # jest-dom + ciclo MSW
    ├── server.js        # instancia MSW
    └── handlers.js      # handlers por defecto (sobre-escribibles por test)
```

No hay tooling E2E en el repo (todo corre sobre Vitest + jsdom). Los niveles
de sistema y aceptación se implementan igual, con la diferencia de qué tanto
del stack ejercitan y a qué pregunta responden:

- **Unitaria** (`components/`): el componente solo, con `api` mockeado —
  aísla su lógica interna (validaciones, estados, permisos por rol).
- **Integración** (`pages/`): la página completa contra MSW — valida el
  cableado entre la UI y los endpoints reales que usa.
- **Sistema** (`system/`): un subsistema (p. ej. el Copiloto IA) recorrido en
  un flujo continuo de varios pasos contra MSW, incluyendo su degradación
  ante fallos del backend (RNF04).
- **Aceptación** (`acceptance/`): un test por criterio de aceptación de la
  historia de usuario, redactado en comentarios Given/When/Then. No cubre el
  cableado de `App.jsx` (routing entre páginas) — el componente se ejercita
  con las props que su contenedor ya le pasaría.

## Cobertura actual

Suite completa: **~130 tests** sobre el cliente HTTP, los 6 componentes, las
10 páginas y el Copiloto IA (RF05) en sus cuatro niveles (~98% de líneas).

| Archivo | Qué cubre |
|---|---|
| `api.test.js` | Cliente HTTP: token Bearer, JSON, 204→null, errores con `detail` (string y objeto), métodos post/put/patch |
| `components/KpiCard.test.jsx` | Render de título, valor y variación del KPI |
| `components/AlertPanel.test.jsx` | RF06 — listado de alertas, estado vacío y color del punto por tipo (`danger`/`warn`/`info`, gris como fallback) |
| `components/Sidebar.test.jsx` | Navegación por rol (admin ve Administración, supervisor no, chofer solo "Mi jornada"), callbacks `onNav`/`onLogout`, avatar e inicial del usuario |
| `components/RouteBar.test.jsx` | RF02 — código, nombre y badge de tipo de ruta con sus colores (`regular`/`expreso`/`nocturna`, fallback y guion sin tipo) |
| `components/CambioPasswordPrimerIngreso.test.jsx` | RF01 — validaciones del formulario (campos vacíos, mínimo 8 caracteres, confirmación), envío a `/api/auth/cambiar-password-primer-ingreso`, manejo de error del API y cierre de sesión |
| `components/CopilotoIA.test.jsx` | RF05 — permisos por rol, pestañas Fatiga/Reemplazo/Asistente, acciones (`programar-descanso`, `sugerir/aplicar-reemplazo`, `chat`), validaciones y manejo de error |
| `pages/Login.test.jsx` | RF01 — login con MSW: éxito, credenciales inválidas, contador de intentos, bloqueo a los 5, error de red |
| `pages/Dashboard.test.jsx` | RF05/RF06 — KPIs del API, rutas activas, alertas de documentos, estado vacío y accesos rápidos |
| `pages/Reportes.test.jsx` | RF07 — exportación PDF/XLSX (descarga con blob stubbeado), error del backend y restricción a Admin ATU |
| `pages/Areas.test.jsx` | RF08 — listado, vacío, error, crear con validación, error 409 y toggle activo |
| `pages/MisRutas.test.jsx` | RF04 — próximo servicio con estaciones, tabla de servicios, vacío, error y re-consulta al cambiar fecha |
| `pages/Buses.test.jsx` | RF09 — listado, filtro por estado, registrar (placa a mayúsculas), cambiar estado, eliminar con confirmación y permisos por área |
| `pages/Usuarios.test.jsx` | RF01 — listado, filtro por rol, crear con validaciones (área del supervisor), toggle activo y cambio de contraseña |
| `pages/Choferes.test.jsx` | RF03 — listado con alertas de vencimiento, filtros, alta con acceso al portal, cambio de estado e indisponibilidades (tab, alta, borrado) |
| `pages/Rutas.test.jsx` | RF02 — tabs rutas/estaciones, crear/editar ruta, toggle de estado, recorrido (asignar/quitar estaciones) y alta de estación |
| `pages/Grilla.test.jsx` | RF04/RF05 — autoselección de programación vigente, conflictos y resolución (modal con sugerencia IA y aplicar-reemplazo), botón Reemplazar, asignar/quitar chofer, aprobar, crear programación, agregar horario, duplicar semana, eliminar horario y permisos del supervisor |
| `system/CopilotoIA.system.test.jsx` | RF05 — flujo continuo fatiga → reemplazo → asistente contra MSW real, y degradación a mensaje de error cuando el servicio IA falla (RNF04) |
| `acceptance/copiloto-ia.acceptance.test.jsx` | RF05 — un escenario por criterio de aceptación: descanso compensatorio con acceso a Grilla, reemplazo automático vía `reemplazoTrigger`, consulta al asistente y restricción de acceso para el rol chofer |

> Ojo: en los fixtures de `Sidebar.test.jsx` el nombre del usuario no debe
> coincidir con la etiqueta de rol que renderiza el componente ("Admin ATU",
> "Supervisor", "Chofer"), porque `getByText` fallaría al encontrar el texto
> duplicado.

## Correr un solo archivo

```bash
npx vitest run src/__tests__/components/Sidebar.test.jsx
```

## Mockear el backend

### Unit tests: mockear el módulo `api`

Para componentes que llaman al backend vía `api` (`src/api.js`), en un unit
test es más directo mockear el módulo que levantar MSW
(ver `CambioPasswordPrimerIngreso.test.jsx`):

```js
import { api } from "../../api";

vi.mock("../../api", () => ({
  api: { post: vi.fn() },
}));

// en el test:
api.post.mockResolvedValueOnce({ ok: true });            // éxito
api.post.mockRejectedValueOnce(new Error("mensaje"));    // error del API
```

Recuerda limpiar los mocks entre tests con `vi.clearAllMocks()` en un
`beforeEach`.

### Integration tests: MSW

Por defecto `handlers.js` resuelve `POST /api/auth/login` con éxito para
`admin.atu@metrohub.gob.pe / admin123`. Para un test específico:

```js
import { http, HttpResponse } from "msw";
import { server } from "../../test/server.js";

server.use(
  http.get("http://localhost:8000/api/choferes", () =>
    HttpResponse.json([{ id: 1, nombres: "Juan" }])
  )
);
```

## Convenciones

- Prioriza queries accesibles (`getByRole`, `getByLabelText`) sobre `getByTestId`.
- Usa `userEvent.setup()` en lugar de `fireEvent` cuando simulas interacción real
  (`fireEvent.change` solo para inputs `date`/`time`, que `userEvent` no tipea).
- Cada test debe poder correr aislado — MSW resetea handlers entre tests.
- jsdom no implementa `window.confirm`/`alert` ni descargas: stubea con
  `vi.spyOn(window, "confirm")`, `URL.createObjectURL = vi.fn()` y el click del
  `<a>` (ver `Buses.test.jsx` y `Reportes.test.jsx`), y restaura en `afterEach`.
- El nombre del usuario logueado en los fixtures no debe coincidir con textos de
  la página (nombres en tablas, etiquetas de rol): el Sidebar lo pinta de
  inmediato y un `findByText` resolvería antes de que cargue la data real.
