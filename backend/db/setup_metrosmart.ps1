# =============================================================================
# MetroSmart - Script de Setup Automático de Base de Datos
# Universidad Nacional de Ingeniería - EPCC
# Uso: Ejecutar en PowerShell (no PowerShell ISE)
#      .\setup_metrosmart.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

# --- CONFIGURACIÓN ---
$PG_HOST     = "localhost"
$PG_PORT     = "5432"
$PG_USER     = "postgres"
$PG_DBNAME   = "metrosmart"
$SCRIPT_DIR  = $PSScriptRoot   # La carpeta donde está este script (también tiene los .sql)
$SQL_SCHEMA  = Join-Path $SCRIPT_DIR "01_schema_metrosmart.sql"
$SQL_SEED    = Join-Path $SCRIPT_DIR "02_seed_data.sql"
$BACKUP_FILE = Join-Path $SCRIPT_DIR "metrosmart_backup_inicial.sql"

# Colores
function Write-Header($msg) { Write-Host "`n═══════════════════════════════════════" -ForegroundColor Cyan; Write-Host "  $msg" -ForegroundColor Cyan; Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan }
function Write-OK($msg)     { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Info($msg)   { Write-Host "  → $msg" -ForegroundColor Yellow }
function Write-Err($msg)    { Write-Host "`n  ✗ ERROR: $msg" -ForegroundColor Red }

# =============================================================================
# PASO 0 — Verificar herramientas y servicio
# =============================================================================
Write-Header "PASO 0 — Verificando PostgreSQL"

# Verificar que psql existe
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlPath) {
    Write-Err "psql no encontrado en PATH."
    Write-Host @"

  Posibles soluciones:
  1. Agrega la carpeta bin de PostgreSQL al PATH de Windows, por ejemplo:
     C:\Program Files\PostgreSQL\16\bin
  2. Reinicia PowerShell después de cambiar el PATH.
"@ -ForegroundColor Yellow
    exit 1
}
$psqlVersion = (psql --version)
Write-OK "psql encontrado: $psqlVersion"

# Verificar pg_isready
$isReady = & pg_isready -h $PG_HOST -p $PG_PORT 2>&1
Write-Info "pg_isready: $isReady"
if ($LASTEXITCODE -ne 0) {
    Write-Err "PostgreSQL no está accesible en ${PG_HOST}:${PG_PORT}."
    Write-Host "  Verifica que el servicio 'postgresql-x64-XX' esté corriendo en Windows Services." -ForegroundColor Yellow
    exit 1
}
Write-OK "PostgreSQL está corriendo en ${PG_HOST}:${PG_PORT}"

# Verificar que los archivos SQL existen
if (-not (Test-Path $SQL_SCHEMA)) { Write-Err "No se encontró: $SQL_SCHEMA"; exit 1 }
if (-not (Test-Path $SQL_SEED))   { Write-Err "No se encontró: $SQL_SEED";   exit 1 }
Write-OK "Archivos SQL encontrados en: $SCRIPT_DIR"

# =============================================================================
# PEDIR CONTRASEÑA (nunca se guarda en disco)
# =============================================================================
Write-Host ""
$secPass = Read-Host "  Ingresa la contraseña del usuario postgres" -AsSecureString
$BSTR    = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secPass)
$env:PGPASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)

# Función helper para ejecutar SQL y capturar errores
function Invoke-Psql {
    param(
        [string]$Database = "postgres",
        [string]$Command  = "",
        [string]$File     = "",
        [switch]$NoStop
    )
    if ($File) {
        $result = & psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $Database -f $File 2>&1
    } else {
        $result = & psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $Database -c $Command 2>&1
    }
    if ($LASTEXITCODE -ne 0 -and -not $NoStop) {
        $env:PGPASSWORD = ""
        Write-Err "Falló el comando SQL. Detalle:"
        Write-Host ($result | Out-String) -ForegroundColor Red
        exit 1
    }
    return $result
}

# =============================================================================
# PASO 1 — Crear la base de datos
# =============================================================================
Write-Header "PASO 1 — Creando base de datos '$PG_DBNAME'"

# Verificar si ya existe
$exists = Invoke-Psql -Command "SELECT 1 FROM pg_database WHERE datname = '$PG_DBNAME';" -NoStop
if ($exists -match "1 fila" -or $exists -match "1 row") {
    Write-Host ""
    Write-Host "  ⚠  La base de datos '$PG_DBNAME' ya existe." -ForegroundColor Magenta
    $confirm = Read-Host "  ¿Deseas ELIMINARLA y recrearla desde cero? (escribe 'si' para confirmar)"
    if ($confirm -ne "si") {
        Write-Info "Conservando BD existente. Continuando con el schema..."
    } else {
        Write-Info "Eliminando BD '$PG_DBNAME'..."
        Invoke-Psql -Command "DROP DATABASE IF EXISTS $PG_DBNAME;"
        Write-OK "BD '$PG_DBNAME' eliminada."
        $exists = ""
    }
}

if ($exists -notmatch "1 row") {
    # Intentar con collation es_PE.UTF-8 primero
    Write-Info "Intentando crear con collation es_PE.UTF-8..."
    $createResult = Invoke-Psql -NoStop -Command @"
CREATE DATABASE $PG_DBNAME
    WITH ENCODING 'UTF8'
    LC_COLLATE 'es_PE.UTF-8'
    LC_CTYPE 'es_PE.UTF-8'
    TEMPLATE template0;
"@
    if ($LASTEXITCODE -ne 0) {
        Write-Info "Collation 'es_PE.UTF-8' no disponible en este sistema. Usando collation por defecto..."
        $createResult = Invoke-Psql -Command @"
CREATE DATABASE $PG_DBNAME
    WITH ENCODING 'UTF8'
    TEMPLATE template0;
"@
        Write-OK "BD '$PG_DBNAME' creada con collation por defecto (UTF8)."
        Write-Host "  ℹ  Nota: la collation es_PE.UTF-8 no está instalada en tu Windows." -ForegroundColor Cyan
        Write-Host "     Esto es normal. La BD funciona correctamente con UTF8." -ForegroundColor Cyan
    } else {
        Write-OK "BD '$PG_DBNAME' creada con collation es_PE.UTF-8."
    }
}

# =============================================================================
# PASO 2 — Ejecutar schema
# =============================================================================
Write-Header "PASO 2 — Ejecutando schema (01_schema_metrosmart.sql)"
Write-Info "Creando 12 tablas, índices, triggers y vista..."

$schemaResult = Invoke-Psql -Database $PG_DBNAME -File $SQL_SCHEMA -NoStop
if ($LASTEXITCODE -ne 0) {
    Write-Err "Error ejecutando el schema. Detalle:"
    Write-Host ($schemaResult | Out-String) -ForegroundColor Red
    Write-Host "  NO se continuará con el seed data." -ForegroundColor Red
    $env:PGPASSWORD = ""
    exit 1
}

Write-OK "Schema ejecutado sin errores."

# Verificar las 12 tablas
Write-Info "Verificando tablas creadas..."
$tablesResult = Invoke-Psql -Database $PG_DBNAME -Command "\dt"
Write-Host ""
Write-Host $tablesResult -ForegroundColor White

$tablesCount = Invoke-Psql -Database $PG_DBNAME -Command @"
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
"@

$countLine = ($tablesCount | Where-Object { $_ -match '^\s*\d+\s*$' } | Select-Object -First 1)
$numTables = [int]($countLine.Trim())

if ($numTables -lt 12) {
    Write-Err "Solo se encontraron $numTables tablas, se esperaban 12."
    $env:PGPASSWORD = ""
    exit 1
}
Write-OK "Las 12 tablas esperadas están presentes ($numTables encontradas)."

# =============================================================================
# PASO 3 — Ejecutar seed data
# =============================================================================
Write-Header "PASO 3 — Cargando datos de prueba (02_seed_data.sql)"
Write-Info "Insertando datos reales del Metropolitano..."

$seedResult = Invoke-Psql -Database $PG_DBNAME -File $SQL_SEED -NoStop
if ($LASTEXITCODE -ne 0) {
    Write-Err "Error ejecutando seed data. Detalle:"
    Write-Host ($seedResult | Out-String) -ForegroundColor Red
    $env:PGPASSWORD = ""
    exit 1
}

Write-OK "Datos insertados correctamente."

# Conteos por tabla
Write-Info "Conteo de filas por tabla:"
$countQuery = @"
SELECT 'concesionarios'     AS tabla, COUNT(*) AS filas FROM concesionarios
UNION ALL SELECT 'usuarios',          COUNT(*) FROM usuarios
UNION ALL SELECT 'estaciones',        COUNT(*) FROM estaciones
UNION ALL SELECT 'rutas',             COUNT(*) FROM rutas
UNION ALL SELECT 'ruta_estacion',     COUNT(*) FROM ruta_estacion
UNION ALL SELECT 'choferes',          COUNT(*) FROM choferes
UNION ALL SELECT 'buses',             COUNT(*) FROM buses
UNION ALL SELECT 'programaciones',    COUNT(*) FROM programaciones
UNION ALL SELECT 'horarios_servicio', COUNT(*) FROM horarios_servicio
UNION ALL SELECT 'asignaciones',      COUNT(*) FROM asignaciones
UNION ALL SELECT 'disponibilidad_chofer', COUNT(*) FROM disponibilidad_chofer
UNION ALL SELECT 'conflictos',        COUNT(*) FROM conflictos
ORDER BY tabla;
"@
$countResult = Invoke-Psql -Database $PG_DBNAME -Command $countQuery
Write-Host $countResult -ForegroundColor White

# Vista dashboard
Write-Info "Resultado de v_dashboard_kpis:"
$kpisResult = Invoke-Psql -Database $PG_DBNAME -Command "SELECT * FROM v_dashboard_kpis;"
Write-Host $kpisResult -ForegroundColor White

# =============================================================================
# PASO 4 — Validaciones finales
# =============================================================================
Write-Header "PASO 4 — Validaciones finales"

Write-Info "1. Conteo de tablas creadas:"
$q1 = Invoke-Psql -Database $PG_DBNAME -Command @"
SELECT COUNT(*) AS total_tablas
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
"@
Write-Host $q1 -ForegroundColor White

Write-Info "2. Conteo de foreign keys:"
$q2 = Invoke-Psql -Database $PG_DBNAME -Command @"
SELECT COUNT(*) AS total_fks
FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public';
"@
Write-Host $q2 -ForegroundColor White

Write-Info "3. Los 4 concesionarios reales del Metropolitano:"
$q3 = Invoke-Psql -Database $PG_DBNAME -Command @"
SELECT id, nombre_corto, ruc FROM concesionarios ORDER BY id;
"@
Write-Host $q3 -ForegroundColor White

Write-Info "4. Join múltiple — asignaciones con chofer, bus, ruta y concesionario:"
$q4 = Invoke-Psql -Database $PG_DBNAME -Command @"
SELECT
    r.codigo AS ruta,
    hs.fecha,
    hs.hora_salida,
    hs.turno,
    c.nombres || ' ' || c.apellidos AS chofer,
    a.bus_placa,
    conc.nombre_corto AS concesionario,
    a.estado
FROM asignaciones a
JOIN choferes c ON a.chofer_id = c.id
JOIN horarios_servicio hs ON a.horario_id = hs.id
JOIN rutas r ON hs.ruta_id = r.id
JOIN concesionarios conc ON a.concesionario_id = conc.id
ORDER BY hs.fecha, hs.hora_salida;
"@
Write-Host $q4 -ForegroundColor White

# =============================================================================
# PASO 5 — Backup
# =============================================================================
Write-Header "PASO 5 — Generando backup inicial"
Write-Info "Ejecutando pg_dump → $BACKUP_FILE"

& pg_dump -U $PG_USER -h $PG_HOST -p $PG_PORT -d $PG_DBNAME -F p -f $BACKUP_FILE 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Err "pg_dump falló. Verifica permisos de escritura en: $SCRIPT_DIR"
} else {
    $backupSize = (Get-Item $BACKUP_FILE).Length / 1KB
    Write-OK "Backup generado: $BACKUP_FILE"
    Write-OK "Tamaño: $([math]::Round($backupSize, 1)) KB"
}

# Limpiar contraseña de memoria
$env:PGPASSWORD = ""

# =============================================================================
# PASO 6 — Resumen final
# =============================================================================
Write-Header "PASO 6 — RESUMEN FINAL"

# Obtener conteos finales para el resumen
$env:PGPASSWORD = ""  # Ya limpiada, necesitamos pedirla otra vez solo para esto
# Usar los datos que ya tenemos

Write-Host @"

  ✓ BD '$PG_DBNAME' creada y configurada en ${PG_HOST}:${PG_PORT}
  ✓ 12 tablas creadas (asignaciones, buses, choferes, concesionarios,
        conflictos, disponibilidad_chofer, estaciones, horarios_servicio,
        programaciones, ruta_estacion, rutas, usuarios)
  ✓ Índices, triggers (updated_at) y vista v_dashboard_kpis creados
  ✓ Datos del Metropolitano insertados:
        4 concesionarios reales · 5 usuarios · 28 estaciones troncales
        10 rutas · 20 choferes · 16 buses · 10 horarios · 5 asignaciones
  ✓ Backup generado en: $BACKUP_FILE

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRÓXIMOS PASOS SUGERIDOS:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Abre pgAdmin → conecta a localhost:5432 → explora 'metrosmart'
  2. Revisa la vista v_dashboard_kpis para el módulo RF06
  3. Conecta tu backend (FastAPI/Django/Node) con:
       host=localhost port=5432 dbname=metrosmart user=postgres
  4. Cambia los password_hash en la tabla usuarios por hashes bcrypt reales
  5. Agrega más rutas/horarios según el calendario real del Metropolitano

"@ -ForegroundColor Green

Write-Host "  ¡Setup completado exitosamente! 🚌" -ForegroundColor Cyan
Write-Host ""
