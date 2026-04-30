-- =============================================================================
-- MetroSmart v2.0 - Datos de Prueba
-- Datos basados en información pública del Metropolitano de Lima (ATU)
-- Ejecutar DESPUÉS de 01_schema_metrosmart.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. CONCESIONARIOS (los 4 reales del Metropolitano)
-- -----------------------------------------------------------------------------
INSERT INTO concesionarios (ruc, razon_social, nombre_corto, telefono, email_contacto) VALUES
('20513967720', 'Lima Vías Express S.A.',           'Lima Vías Express',    '014567890', 'contacto@limaviasexpress.pe'),
('20524893451', 'Lima Bus Internacional S.A.',      'Lima Bus',             '014789012', 'operaciones@limabus.pe'),
('20545678901', 'Transvial Lima S.A.C.',            'Transvial',            '014234567', 'contacto@transvial.pe'),
('20556789234', 'Perú Masivo S.A.',                 'Perú Masivo',          '014345678', 'info@perumasivo.pe');

-- -----------------------------------------------------------------------------
-- 2. USUARIOS (1 admin ATU + 4 supervisores, uno por concesionario)
-- -----------------------------------------------------------------------------
INSERT INTO usuarios (email, password_hash, nombre, apellidos, dni, rol, concesionario_id) VALUES
('admin.atu@metrosmart.gob.pe',     '$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef', 'María',   'Quispe Rivera',     '72839401', 'admin_atu', NULL),
('sup.limavias@metrosmart.gob.pe',  '$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef', 'Carlos',  'Ramírez Torres',    '45892013', 'supervisor_concesionario', 1),
('sup.limabus@metrosmart.gob.pe',   '$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef', 'Lucía',   'Morales Salinas',   '41203987', 'supervisor_concesionario', 2),
('sup.transvial@metrosmart.gob.pe', '$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef', 'Jorge',   'Vega Mendoza',      '43897201', 'supervisor_concesionario', 3),
('sup.perumasivo@metrosmart.gob.pe','$2b$12$REEMPLAZAR_CON_HASH_REAL_BCRYPT_AQUI_1234567890abcdef', 'Ana',     'Ccahuana Pérez',    '47123890', 'supervisor_concesionario', 4);

-- -----------------------------------------------------------------------------
-- 3. ESTACIONES TRONCALES (subset representativo)
--    Orden troncal: norte (1) -> sur (N)
-- -----------------------------------------------------------------------------
INSERT INTO estaciones (codigo, nombre, tipo, tramo, orden_troncal, latitud, longitud) VALUES
-- TRAMO NORTE
('EST-CHO',  'Chimpu Ocllo',     'terminal',     'norte',   1,  -11.87480,  -77.02950),
('EST-LIN',  'Los Incas',        'intermedia',   'norte',   2,  -11.94800,  -77.05300),
('EST-UNI',  'Universidad',      'intermedia',   'norte',   3,  -11.98500,  -77.05800),
('EST-NAR',  'Naranjal',         'terminal',     'norte',   4,  -11.99100,  -77.06100),
('EST-IZA',  'Izaguirre',        'intermedia',   'norte',   5,  -11.99700,  -77.06400),
('EST-PAC',  'Pacífico',         'intermedia',   'norte',   6,  -12.00200,  -77.06000),
('EST-INA',  'Independencia',    'intermedia',   'norte',   7,  -12.00900,  -77.05700),
('EST-TV',   'Tomás Valle',      'intermedia',   'norte',   8,  -12.01500,  -77.05400),
-- TRAMO CENTRO
('EST-CAQ',  'Caquetá',          'intermedia',   'centro',  9,  -12.02800,  -77.04800),
('EST-PP',   'Parque del Trabajo','intermedia',  'centro', 10,  -12.03500,  -77.04500),
('EST-RCA',  'Ramón Castilla',   'intermedia',   'centro', 11,  -12.04200,  -77.04100),
('EST-TAC',  'Tacna',            'intermedia',   'centro', 12,  -12.04800,  -77.03700),
('EST-JDU',  'Jirón de la Unión','intermedia',   'centro', 13,  -12.05100,  -77.03400),
('EST-COL',  'Colmena',          'intermedia',   'centro', 14,  -12.05400,  -77.03200),
('EST-CEN',  'Estación Central', 'transferencia','centro', 15,  -12.05800,  -77.03000),
('EST-ENA',  'Estadio Nacional', 'intermedia',   'centro', 16,  -12.06700,  -77.03200),
('EST-MEX',  'México',           'intermedia',   'centro', 17,  -12.07400,  -77.02900),
('EST-CAN',  'Canadá',           'intermedia',   'centro', 18,  -12.08100,  -77.02600),
-- TRAMO SUR
('EST-JAV',  'Javier Prado',     'intermedia',   'sur',    19,  -12.09000,  -77.02100),
('EST-CYM',  'Canaval y Moreyra','intermedia',   'sur',    20,  -12.09700,  -77.02000),
('EST-ARA',  'Aramburú',         'intermedia',   'sur',    21,  -12.10400,  -77.01900),
('EST-DOM',  'Domingo Orué',     'intermedia',   'sur',    22,  -12.10900,  -77.02100),
('EST-ANG',  'Angamos',          'intermedia',   'sur',    23,  -12.11400,  -77.02300),
('EST-RPA',  'Ricardo Palma',    'intermedia',   'sur',    24,  -12.12000,  -77.02700),
('EST-BEN',  'Benavides',        'intermedia',   'sur',    25,  -12.12600,  -77.03100),
('EST-28J',  '28 de Julio',      'intermedia',   'sur',    26,  -12.13200,  -77.02900),
('EST-PFL',  'Plaza de Flores',  'intermedia',   'sur',    27,  -12.13800,  -77.02700),
('EST-MAT',  'Matellini',        'terminal',     'sur',    28,  -12.18100,  -77.01400);

-- -----------------------------------------------------------------------------
-- 4. RUTAS TRONCALES
-- -----------------------------------------------------------------------------
INSERT INTO rutas (codigo, nombre, tipo, hora_inicio, hora_fin, frecuencia_min) VALUES
('A',   'Ruta A - Naranjal a Estación Central',          'regular',  '05:00', '22:30',  6),
('B',   'Ruta B - Naranjal a Plaza de Flores',           'regular',  '05:00', '22:30',  8),
('C',   'Ruta C - Ramón Castilla a Matellini',           'regular',  '05:00', '22:30',  8),
('EX1', 'Expreso 1 - Naranjal a Matellini',              'expreso',  '05:30', '21:30',  5),
('EX2', 'Expreso 2 - Naranjal a Ricardo Palma',          'expreso',  '05:30', '21:30',  6),
('EX5', 'Expreso 5 - Naranjal a Angamos',                'expreso',  '05:30', '21:30',  6),
('EX7', 'Expreso 7 - Tomás Valle a Angamos',             'expreso',  '06:00', '21:00',  8),
('EX8', 'Expreso 8 - Naranjal a Benavides',              'expreso',  '05:30', '21:30',  7),
('EX9', 'Expreso 9 - Naranjal a Benavides (semidirecto)','expreso',  '05:30', '21:30',  7),
('N',   'Ruta Nocturna - Naranjal a Matellini',          'nocturna', '23:30', '04:00', 20);

-- -----------------------------------------------------------------------------
-- 5. RUTA_ESTACION (asignación de paraderos por ruta)
-- -----------------------------------------------------------------------------
-- Ruta A: Naranjal -> Estación Central
INSERT INTO ruta_estacion (ruta_id, estacion_id, orden, tiempo_est_min) VALUES
(1, 4,  1, 0), (1, 5,  2, 3),  (1, 6,  3, 6),  (1, 7,  4, 9),  (1, 8,  5, 12),
(1, 9,  6, 16),(1, 10, 7, 19), (1, 11, 8, 22), (1, 12, 9, 25), (1, 13, 10, 28),
(1, 14, 11, 31),(1, 15, 12, 35);

-- Ruta C: Ramón Castilla -> Matellini
INSERT INTO ruta_estacion (ruta_id, estacion_id, orden, tiempo_est_min) VALUES
(3, 11, 1,  0), (3, 12, 2,  3), (3, 13, 3,  6), (3, 14, 4,  9), (3, 15, 5,  12),
(3, 16, 6,  17),(3, 17, 7,  21),(3, 18, 8,  25),(3, 19, 9,  30),(3, 20, 10, 34),
(3, 21, 11, 38),(3, 22, 12, 42),(3, 23, 13, 46),(3, 24, 14, 50),(3, 25, 15, 54),
(3, 26, 16, 58),(3, 27, 17, 62),(3, 28, 18, 75);

-- Expreso 1: Naranjal -> Matellini (solo estaciones clave)
INSERT INTO ruta_estacion (ruta_id, estacion_id, orden, tiempo_est_min) VALUES
(4, 4,  1, 0), (4, 15, 2, 25), (4, 16, 3, 30), (4, 19, 4, 38),
(4, 20, 5, 42),(4, 23, 6, 48), (4, 26, 7, 55), (4, 28, 8, 68);

-- -----------------------------------------------------------------------------
-- 6. CHOFERES (20 choferes distribuidos entre los 4 concesionarios)
-- -----------------------------------------------------------------------------
INSERT INTO choferes (dni, nombres, apellidos, fecha_nacimiento, telefono, email, concesionario_id, numero_licencia, tipo_licencia, fec_vence_licencia, fec_vence_certif_prot, estado, anios_experiencia) VALUES
-- Lima Vías Express
('44156789', 'Juan Manuel',   'Huamán Flores',    '1985-03-12', '987654321', 'jhuaman@limaviasexpress.pe',   1, 'Q12345678', 'A-IIIA', '2027-06-30', '2026-08-15', 'activo', 12),
('45892314', 'Roberto',       'Castillo Vera',    '1979-11-23', '987123456', 'rcastillo@limaviasexpress.pe', 1, 'Q23456789', 'A-IIIA', '2026-12-15', '2026-05-20', 'activo', 15),
('46789012', 'Pedro',         'Quispe Mendoza',   '1988-07-04', '986543210', 'pquispe@limaviasexpress.pe',   1, 'Q34567890', 'A-IIIC', '2027-03-10', '2026-11-02', 'activo', 8),
('42345678', 'Luis Alberto',  'Gonzales Pariona', '1975-02-18', '985432109', 'lgonzales@limaviasexpress.pe', 1, 'Q45678901', 'A-IIIA', '2026-09-25', '2026-07-18', 'activo', 20),
('47234567', 'Cinthia',       'Soldevilla Ríos',  '1986-09-15', '984321098', 'csoldevilla@limaviasexpress.pe',1,'Q56789012','A-IIIC', '2028-01-20', '2027-02-10', 'activo', 6),
-- Lima Bus Internacional
('43678912', 'Miguel Ángel',  'Torres Huanca',    '1982-05-30', '983210987', 'mtorres@limabus.pe',           2, 'Q67890123', 'A-IIIA', '2026-11-12', '2026-06-25', 'activo', 14),
('44987654', 'Cesar',         'Ramos Vilca',      '1990-12-08', '982109876', 'cramos@limabus.pe',            2, 'Q78901234', 'A-IIIC', '2027-08-05', '2026-09-30', 'activo', 5),
('45123698', 'Walter',        'Gálvez Mamani',    '1984-04-22', '981098765', 'wgalvez@limabus.pe',           2, 'Q89012345', 'A-IIIA', '2027-05-18', '2026-04-28', 'vacaciones', 11),
('46456789', 'Arturo',        'Napa Marcos',      '1972-08-11', '980987654', 'anapa@limabus.pe',             2, 'Q90123456', 'A-IIIC', '2026-10-30', '2026-12-15', 'activo', 22),
('43852147', 'Ricardo',       'Suárez Ccopa',     '1987-01-25', '979876543', 'rsuarez@limabus.pe',           2, 'Q01234567', 'A-IIIA', '2027-11-08', '2027-01-22', 'activo', 9),
-- Transvial Lima
('44963852', 'Fernando',      'Huertas Ayala',    '1981-06-14', '978765432', 'fhuertas@transvial.pe',        3, 'Q11122233', 'A-IIIA', '2026-08-22', '2026-05-10', 'activo', 13),
('45741963', 'Víctor',        'Mellado Ramírez',  '1976-10-02', '977654321', 'vmellado@transvial.pe',        3, 'Q22233344', 'A-IIIA', '2027-02-14', '2026-10-18', 'activo', 18),
('46258147', 'Eduardo',       'Pérez Condori',    '1989-03-19', '976543210', 'eperez@transvial.pe',          3, 'Q33344455', 'A-IIIC', '2027-07-26', '2026-08-30', 'activo', 7),
('43159753', 'Hugo',          'Valencia Chávez',  '1978-12-05', '975432109', 'hvalencia@transvial.pe',       3, 'Q44455566', 'A-IIIA', '2026-07-11', '2026-03-25', 'licencia_medica', 16),
('47852963', 'Junior',        'Córdova Fernández','1991-08-28', '974321098', 'jcordova@transvial.pe',        3, 'Q55566677', 'A-IIIC', '2028-04-03', '2027-03-15', 'activo', 4),
-- Perú Masivo
('44753159', 'Alberto',       'Paredes Yupanqui', '1983-11-17', '973210987', 'aparedes@perumasivo.pe',       4, 'Q66677788', 'A-IIIA', '2027-01-29', '2026-06-12', 'activo', 11),
('45951357', 'Daniel',        'Rojas Limachi',    '1986-02-09', '972109876', 'drojas@perumasivo.pe',         4, 'Q77788899', 'A-IIIA', '2026-12-06', '2026-09-05', 'activo', 10),
('46357159', 'Raúl',          'Cárdenas Pérez',   '1980-07-21', '971098765', 'rcardenas@perumasivo.pe',      4, 'Q88899900', 'A-IIIC', '2027-06-14', '2026-04-08', 'activo', 15),
('43951753', 'Enrique',       'Lozano Machaca',   '1974-05-06', '970987654', 'elozano@perumasivo.pe',        4, 'Q99900011', 'A-IIIA', '2026-09-17', '2026-11-25', 'activo', 21),
('47159951', 'Jorge Luis',    'Tello Quiñones',   '1988-10-31', '969876543', 'jtello@perumasivo.pe',         4, 'Q00011122', 'A-IIIC', '2027-12-22', '2027-04-30', 'activo', 7);

-- -----------------------------------------------------------------------------
-- 7. BUSES (16 buses: 4 articulados y 4 convencionales por concesionario, 3 por empresa)
-- -----------------------------------------------------------------------------
INSERT INTO buses (placa, concesionario_id, tipo, anio, capacidad_pasajeros, estado) VALUES
-- Lima Vías Express
('C1J-985', 1, 'articulado',   2018, 160, 'operativo'),
('C1J-986', 1, 'articulado',   2019, 160, 'operativo'),
('C1K-112', 1, 'articulado',   2020, 160, 'mantenimiento'),
('C2K-334', 1, 'convencional',  2017,  80, 'operativo'),
-- Lima Bus Internacional
('C1L-201', 2, 'articulado',   2018, 160, 'operativo'),
('C1L-202', 2, 'articulado',   2019, 160, 'operativo'),
('C1M-450', 2, 'articulado',   2021, 160, 'operativo'),
('C2M-778', 2, 'convencional',  2016,  80, 'reparacion'),
-- Transvial Lima
('C3A-001', 3, 'articulado',   2017, 160, 'operativo'),
('C3A-002', 3, 'articulado',   2018, 160, 'operativo'),
('C3B-123', 3, 'articulado',   2020, 160, 'operativo'),
('C4B-556', 3, 'convencional',  2018,  80, 'operativo'),
-- Perú Masivo
('C5D-701', 4, 'articulado',   2019, 160, 'operativo'),
('C5D-702', 4, 'articulado',   2020, 160, 'operativo'),
('C5E-890', 4, 'articulado',   2021, 160, 'operativo'),
('C6E-109', 4, 'convencional',  2017,  80, 'mantenimiento');

-- -----------------------------------------------------------------------------
-- 8. PROGRAMACIÓN de ejemplo (semana actual)
-- -----------------------------------------------------------------------------
INSERT INTO programaciones (nombre, fecha_inicio, fecha_fin, estado, creado_por, observaciones) VALUES
('Semana 17 - Abril 2026', '2026-04-20', '2026-04-26', 'borrador', 1, 'Programación inicial para validación del sistema');

-- -----------------------------------------------------------------------------
-- 9. HORARIOS_SERVICIO (ejemplo: Ruta A del lunes 21-abr)
-- -----------------------------------------------------------------------------
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(1, 1, '2026-04-21', '05:00', 'manana', 35),
(1, 1, '2026-04-21', '05:30', 'manana', 35),
(1, 1, '2026-04-21', '06:00', 'manana', 40),
(1, 1, '2026-04-21', '06:30', 'manana', 40),
(1, 1, '2026-04-21', '07:00', 'manana', 45),
(1, 1, '2026-04-21', '13:00', 'tarde', 40),
(1, 1, '2026-04-21', '13:30', 'tarde', 40),
(1, 1, '2026-04-21', '14:00', 'tarde', 40),
(1, 1, '2026-04-21', '18:00', 'tarde', 45),
(1, 1, '2026-04-21', '18:30', 'tarde', 45);

-- -----------------------------------------------------------------------------
-- 10. ASIGNACIONES (con choferes y buses de Lima Vías)
-- -----------------------------------------------------------------------------
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas) VALUES
(1, 1, 'C1J-985', 1, 'confirmada', 2, 'Asignación manual por supervisor'),
(2, 2, 'C1J-986', 1, 'confirmada', 2, 'Asignación manual por supervisor'),
(3, 3, 'C1J-985', 1, 'propuesta',  2, 'Chofer Pedro Quispe con bus C1J-985 (rotación)'),
(4, 4, 'C2K-334', 1, 'confirmada', 2, 'Bus convencional asignado'),
(5, 5, NULL,      1, 'propuesta',  2, 'Pendiente asignar bus operativo');

-- -----------------------------------------------------------------------------
-- 11. DISPONIBILIDAD (ejemplo: un chofer de vacaciones)
-- -----------------------------------------------------------------------------
INSERT INTO disponibilidad_chofer (chofer_id, fecha, hora_desde, hora_hasta, motivo, observaciones, registrado_por) VALUES
(8, '2026-04-21', '00:00', '23:59', 'vacaciones', 'Vacaciones programadas Abr 18-25', 3),
(8, '2026-04-22', '00:00', '23:59', 'vacaciones', 'Vacaciones programadas Abr 18-25', 3);

-- -----------------------------------------------------------------------------
-- 12. CONFLICTO de ejemplo
-- -----------------------------------------------------------------------------
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion) VALUES
(4, 'certif_prot_vencida', 'alta', 'La certificación Protransporte del chofer Luis Gonzales vence el 2026-07-18, dentro de 90 días.');

-- =============================================================================
-- VERIFICACIÓN
-- =============================================================================
SELECT 'Concesionarios: ' || COUNT(*) AS resultado FROM concesionarios
UNION ALL SELECT 'Usuarios: '      || COUNT(*) FROM usuarios
UNION ALL SELECT 'Estaciones: '    || COUNT(*) FROM estaciones
UNION ALL SELECT 'Rutas: '         || COUNT(*) FROM rutas
UNION ALL SELECT 'Ruta-Estacion: ' || COUNT(*) FROM ruta_estacion
UNION ALL SELECT 'Choferes: '      || COUNT(*) FROM choferes
UNION ALL SELECT 'Buses: '         || COUNT(*) FROM buses
UNION ALL SELECT 'Horarios: '      || COUNT(*) FROM horarios_servicio
UNION ALL SELECT 'Asignaciones: '  || COUNT(*) FROM asignaciones;

SELECT * FROM v_dashboard_kpis;
