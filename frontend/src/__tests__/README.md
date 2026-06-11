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
│   ├── components/      # unit tests de componentes presentacionales
│   ├── pages/           # integration tests con MSW para mockear /api
│   └── README.md
└── test/
    ├── setup.js         # jest-dom + ciclo MSW
    ├── server.js        # instancia MSW
    └── handlers.js      # handlers por defecto (sobre-escribibles por test)
```

## Cobertura actual

| Archivo | Qué cubre |
|---|---|
| `components/KpiCard.test.jsx` | Render de título, valor y variación del KPI |
| `components/AlertPanel.test.jsx` | RF06 — listado de alertas, estado vacío y color del punto por tipo (`danger`/`warn`/`info`, gris como fallback) |
| `components/Sidebar.test.jsx` | Navegación por rol (admin ve Administración, supervisor no, chofer solo "Mi jornada"), callbacks `onNav`/`onLogout`, avatar e inicial del usuario |
| `components/RouteBar.test.jsx` | RF02 — código, nombre y badge de tipo de ruta con sus colores (`regular`/`expreso`/`nocturna`, fallback y guion sin tipo) |
| `components/CambioPasswordPrimerIngreso.test.jsx` | RF01 — validaciones del formulario (campos vacíos, mínimo 8 caracteres, confirmación), envío a `/api/auth/cambiar-password-primer-ingreso`, manejo de error del API y cierre de sesión |
| `pages/Login.test.jsx` | Flujo de login con MSW (éxito, credenciales inválidas) |

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
- Usa `userEvent.setup()` en lugar de `fireEvent` cuando simulas interacción real.
- Cada test debe poder correr aislado — MSW resetea handlers entre tests.
