-- ============================================================
-- MetroHub — Datos iniciales de prueba (seed)
-- ============================================================
-- Importante: los password_hash están generados con bcrypt
-- para los passwords:
--   admin123      -> admin@atu.gob.pe
--   super123      -> supervisor@empresa.com
-- ============================================================

INSERT INTO concesionarios (nombre, ruc, contacto_email, contacto_telefono) VALUES
    ('Empresa Lima Norte SAC',  '20100100100', 'contacto@limanorte.pe',  '014701000'),
    ('Empresa Lima Sur SAC',    '20100200200', 'contacto@limasur.pe',    '014702000'),
    ('Empresa Lima Centro SAC', '20100300300', 'contacto@limacentro.pe', '014703000')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO usuarios (email, password_hash, nombre, rol, concesionario_id) VALUES
    ('admin@atu.gob.pe',
     '$2b$12$KIXJBYgOgK/qXKLZZYyq8.TmKb5ZaVvNGN7YvD8dGHvR8rZxYqjFa',
     'Administrador ATU',
     'admin_atu',
     NULL),
    ('supervisor@empresa.com',
     '$2b$12$5GZ2kS3bX.sFwVqXaP9W6e8vN7rT2qWcLK3XzNfYH4L5DaZ6KdXvW',
     'Supervisor Lima Norte',
     'supervisor',
     1)
ON CONFLICT (email) DO NOTHING;

INSERT INTO estaciones (nombre, latitud, longitud, capacidad_operativa) VALUES
    ('Naranjal',    -11.9856, -77.0648, 5000),
    ('Matellini',   -12.1745, -77.0289, 3500),
    ('Barranco',    -12.1483, -77.0218, 2800),
    ('Plaza Mayor', -12.0464, -77.0306, 4200),
    ('Tomas Valle', -12.0156, -77.0612, 3000),
    ('Caquetá',     -12.0367, -77.0489, 2500)
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO rutas (codigo, nombre, estacion_inicio_id, estacion_fin_id,
                   frecuencia_base, concesionario_id, activa) VALUES
    ('RUTA-A',    'Ruta A — Naranjal a Matellini',    1, 2, 3, 1, TRUE),
    ('RUTA-B',    'Ruta B — Naranjal a Barranco',     1, 3, 5, 2, TRUE),
    ('EXPRESO-1', 'Expreso 1 — Naranjal a Plaza Mayor', 1, 4, 4, 3, TRUE)
ON CONFLICT (codigo) DO NOTHING;

INSERT INTO unidades (placa, modelo, capacidad, concesionario_id, estado) VALUES
    ('ABC-001', 'Volvo B7R',          80, 1, 'operativa'),
    ('ABC-002', 'Volvo B7R',          80, 1, 'operativa'),
    ('XYZ-101', 'Mercedes-Benz O500', 90, 2, 'operativa'),
    ('ZZZ-501', 'Scania K310',        85, 3, 'operativa'),
    ('ABC-099', 'Volvo B7R',          80, 1, 'mantenimiento')
ON CONFLICT (placa) DO NOTHING;

INSERT INTO choferes (nombre, apellido, dni, licencia, tipo_licencia,
                      vencimiento_licencia, concesionario_id, disponibilidad) VALUES
    ('Carlos', 'Mamani', '45678901', 'L-001234', 'A3', '2026-08-15', 1, 'disponible'),
    ('Jorge',  'Quispe', '34567890', 'L-005678', 'A3', '2025-12-01', 1, 'descanso'),
    ('Luis',   'Flores', '56789012', 'L-009012', 'A2', '2026-03-20', 2, 'disponible')
ON CONFLICT (dni) DO NOTHING;

INSERT INTO horarios (ruta_id, chofer_id, unidad_id, fecha,
                      hora_salida, hora_llegada, turno, estado) VALUES
    (1, 1, 1, '2026-04-28', '06:00', '14:00', 'manana', 'aprobado'),
    (2, 3, 3, '2026-04-28', '14:00', '22:00', 'tarde',  'aprobado')
ON CONFLICT DO NOTHING;
