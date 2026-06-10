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

## Mockear el backend

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
