# Guía de tests — MetroHub
### Referencia para evaluación docente

---

## Resumen general

La suite tiene **38 tests automatizados** divididos en cuatro grupos, todos orientados al módulo de autenticación y control de acceso (RF01).

| Grupo | Cantidad | Qué verifica |
|-------|----------|--------------|
| Unitarios backend | 16 | La lógica interna de seguridad (contraseñas, tokens, bloqueos) |
| Integración backend | 11 | Los endpoints del servidor reciben y responden correctamente |
| Unitarios frontend | 5 | Los componentes visuales muestran los datos correctamente |
| Integración frontend | 6 | El formulario de login se comporta bien desde la perspectiva del usuario |

**Objetivo general:** garantizar que ningún usuario pueda entrar sin credenciales válidas, que cada rol solo acceda a lo que le corresponde, y que la plataforma comunique errores al usuario de forma adecuada.

---

## 1. Tests unitarios del backend (16 tests)
**Archivo:** `backend/tests/unit/services/test_auth_service.py`

Estos tests prueban la lógica de seguridad de forma aislada, sin levantar ningún servidor ni conectarse a internet. Son los más rápidos de ejecutar.

### Seguridad de contraseñas

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| `test_hash_password_genera_hash_bcrypt` | Las contraseñas se almacenan cifradas, nunca en texto plano | Si el sistema guardara la contraseña tal como la escribe el usuario |
| `test_verificar_password_correcta` | La contraseña correcta pasa la verificación sin errores | Si el cifrado estuviera mal implementado y rechazara contraseñas válidas |
| `test_verificar_password_incorrecta` | Una contraseña equivocada es rechazada | Si el sistema aceptara cualquier contraseña como válida |

### Tokens de sesión (el "pase digital")

Cuando el usuario inicia sesión correctamente, el sistema le entrega un token — un código cifrado que funciona como credencial mientras navega por la plataforma.

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| `test_crear_y_decodificar_token_admin` | El token del administrador contiene su correo y su rol correctamente | Si el token no identificara correctamente quién es el usuario |
| `test_token_supervisor_incluye_area_id` | El token del supervisor lleva el identificador de su área operativa | Si el supervisor perdiera la información de su área al iniciar sesión |
| `test_token_invalido_lanza_jwterror` | Un token falsificado o inventado es detectado y rechazado | Si el sistema aceptara tokens fabricados por terceros |
| `test_token_sin_sub_lanza_jwterror` | Un token que no identifica a ningún usuario es rechazado | Si el sistema procesara tokens incompletos sin validarlos |

### Autenticación contra la base de datos

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| `test_autenticar_admin_ok` | El administrador puede iniciar sesión con sus credenciales correctas | Si el login fallara ante datos válidos |
| `test_autenticar_supervisor_devuelve_area_id` | Al autenticarse, el supervisor recibe su área asignada | Si el área no se asociara correctamente a la sesión |
| `test_autenticar_chofer_devuelve_chofer_id` | El chofer recibe su identificador propio al iniciar sesión | Si el sistema no pudiera distinguir qué chofer está ingresando |
| `test_autenticar_password_incorrecta` | Una contraseña incorrecta no otorga acceso | Si el sistema permitiera entrar con contraseña equivocada |
| `test_autenticar_email_inexistente` | Un correo que no existe en el sistema es rechazado | Si el sistema dejara entrar a personas no registradas |
| `test_bloqueo_tras_max_intentos` | Tras 5 intentos fallidos consecutivos, la cuenta queda bloqueada temporalmente —incluso si después se escribe la contraseña correcta— | Si el sistema permitiera intentos ilimitados sin bloquear la cuenta |

### Cambio de contraseña en primer ingreso (choferes)

Los choferes nuevos reciben una contraseña temporal (su DNI) y el sistema les obliga a cambiarla en su primer ingreso.

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| `test_cambiar_password_primer_ingreso_ok` | Un chofer nuevo puede cambiar su contraseña temporal exitosamente | Si el proceso de cambio de contraseña estuviera roto |
| `test_cambiar_password_rechaza_password_igual_a_dni` | No se puede usar el propio DNI como nueva contraseña | Si el sistema aceptara el DNI como contraseña (regla de seguridad) |
| `test_cambiar_password_rechaza_corta` | La nueva contraseña debe tener al menos 8 caracteres | Si el sistema aceptara contraseñas de 1 o 2 caracteres |

---

## 2. Tests de integración del backend (11 tests)
**Archivo:** `backend/tests/integration/test_auth_endpoints.py`

Estos tests prueban el servidor completo: envían peticiones HTTP reales al sistema y verifican las respuestas, exactamente como lo haría un navegador.

### Login

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| `test_login_admin_ok` | El administrador inicia sesión y recibe un token de acceso válido | Si el servidor devolviera un error ante credenciales correctas |
| `test_login_supervisor_incluye_area` | La respuesta del login del supervisor incluye el ID de su área operativa | Si la respuesta no incluyera el área y el sistema no supiera qué datos mostrarle |
| `test_login_chofer_ok` | El chofer inicia sesión y el servidor devuelve su identificador propio | Si el servidor no pudiera distinguir al chofer o no devolviera su ID |
| `test_login_credenciales_invalidas` | Con contraseña incorrecta, el servidor responde con error "no autorizado" (HTTP 401) | Si el servidor devolviera "éxito" ante credenciales inválidas |
| `test_login_usuario_inexistente` | Con un correo que no existe, el servidor responde con error 401 | Si el servidor revelara si el usuario existe o no (vulnerabilidad de enumeración) |

### Endpoint `/me` — "¿quién soy?"

Este endpoint permite que la plataforma identifique al usuario que ya tiene sesión activa.

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| `test_me_admin` | Con un token válido de admin, el sistema devuelve sus datos correctos | Si el servidor no pudiera leer el token o devolviera datos de otro usuario |
| `test_me_supervisor` | El sistema devuelve los datos del supervisor incluyendo su área | Si los datos del supervisor estuvieran incompletos |
| `test_me_chofer` | El sistema devuelve los datos del chofer incluyendo su ID | Si los datos del chofer no estuvieran disponibles |
| `test_me_sin_token_devuelve_401` | Sin token de acceso, el servidor rechaza la solicitud | Si el servidor diera información sin pedir ninguna identificación |
| `test_me_token_invalido_devuelve_401` | Con un token inventado o alterado, el servidor rechaza con 401 | Si el servidor aceptara credenciales falsificadas |

### Control de acceso por rol

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| `test_cambiar_password_solo_chofer` | Un administrador no puede usar el endpoint de cambio de contraseña de primer ingreso — esa función es exclusiva para choferes y el servidor responde "prohibido" (HTTP 403) | Si cualquier usuario pudiera acceder a funciones reservadas para otro rol |

---

## 3. Tests unitarios del frontend (5 tests)
**Archivo:** `frontend/src/__tests__/components/KpiCard.test.jsx`

Prueban el componente de tarjeta de indicadores (KPI) que aparece en el panel de control del administrador y supervisor. Estas tarjetas muestran métricas como "Rutas activas: 12" o "Choferes: 45 (+3 vs ayer)".

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| "renderiza label y value" | La tarjeta muestra el título y el número correctamente en pantalla | Si los datos no aparecieran visualmente en el panel |
| "renderiza el sub cuando se provee" | Si se pasa un subtítulo (ej. "+3 vs ayer"), aparece en la tarjeta | Si el subtítulo se perdiera y el usuario no viera la variación |
| "omite el sub cuando no se provee" | Sin subtítulo, la tarjeta no muestra texto basura como "undefined" | Si la tarjeta mostrara errores visuales al no recibir todos los datos |
| "aplica el color del tone correctamente" | En tono `danger`, el subtítulo se pinta de rojo oscuro para alertar | Si los colores de alerta no funcionaran y el usuario no distinguiera un indicador crítico |
| "usa color neutral por defecto" | Sin tono especificado, el subtítulo usa gris neutro | Si el componente lanzara un error cuando no se le indica un tono |

---

## 4. Tests de integración del frontend (6 tests)
**Archivo:** `frontend/src/__tests__/pages/Login.test.jsx`

Simulan el uso real del formulario de login tal como lo vive el usuario: hacen clic, escriben texto, y verifican lo que aparece en pantalla. Las llamadas al servidor son interceptadas por un servidor simulado (MSW) para que las pruebas sean predecibles.

| Test | Qué verifica | Cuándo fallaría |
|------|--------------|-----------------|
| "muestra el formulario con campos requeridos" | Al abrir la página de login aparecen el campo de correo, el de contraseña y el botón "Ingresar" | Si el formulario no cargara o le faltaran elementos |
| "muestra error si faltan campos" | Hacer clic en "Ingresar" sin rellenar los campos muestra un mensaje de advertencia | Si el sistema enviara el formulario vacío sin ninguna validación |
| "login exitoso llama onLogin con los datos del usuario y guarda token" | Al ingresar credenciales correctas, el token se guarda en el navegador y la aplicación reconoce al usuario como logueado | Si el token no se guardara o la sesión no se iniciara correctamente |
| "credenciales inválidas incrementan el contador de intentos" | Al fallar el login, aparece un contador visible "Intento 1/5" | Si el usuario no supiera cuántos intentos le quedan antes del bloqueo |
| "bloquea el formulario tras 5 intentos fallidos" | Tras el quinto fallo consecutivo, el formulario se desactiva y aparece el mensaje "cuenta bloqueada" | Si el bloqueo del lado visual no funcionara y el usuario pudiera seguir intentando |
| "muestra error de conexión si la red falla" | Cuando el servidor no responde, aparece el aviso "no se pudo conectar" | Si el sistema se colgara silenciosamente sin informar al usuario |

---

## 5. Por qué existen varias formas de ejecutar los tests

Cada comando está pensado para un momento distinto del desarrollo. No son redundantes; cada uno sirve a un propósito concreto.

### Backend

| Comando | Para qué sirve | Cuándo se usa |
|---------|---------------|---------------|
| `pytest` | Corre todos los tests | Antes de fusionar cambios o hacer una entrega |
| `pytest tests/unit` | Solo los tests unitarios (más rápidos) | Durante el desarrollo, para verificar la lógica sin esperar |
| `pytest tests/integration` | Solo los tests de endpoints | Cuando se modifica un endpoint o la lógica de autenticación |
| `pytest --cov=app` | Todos los tests + reporte de cobertura | Para verificar que se cumple el objetivo del ≥70% (RNF05) |
| `pytest -m "not postgres"` | Omite tests que requieren PostgreSQL real | Para correr la suite en cualquier computadora sin base de datos |

### Frontend

| Comando | Para qué sirve | Cuándo se usa |
|---------|---------------|---------------|
| `npm test` | Corre todos los tests una vez | Antes de un commit o entrega |
| `npm run test:watch` | Corre tests automáticamente al guardar un archivo | Durante el desarrollo activo (ciclo continuo) |
| `npm run test:coverage` | Tests + reporte HTML navegable de cobertura | Para ver visualmente qué partes del frontend no tienen tests |

> **Analogía para el docente:** es como tener un manual de una máquina. Puedes hacer una revisión rápida (5 minutos), una revisión completa (30 minutos) o generar un informe técnico completo (con reporte de cobertura). Cada nivel sirve a un propósito distinto y los tres son correctos según el contexto.
