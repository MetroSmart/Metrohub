-- =============================================================================
-- MetroHub v2.1 - Datos de Prueba
-- Datos representativos del Metropolitano de Lima (ATU)
-- Ejecutar DESPUÉS de 01_schema_metrohub.sql
-- Semana de referencia: junio 2026
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. ÁREAS OPERATIVAS (divisiones internas del Metropolitano)
-- -----------------------------------------------------------------------------
INSERT INTO areas_operativas (nombre, nombre_corto, descripcion) VALUES
('Operaciones Norte',    'Op. Norte',    'Gestión de rutas, choferes y buses del tramo norte del Metropolitano'),
('Operaciones Sur',      'Op. Sur',      'Gestión de rutas, choferes y buses del tramo sur del Metropolitano'),
('Mantenimiento de Flota', 'Mantenimiento', 'Supervisión del estado operativo de la flota de buses'),
('Turnos y Guardias',   'Turnos',       'Coordinación de turnos noche, guardias y servicios especiales');

-- -----------------------------------------------------------------------------
-- 2. USUARIOS (1 admin ATU + 4 supervisores de área)
-- Contraseña admin: admin123 | supervisores: ver README
-- -----------------------------------------------------------------------------
INSERT INTO usuarios (email, password_hash, nombre, apellidos, dni, rol, area_id) VALUES
('admin.atu@metrohub.gob.pe',         '$2b$12$/AeChPKE1TQAUab7o1HKwO3lH9RfGcX3.3NMdRGzAPtjE4q5HF31m', 'María',   'Quispe Rivera',   '72839401', 'admin_atu',       NULL),
('sup.norte@metrohub.gob.pe',         '$2b$12$jAHMoWqWX5x8CaWNw/5dvuVHQ5fxcbcz5N8tYf4gEWReJMYgyn9jq', 'Carlos',  'Ramírez Torres',  '45892013', 'supervisor_area', 1),
('sup.sur@metrohub.gob.pe',           '$2b$12$T3j5aI3I9WfuciRro.zwuusamaldXryYSlPBNOp0NHmiZ.zshK1x2',  'Lucía',   'Morales Salinas', '41203987', 'supervisor_area', 2),
('sup.mantenimiento@metrohub.gob.pe', '$2b$12$N9pjZBb/WGLA9YVJMGpkTe./GiYMgYrcMZcWkdWp7IhtX66glPKF6','Jorge',   'Vega Mendoza',    '43897201', 'supervisor_area', 3),
('sup.turnos@metrohub.gob.pe',        '$2b$12$FpFAYTtgbvJsORa6E6bYe.NLn7qBSoDpE/uiUS9xX1dx07fpAk2Zu', 'Ana',     'Ccahuana Pérez',  '47123890', 'supervisor_area', 4);

-- -----------------------------------------------------------------------------
-- 3. ESTACIONES TRONCALES (recorrido norte-sur)
-- -----------------------------------------------------------------------------
INSERT INTO estaciones (codigo, nombre, tipo, tramo, orden_troncal, latitud, longitud) VALUES
('EST-CHO', 'Chimpu Ocllo',      'terminal',     'norte',   1, -11.87480, -77.02950),
('EST-LIN', 'Los Incas',         'intermedia',   'norte',   2, -11.94800, -77.05300),
('EST-UNI', 'Universidad',       'intermedia',   'norte',   3, -11.98500, -77.05800),
('EST-NAR', 'Naranjal',          'terminal',     'norte',   4, -11.99100, -77.06100),
('EST-IZA', 'Izaguirre',         'intermedia',   'norte',   5, -11.99700, -77.06400),
('EST-PAC', 'Pacífico',          'intermedia',   'norte',   6, -12.00200, -77.06000),
('EST-INA', 'Independencia',     'intermedia',   'norte',   7, -12.00900, -77.05700),
('EST-TV',  'Tomás Valle',       'intermedia',   'norte',   8, -12.01500, -77.05400),
('EST-CAQ', 'Caquetá',           'intermedia',   'centro',  9, -12.02800, -77.04800),
('EST-PP',  'Parque del Trabajo','intermedia',   'centro', 10, -12.03500, -77.04500),
('EST-RCA', 'Ramón Castilla',    'intermedia',   'centro', 11, -12.04200, -77.04100),
('EST-TAC', 'Tacna',             'intermedia',   'centro', 12, -12.04800, -77.03700),
('EST-JDU', 'Jirón de la Unión', 'intermedia',   'centro', 13, -12.05100, -77.03400),
('EST-COL', 'Colmena',           'intermedia',   'centro', 14, -12.05400, -77.03200),
('EST-CEN', 'Estación Central',  'transferencia','centro', 15, -12.05800, -77.03000),
('EST-ENA', 'Estadio Nacional',  'intermedia',   'centro', 16, -12.06700, -77.03200),
('EST-MEX', 'México',            'intermedia',   'centro', 17, -12.07400, -77.02900),
('EST-CAN', 'Canadá',            'intermedia',   'centro', 18, -12.08100, -77.02600),
('EST-JAV', 'Javier Prado',      'intermedia',   'sur',    19, -12.09000, -77.02100),
('EST-CYM', 'Canaval y Moreyra', 'intermedia',   'sur',    20, -12.09700, -77.02000),
('EST-ARA', 'Aramburú',          'intermedia',   'sur',    21, -12.10400, -77.01900),
('EST-DOM', 'Domingo Orué',      'intermedia',   'sur',    22, -12.10900, -77.02100),
('EST-ANG', 'Angamos',           'intermedia',   'sur',    23, -12.11400, -77.02300),
('EST-RPA', 'Ricardo Palma',     'intermedia',   'sur',    24, -12.12000, -77.02700),
('EST-BEN', 'Benavides',         'intermedia',   'sur',    25, -12.12600, -77.03100),
('EST-28J', '28 de Julio',       'intermedia',   'sur',    26, -12.13200, -77.02900),
('EST-PFL', 'Plaza de Flores',   'intermedia',   'sur',    27, -12.13800, -77.02700),
('EST-MAT', 'Matellini',         'terminal',     'sur',    28, -12.18100, -77.01400);

-- -----------------------------------------------------------------------------
-- 4. RUTAS TRONCALES
-- -----------------------------------------------------------------------------
INSERT INTO rutas (codigo, nombre, tipo, hora_inicio, hora_fin, frecuencia_min) VALUES
('A',   'Ruta A - Naranjal a Estación Central',           'regular',  '05:00', '22:30',  6),
('B',   'Ruta B - Naranjal a Plaza de Flores',            'regular',  '05:00', '22:30',  8),
('C',   'Ruta C - Ramón Castilla a Matellini',            'regular',  '05:00', '22:30',  8),
('EX1', 'Expreso 1 - Naranjal a Matellini',               'expreso',  '05:30', '21:30',  5),
('EX2', 'Expreso 2 - Naranjal a Ricardo Palma',           'expreso',  '05:30', '21:30',  6),
('EX5', 'Expreso 5 - Naranjal a Angamos',                 'expreso',  '05:30', '21:30',  6),
('EX7', 'Expreso 7 - Tomás Valle a Angamos',              'expreso',  '06:00', '21:00',  8),
('EX8', 'Expreso 8 - Naranjal a Benavides',               'expreso',  '05:30', '21:30',  7),
('EX9', 'Expreso 9 - Naranjal a Benavides (semidirecto)', 'expreso',  '05:30', '21:30',  7),
('N',   'Ruta Nocturna - Naranjal a Matellini',           'nocturna', '23:30', '04:00', 20);

-- -----------------------------------------------------------------------------
-- 5. RUTA_ESTACION
-- -----------------------------------------------------------------------------
INSERT INTO ruta_estacion (ruta_id, estacion_id, orden, tiempo_est_min) VALUES
(1, 4, 1,0),(1, 5, 2,3),(1, 6, 3,6),(1, 7, 4,9),(1, 8, 5,12),
(1, 9, 6,16),(1,10, 7,19),(1,11, 8,22),(1,12, 9,25),(1,13,10,28),(1,14,11,31),(1,15,12,35);

INSERT INTO ruta_estacion (ruta_id, estacion_id, orden, tiempo_est_min) VALUES
(3,11, 1,0),(3,12, 2,3),(3,13, 3,6),(3,14, 4,9),(3,15, 5,12),
(3,16, 6,17),(3,17, 7,21),(3,18, 8,25),(3,19, 9,30),(3,20,10,34),
(3,21,11,38),(3,22,12,42),(3,23,13,46),(3,24,14,50),(3,25,15,54),
(3,26,16,58),(3,27,17,62),(3,28,18,75);

INSERT INTO ruta_estacion (ruta_id, estacion_id, orden, tiempo_est_min) VALUES
(4, 4,1,0),(4,15,2,25),(4,16,3,30),(4,19,4,38),(4,20,5,42),(4,23,6,48),(4,26,7,55),(4,28,8,68);

-- -----------------------------------------------------------------------------
-- 6. CHOFERES (20 choferes — estados y vencimientos variados para prueba)
--    Algunos vencimientos ya pasados (muestran alerta), otros próximos, otros lejanos
-- -----------------------------------------------------------------------------
INSERT INTO choferes (dni, nombres, apellidos, fecha_nacimiento, telefono, email, area_id, numero_licencia, tipo_licencia, fec_vence_licencia, fec_vence_certif_prot, estado, anios_experiencia) VALUES
-- Lima Vías Express — id 1-5
('44156789', 'Juan Manuel',  'Huamán Flores',     '1985-03-12', '987654321', 'jhuaman@limaviasexpress.pe',    1, 'Q12345678', 'A-IIIA', '2027-06-30', '2026-12-15', 'activo',        12),
('45892314', 'Roberto',      'Castillo Vera',      '1979-11-23', '987123456', 'rcastillo@limaviasexpress.pe',  1, 'Q23456789', 'A-IIIA', '2026-12-15', '2026-07-10', 'activo',        15),
('46789012', 'Pedro',        'Quispe Mendoza',     '1988-07-04', '986543210', 'pquispe@limaviasexpress.pe',    1, 'Q34567890', 'A-IIIC', '2027-03-10', '2026-11-02', 'activo',         8),
('42345678', 'Luis Alberto', 'Gonzales Pariona',   '1975-02-18', '985432109', 'lgonzales@limaviasexpress.pe',  1, 'Q45678901', 'A-IIIA', '2026-09-25', '2026-05-18', 'suspendido',    20),
('47234567', 'Cinthia',      'Soldevilla Ríos',    '1986-09-15', '984321098', 'csoldevilla@limaviasexpress.pe',1, 'Q56789012', 'A-IIIC', '2028-01-20', '2027-02-10', 'activo',         6),
-- Lima Bus Internacional — id 6-10
('43678912', 'Miguel Ángel', 'Torres Huanca',      '1982-05-30', '983210987', 'mtorres@limabus.pe',            2, 'Q67890123', 'A-IIIA', '2026-11-12', '2026-06-20', 'activo',        14),
('44987654', 'Cesar',        'Ramos Vilca',        '1990-12-08', '982109876', 'cramos@limabus.pe',             2, 'Q78901234', 'A-IIIC', '2027-08-05', '2026-09-30', 'activo',         5),
('45123698', 'Walter',       'Gálvez Mamani',      '1984-04-22', '981098765', 'wgalvez@limabus.pe',            2, 'Q89012345', 'A-IIIA', '2027-05-18', '2026-08-14', 'activo',        11),
('46456789', 'Arturo',       'Napa Marcos',        '1972-08-11', '980987654', 'anapa@limabus.pe',              2, 'Q90123456', 'A-IIIC', '2026-10-30', '2026-12-15', 'activo',        22),
('43852147', 'Ricardo',      'Suárez Ccopa',       '1987-01-25', '979876543', 'rsuarez@limabus.pe',            2, 'Q01234567', 'A-IIIB', '2027-11-08', '2027-01-22', 'activo',         9),
-- Transvial Lima — id 11-15
('44963852', 'Fernando',     'Huertas Ayala',      '1981-06-14', '978765432', 'fhuertas@transvial.pe',         3, 'Q11122233', 'A-IIIA', '2026-08-22', '2026-06-25', 'activo',        13),
('45741963', 'Víctor',       'Mellado Ramírez',    '1976-10-02', '977654321', 'vmellado@transvial.pe',         3, 'Q22233344', 'A-IIIA', '2027-02-14', '2026-10-18', 'activo',        18),
('46258147', 'Eduardo',      'Pérez Condori',      '1989-03-19', '976543210', 'eperez@transvial.pe',           3, 'Q33344455', 'A-IIIC', '2027-07-26', '2026-08-30', 'activo',         7),
('43159753', 'Hugo',         'Valencia Chávez',    '1978-12-05', '975432109', 'hvalencia@transvial.pe',        3, 'Q44455566', 'A-IIIA', '2026-06-20', '2026-05-02', 'licencia_medica',16),
('47852963', 'Junior',       'Córdova Fernández',  '1991-08-28', '974321098', 'jcordova@transvial.pe',         3, 'Q55566677', 'A-IIIC', '2028-04-03', '2027-03-15', 'activo',         4),
-- Perú Masivo — id 16-20
('44753159', 'Alberto',      'Paredes Yupanqui',   '1983-11-17', '973210987', 'aparedes@perumasivo.pe',        4, 'Q66677788', 'A-IIIA', '2027-01-29', '2026-06-28', 'activo',        11),
('45951357', 'Daniel',       'Rojas Limachi',      '1986-02-09', '972109876', 'drojas@perumasivo.pe',          4, 'Q77788899', 'A-IIIA', '2026-12-06', '2026-09-05', 'activo',        10),
('46357159', 'Raúl',         'Cárdenas Pérez',     '1980-07-21', '971098765', 'rcardenas@perumasivo.pe',       4, 'Q88899900', 'A-IIIC', '2027-06-14', '2026-07-20', 'activo',        15),
('43951753', 'Enrique',      'Lozano Machaca',     '1974-05-06', '970987654', 'elozano@perumasivo.pe',         4, 'Q99900011', 'A-IIIA', '2026-09-17', '2026-11-25', 'activo',        21),
('47159951', 'Jorge Luis',   'Tello Quiñones',     '1988-10-31', '969876543', 'jtello@perumasivo.pe',          4, 'Q00011122', 'A-IIIC', '2027-12-22', '2027-04-30', 'inactivo',       7);

-- Chofer 21 — Op. Sur, de vacaciones (completa variedad de estados)
INSERT INTO choferes (dni, nombres, apellidos, fecha_nacimiento, telefono, email, area_id, numero_licencia, tipo_licencia, fec_vence_licencia, fec_vence_certif_prot, estado, anios_experiencia) VALUES
('43652871', 'Carmen', 'Villalobos Huanca', '1986-06-03', '968765432', 'cvillalobos@limabus.pe', 2, 'Q11233211', 'A-IIIA', '2027-03-22', '2026-12-10', 'vacaciones', 9);

-- Accesos al portal del chofer
-- Choferes 1 y 2: contraseña = su propio DNI (sin cambio obligatorio)
-- Choferes 3,5,7,11,16: contraseña temporal = 44156789 (debe_cambiar_password=TRUE → cambian en primer ingreso)
INSERT INTO accesos_chofer (chofer_id, email, password_hash, creado_por, debe_cambiar_password) VALUES
(1,  'jhuaman@metrohub.gob.pe',    '$2b$12$FiMPYw5PdTaBXx45bQxqa.PdSiADlHV5KWLbXO1hjWZh4VM5sxjZG', 2, FALSE),
(2,  'rcastillo@metrohub.gob.pe',  '$2b$12$sOMcxG.6ZHg.QcUoiTu3u.rI/UuV5K//AH4l.VIszVi.XUCZXxO0q', 2, FALSE),
(3,  'pquispe@metrohub.gob.pe',    '$2b$12$FiMPYw5PdTaBXx45bQxqa.PdSiADlHV5KWLbXO1hjWZh4VM5sxjZG', 2, TRUE),
(5,  'csoldevilla@metrohub.gob.pe','$2b$12$FiMPYw5PdTaBXx45bQxqa.PdSiADlHV5KWLbXO1hjWZh4VM5sxjZG', 2, TRUE),
(6,  'mtorres@metrohub.gob.pe',    '$2b$12$tElheL0UCmjvFEaLFYqw2Ohud6J7LHNP.UD3TvZEjzQUs9MaiNSbq', 3, FALSE),
(7,  'cramos@metrohub.gob.pe',     '$2b$12$FiMPYw5PdTaBXx45bQxqa.PdSiADlHV5KWLbXO1hjWZh4VM5sxjZG', 3, TRUE),
(11, 'fhuertas@metrohub.gob.pe',   '$2b$12$FiMPYw5PdTaBXx45bQxqa.PdSiADlHV5KWLbXO1hjWZh4VM5sxjZG', 4, TRUE),
(16, 'aparedes@metrohub.gob.pe',   '$2b$12$FiMPYw5PdTaBXx45bQxqa.PdSiADlHV5KWLbXO1hjWZh4VM5sxjZG', 5, TRUE);

-- -----------------------------------------------------------------------------
-- 7. BUSES (16 unidades — estados variados)
-- -----------------------------------------------------------------------------
INSERT INTO buses (placa, area_id, tipo, anio, capacidad_pasajeros, estado) VALUES
('C1J-985', 1, 'articulado',  2018, 160, 'operativo'),
('C1J-986', 1, 'articulado',  2019, 160, 'operativo'),
('C1K-112', 1, 'articulado',  2020, 160, 'mantenimiento'),
('C2K-334', 1, 'convencional',2017,  80, 'operativo'),
('C1L-201', 2, 'articulado',  2018, 160, 'operativo'),
('C1L-202', 2, 'articulado',  2019, 160, 'operativo'),
('C1M-450', 2, 'articulado',  2021, 160, 'operativo'),
('C2M-778', 2, 'convencional',2016,  80, 'reparacion'),
('C3A-001', 3, 'articulado',  2017, 160, 'operativo'),
('C3A-002', 3, 'articulado',  2018, 160, 'operativo'),
('C3B-123', 3, 'articulado',  2020, 160, 'baja'),
('C4B-556', 3, 'convencional',2018,  80, 'operativo'),
('C5D-701', 4, 'articulado',  2019, 160, 'operativo'),
('C5D-702', 4, 'articulado',  2020, 160, 'operativo'),
('C5E-890', 4, 'articulado',  2021, 160, 'operativo'),
('C6E-109', 4, 'convencional',2017,  80, 'mantenimiento');

-- -----------------------------------------------------------------------------
-- 8. PROGRAMACIONES (semanas de prueba en junio 2026)
-- -----------------------------------------------------------------------------
INSERT INTO programaciones (nombre, fecha_inicio, fecha_fin, estado, creado_por, observaciones) VALUES
('Semana 24 — 09 al 15 Jun 2026', '2026-06-09', '2026-06-15', 'archivada', 1, 'Semana completada — archivada'),
('Semana 25 — 16 al 22 Jun 2026', '2026-06-16', '2026-06-22', 'archivada', 1, 'Semana completada — archivada');

-- -----------------------------------------------------------------------------
-- 9. HORARIOS — lunes 09-jun-2026 (programación id=1, semana vigente)
-- -----------------------------------------------------------------------------
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
-- Ruta A
(1,1,'2026-06-09','05:00','manana',35),(1,1,'2026-06-09','05:30','manana',35),
(1,1,'2026-06-09','06:00','manana',40),(1,1,'2026-06-09','06:30','manana',40),
(1,1,'2026-06-09','07:00','manana',45),(1,1,'2026-06-09','13:00','tarde', 40),
(1,1,'2026-06-09','13:30','tarde', 40),(1,1,'2026-06-09','14:00','tarde', 40),
(1,1,'2026-06-09','18:00','tarde', 45),(1,1,'2026-06-09','18:30','tarde', 45),
-- Ruta B
(1,2,'2026-06-09','05:00','manana',50),(1,2,'2026-06-09','05:30','manana',50),
(1,2,'2026-06-09','06:00','manana',55),(1,2,'2026-06-09','07:00','manana',55),
(1,2,'2026-06-09','13:00','tarde', 50),(1,2,'2026-06-09','14:00','tarde', 50),
(1,2,'2026-06-09','18:00','tarde', 55),(1,2,'2026-06-09','19:00','tarde', 55),
-- Ruta C
(1,3,'2026-06-09','05:00','manana',75),(1,3,'2026-06-09','05:30','manana',75),
(1,3,'2026-06-09','06:00','manana',80),(1,3,'2026-06-09','07:00','manana',80),
(1,3,'2026-06-09','13:00','tarde', 75),(1,3,'2026-06-09','14:00','tarde', 75),
(1,3,'2026-06-09','18:30','tarde', 80),
-- Expreso 1
(1,4,'2026-06-09','05:30','manana',68),(1,4,'2026-06-09','06:00','manana',68),
(1,4,'2026-06-09','06:30','manana',68),(1,4,'2026-06-09','13:00','tarde', 68),
(1,4,'2026-06-09','14:00','tarde', 68),(1,4,'2026-06-09','18:00','tarde', 68),
-- Expreso 2
(1,5,'2026-06-09','05:30','manana',55),(1,5,'2026-06-09','06:00','manana',55),
(1,5,'2026-06-09','13:30','tarde', 55),(1,5,'2026-06-09','18:30','tarde', 55),
-- Expreso 5
(1,6,'2026-06-09','05:30','manana',48),(1,6,'2026-06-09','06:30','manana',48),
(1,6,'2026-06-09','14:00','tarde', 48),(1,6,'2026-06-09','18:00','tarde', 48),
-- Ruta Nocturna
(1,10,'2026-06-09','23:30','noche',35),(1,10,'2026-06-10','00:30','noche',35),
(1,10,'2026-06-10','01:30','noche',35);

-- martes 10-jun-2026
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(1,1,'2026-06-10','05:00','manana',35),(1,1,'2026-06-10','06:00','manana',40),
(1,1,'2026-06-10','07:00','manana',45),(1,1,'2026-06-10','13:00','tarde', 40),
(1,1,'2026-06-10','18:00','tarde', 45),
(1,2,'2026-06-10','05:00','manana',50),(1,2,'2026-06-10','07:00','manana',55),
(1,2,'2026-06-10','14:00','tarde', 50),(1,2,'2026-06-10','18:30','tarde', 55),
(1,3,'2026-06-10','05:30','manana',75),(1,3,'2026-06-10','07:00','manana',80),
(1,3,'2026-06-10','14:00','tarde', 75),(1,3,'2026-06-10','19:00','tarde', 80),
(1,4,'2026-06-10','05:30','manana',68),(1,4,'2026-06-10','14:00','tarde', 68),
(1,4,'2026-06-10','18:00','tarde', 68);

-- -----------------------------------------------------------------------------
-- 10. ASIGNACIONES para lunes 09-jun
-- -----------------------------------------------------------------------------
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas) VALUES
(1,  1, 'C1J-985', 1, 'confirmada', 2, 'Turno mañana Ruta A 05:00'),
(2,  2, 'C1J-986', 1, 'confirmada', 2, 'Turno mañana Ruta A 05:30'),
(3,  3, 'C2K-334', 1, 'confirmada', 2, 'Turno mañana Ruta A 06:00'),
(4,  5, 'C1J-985', 1, 'propuesta',  2, 'Bus duplicado — detectar conflicto'),
(5,  3,  NULL,     1, 'cancelada',  2, 'Sin bus asignado — turno cancelado por falta de unidad operativa'),
(11, 6, 'C1L-201', 2, 'confirmada', 3, 'Turno mañana Ruta B 05:00'),
(12, 7, 'C1L-202', 2, 'confirmada', 3, 'Turno mañana Ruta B 05:30'),
(19,12, 'C3A-001', 3, 'confirmada', 4, 'Turno mañana Ruta C 05:00'),
(20,13, 'C3A-002', 3, 'confirmada', 4, 'Turno mañana Ruta C 05:30'),
(27,16, 'C5D-701', 4, 'confirmada',  5, 'Turno mañana Expreso 1 06:30'),
(28,17, 'C5D-702', 4, 'confirmada',  5, 'Turno mañana Expreso 1 13:00'),
(31,18, 'C5E-890', 4, 'confirmada',  5, 'Turno mañana Expreso 2 05:30');

-- Asignación reemplazada: Juan Huamán tenía el turno 06:00 Ruta A (horario 3) pero se permutó con Pedro Quispe
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas) VALUES
(3, 1, 'C1J-985', 1, 'reemplazada', 2, 'Turno 06:00 Ruta A reasignado a Pedro Quispe — permuta de turno aprobada 09-Jun');

-- -----------------------------------------------------------------------------
-- 11. DISPONIBILIDAD — variedad de motivos y choferes (junio 2026)
-- -----------------------------------------------------------------------------
INSERT INTO disponibilidad_chofer (chofer_id, fecha, hora_desde, hora_hasta, motivo, observaciones, registrado_por) VALUES
-- Walter Gálvez (id=8) — vacaciones toda la semana
(8,  '2026-06-09', '00:00', '23:59', 'vacaciones',    'Vacaciones aprobadas 09-13 Jun',                      3),
(8,  '2026-06-10', '00:00', '23:59', 'vacaciones',    'Vacaciones aprobadas 09-13 Jun',                      3),
(8,  '2026-06-11', '00:00', '23:59', 'vacaciones',    'Vacaciones aprobadas 09-13 Jun',                      3),
(8,  '2026-06-12', '00:00', '23:59', 'vacaciones',    'Vacaciones aprobadas 09-13 Jun',                      3),
(8,  '2026-06-13', '00:00', '23:59', 'vacaciones',    'Vacaciones aprobadas 09-13 Jun',                      3),
-- Hugo Valencia (id=14) — licencia médica
(14, '2026-06-09', '00:00', '23:59', 'medico',        'Post-operatorio rodilla, reposo 2 semanas',            4),
(14, '2026-06-10', '00:00', '23:59', 'medico',        'Post-operatorio rodilla, reposo 2 semanas',            4),
(14, '2026-06-11', '00:00', '23:59', 'medico',        'Post-operatorio rodilla, reposo 2 semanas',            4),
-- Roberto Castillo (id=2) — cita médica mañana
(2,  '2026-06-11', '07:00', '12:00', 'medico',        'Cita control cardiológico Hospital Rebagliati',        2),
-- Fernando Huertas (id=11) — capacitación ATU
(11, '2026-06-10', '08:00', '17:00', 'capacitacion',  'Taller manejo defensivo y emergencias — sede ATU',     1),
(11, '2026-06-11', '08:00', '17:00', 'capacitacion',  'Taller manejo defensivo y emergencias — sede ATU',     1),
-- Luis Alberto Gonzales (id=4) — suspendido, sin disponibilidad durante suspensión
(4,  '2026-06-09', '00:00', '23:59', 'personal',      'Suspensión por incidente documentado (ver exp. #142)', 1),
(4,  '2026-06-10', '00:00', '23:59', 'personal',      'Suspensión por incidente documentado (ver exp. #142)', 1),
-- Ricardo Suárez (id=10) — descanso compensatorio
(10, '2026-06-13', '00:00', '23:59', 'descanso',      'Descanso compensatorio por horas extra semana anterior',3),
-- Cinthia Soldevilla (id=5) — trámite personal tarde
(5,  '2026-06-12', '14:00', '18:00', 'personal',      'Renovación documentos SUTRAN',                        2),
-- Junior Córdova (id=15) — capacitación nueva flota
(15, '2026-06-14', '08:00', '13:00', 'capacitacion',  'Inducción buses articulados modelo 2024',              4),
-- Enrique Lozano (id=19) — descanso dominical
(19, '2026-06-14', '00:00', '23:59', 'descanso',      'Descanso dominical programado',                       5),
-- Jorge Tello (id=20) — inactivo, registrado por admin
(20, '2026-06-09', '00:00', '23:59', 'otro',          'Chofer inactivo — pendiente renovación contrato',      1),
-- Carmen Villalobos (id=21) — vacaciones semana 27 (semana vigente)
(21, '2026-06-29', '00:00', '23:59', 'vacaciones',    'Vacaciones anuales aprobadas 29-Jun al 05-Jul 2026',   3),
(21, '2026-06-30', '00:00', '23:59', 'vacaciones',    'Vacaciones anuales aprobadas 29-Jun al 05-Jul 2026',   3),
(21, '2026-07-01', '00:00', '23:59', 'vacaciones',    'Vacaciones anuales aprobadas 29-Jun al 05-Jul 2026',   3),
(21, '2026-07-02', '00:00', '23:59', 'vacaciones',    'Vacaciones anuales aprobadas 29-Jun al 05-Jul 2026',   3),
(21, '2026-07-03', '00:00', '23:59', 'vacaciones',    'Vacaciones anuales aprobadas 29-Jun al 05-Jul 2026',   3);

-- -----------------------------------------------------------------------------
-- 12. HORARIOS adicionales — Semana 24 (11-13 Jun, programacion_id=1)
-- -----------------------------------------------------------------------------

-- 11-Jun (Miércoles)
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(1,1,'2026-06-11','05:00','manana',35),(1,1,'2026-06-11','07:00','manana',45),
(1,1,'2026-06-11','13:00','tarde', 40),(1,1,'2026-06-11','18:30','tarde', 45),
(1,2,'2026-06-11','05:00','manana',50),(1,2,'2026-06-11','07:00','manana',55),
(1,2,'2026-06-11','14:00','tarde', 50),(1,2,'2026-06-11','18:30','tarde', 55),
(1,3,'2026-06-11','05:30','manana',75),(1,3,'2026-06-11','07:00','manana',80),
(1,3,'2026-06-11','14:00','tarde', 75),(1,3,'2026-06-11','19:00','tarde', 80),
(1,4,'2026-06-11','06:00','manana',68),(1,4,'2026-06-11','13:00','tarde', 68),
(1,4,'2026-06-11','18:00','tarde', 68),
(1,5,'2026-06-11','06:30','manana',55),(1,5,'2026-06-11','14:30','tarde', 55);

-- 12-Jun (Jueves)
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(1,1,'2026-06-12','05:00','manana',35),(1,1,'2026-06-12','07:00','manana',45),
(1,1,'2026-06-12','13:00','tarde', 40),(1,1,'2026-06-12','18:30','tarde', 45),
(1,2,'2026-06-12','05:00','manana',50),(1,2,'2026-06-12','07:00','manana',55),
(1,2,'2026-06-12','14:00','tarde', 50),(1,2,'2026-06-12','18:30','tarde', 55),
(1,3,'2026-06-12','05:30','manana',75),(1,3,'2026-06-12','07:00','manana',80),
(1,3,'2026-06-12','14:00','tarde', 75),(1,3,'2026-06-12','19:00','tarde', 80),
(1,4,'2026-06-12','06:00','manana',68),(1,4,'2026-06-12','13:00','tarde', 68),
(1,4,'2026-06-12','18:00','tarde', 68),
(1,5,'2026-06-12','06:30','manana',55),(1,5,'2026-06-12','14:30','tarde', 55);

-- 13-Jun (Viernes)
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(1,1,'2026-06-13','05:00','manana',35),(1,1,'2026-06-13','07:00','manana',45),
(1,1,'2026-06-13','13:00','tarde', 40),(1,1,'2026-06-13','18:30','tarde', 45),
(1,2,'2026-06-13','05:00','manana',50),(1,2,'2026-06-13','07:00','manana',55),
(1,2,'2026-06-13','14:00','tarde', 50),(1,2,'2026-06-13','18:30','tarde', 55),
(1,3,'2026-06-13','05:30','manana',75),(1,3,'2026-06-13','07:00','manana',80),
(1,3,'2026-06-13','14:00','tarde', 75),(1,3,'2026-06-13','19:00','tarde', 80),
(1,4,'2026-06-13','06:00','manana',68),(1,4,'2026-06-13','13:00','tarde', 68),
(1,4,'2026-06-13','18:00','tarde', 68),
(1,5,'2026-06-13','06:30','manana',55),(1,5,'2026-06-13','14:30','tarde', 55);

-- -----------------------------------------------------------------------------
-- 13. HORARIOS — Semana 25 (16-20 Jun, programacion_id=2)
-- -----------------------------------------------------------------------------

INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(2,1,'2026-06-16','05:00','manana',35),(2,1,'2026-06-16','07:00','manana',45),
(2,1,'2026-06-16','13:00','tarde', 40),(2,1,'2026-06-16','18:30','tarde', 45),
(2,2,'2026-06-16','05:00','manana',50),(2,2,'2026-06-16','07:00','manana',55),
(2,2,'2026-06-16','14:00','tarde', 50),(2,2,'2026-06-16','18:30','tarde', 55),
(2,3,'2026-06-16','05:30','manana',75),(2,3,'2026-06-16','07:00','manana',80),
(2,3,'2026-06-16','14:00','tarde', 75),(2,3,'2026-06-16','19:00','tarde', 80),
(2,4,'2026-06-16','06:00','manana',68),(2,4,'2026-06-16','13:00','tarde', 68),
(2,4,'2026-06-16','18:00','tarde', 68),
(2,5,'2026-06-16','06:30','manana',55),(2,5,'2026-06-16','14:30','tarde', 55),
(2,1,'2026-06-17','05:00','manana',35),(2,1,'2026-06-17','07:00','manana',45),
(2,1,'2026-06-17','13:00','tarde', 40),(2,1,'2026-06-17','18:30','tarde', 45),
(2,2,'2026-06-17','05:00','manana',50),(2,2,'2026-06-17','07:00','manana',55),
(2,2,'2026-06-17','14:00','tarde', 50),(2,2,'2026-06-17','18:30','tarde', 55),
(2,3,'2026-06-17','05:30','manana',75),(2,3,'2026-06-17','07:00','manana',80),
(2,3,'2026-06-17','14:00','tarde', 75),(2,3,'2026-06-17','19:00','tarde', 80),
(2,4,'2026-06-17','06:00','manana',68),(2,4,'2026-06-17','13:00','tarde', 68),
(2,4,'2026-06-17','18:00','tarde', 68),
(2,5,'2026-06-17','06:30','manana',55),(2,5,'2026-06-17','14:30','tarde', 55),
(2,1,'2026-06-18','05:00','manana',35),(2,1,'2026-06-18','07:00','manana',45),
(2,1,'2026-06-18','13:00','tarde', 40),(2,1,'2026-06-18','18:30','tarde', 45),
(2,2,'2026-06-18','05:00','manana',50),(2,2,'2026-06-18','07:00','manana',55),
(2,2,'2026-06-18','14:00','tarde', 50),(2,2,'2026-06-18','18:30','tarde', 55),
(2,3,'2026-06-18','05:30','manana',75),(2,3,'2026-06-18','07:00','manana',80),
(2,3,'2026-06-18','14:00','tarde', 75),(2,3,'2026-06-18','19:00','tarde', 80),
(2,4,'2026-06-18','06:00','manana',68),(2,4,'2026-06-18','13:00','tarde', 68),
(2,4,'2026-06-18','18:00','tarde', 68),
(2,5,'2026-06-18','06:30','manana',55),(2,5,'2026-06-18','14:30','tarde', 55),
(2,1,'2026-06-19','05:00','manana',35),(2,1,'2026-06-19','07:00','manana',45),
(2,1,'2026-06-19','13:00','tarde', 40),(2,1,'2026-06-19','18:30','tarde', 45),
(2,2,'2026-06-19','05:00','manana',50),(2,2,'2026-06-19','07:00','manana',55),
(2,2,'2026-06-19','14:00','tarde', 50),(2,2,'2026-06-19','18:30','tarde', 55),
(2,3,'2026-06-19','05:30','manana',75),(2,3,'2026-06-19','07:00','manana',80),
(2,3,'2026-06-19','14:00','tarde', 75),(2,3,'2026-06-19','19:00','tarde', 80),
(2,4,'2026-06-19','06:00','manana',68),(2,4,'2026-06-19','13:00','tarde', 68),
(2,4,'2026-06-19','18:00','tarde', 68),
(2,5,'2026-06-19','06:30','manana',55),(2,5,'2026-06-19','14:30','tarde', 55),
(2,1,'2026-06-20','05:00','manana',35),(2,1,'2026-06-20','07:00','manana',45),
(2,1,'2026-06-20','13:00','tarde', 40),(2,1,'2026-06-20','18:30','tarde', 45),
(2,2,'2026-06-20','05:00','manana',50),(2,2,'2026-06-20','07:00','manana',55),
(2,2,'2026-06-20','14:00','tarde', 50),(2,2,'2026-06-20','18:30','tarde', 55),
(2,3,'2026-06-20','05:30','manana',75),(2,3,'2026-06-20','07:00','manana',80),
(2,3,'2026-06-20','14:00','tarde', 75),(2,3,'2026-06-20','19:00','tarde', 80),
(2,4,'2026-06-20','06:00','manana',68),(2,4,'2026-06-20','13:00','tarde', 68),
(2,4,'2026-06-20','18:00','tarde', 68),
(2,5,'2026-06-20','06:30','manana',55),(2,5,'2026-06-20','14:30','tarde', 55);

-- -----------------------------------------------------------------------------
-- 14. ASIGNACIONES Semana 24 (11-13 Jun) — subquery para IDs seguros
-- -----------------------------------------------------------------------------

-- 11-Jun: Ruta 1 (chofer2 médico 07:00-12:00 → solo asignado a 13:00T)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-986',1,'confirmada',1,'Ruta A tarde (retorno de médico)'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='18:30:00';
-- 11-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='18:30:00';
-- 11-Jun: Ruta 3 (chofer11 en capacitación)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-11' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-11' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-11' AND h.hora_salida='14:00:00';
-- 11-Jun: Ruta 4
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-11' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-11' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-11' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=5 AND h.fecha='2026-06-11' AND h.hora_salida='06:30:00';

-- 12-Jun: Ruta 1 (chofer5 personal 14:00-18:00 → 13:00T OK termina 13:40)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde (antes de cita)'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='18:30:00';
-- 12-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='18:30:00';
-- 12-Jun: Ruta 3 (chofer11 disponible desde hoy)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='19:00:00';
-- 12-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-12' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-12' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-12' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=5 AND h.fecha='2026-06-12' AND h.hora_salida='06:30:00';

-- 13-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='18:30:00';
-- 13-Jun: Ruta 2 (chofer10 descanso, chofer8 vacaciones)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-13' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-13' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-13' AND h.hora_salida='14:00:00';
-- 13-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='19:00:00';
-- 13-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-13' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-13' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-13' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=5 AND h.fecha='2026-06-13' AND h.hora_salida='06:30:00';

-- -----------------------------------------------------------------------------
-- 15. ASIGNACIONES Semana 25 (16-20 Jun)
-- -----------------------------------------------------------------------------

-- 16-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='18:30:00';
-- 16-Jun: Ruta 2 (chofer8 regresa de vacaciones)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,8,'C1M-450',2,'confirmada',1,'Ruta B tarde (regreso de vacaciones)'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='18:30:00';
-- 16-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='19:00:00';
-- 16-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-16' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-16' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-16' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-16' AND h.hora_salida='06:30:00';

-- 17-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='18:30:00';
-- 17-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,8,'C1L-202',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='18:30:00';
-- 17-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C3A-002',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='19:00:00';
-- 17-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-17' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-17' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-17' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5E-890',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-17' AND h.hora_salida='06:30:00';

-- 18-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-986',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='18:30:00';
-- 18-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,8,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,9,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,10,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='18:30:00';
-- 18-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-002',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='19:00:00';
-- 18-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-18' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-18' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-18' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-18' AND h.hora_salida='06:30:00';

-- 19-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C2K-334',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-985',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='18:30:00';
-- 19-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,9,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='18:30:00';
-- 19-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C4B-556',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C3A-001',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='19:00:00';
-- 19-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-19' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-19' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-19' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-19' AND h.hora_salida='06:30:00';

-- 20-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,5,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='18:30:00';
-- 20-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,8,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,7,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,9,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='18:30:00';
-- 20-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='19:00:00';
-- 20-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-20' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-20' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-20' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id,19,'C5E-890',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-20' AND h.hora_salida='06:30:00';

-- -----------------------------------------------------------------------------
-- 16. CONFLICTOS (variados: vencimientos, solapamientos, buses)
-- -----------------------------------------------------------------------------
-- asignacion 4: bus C1J-985 usado simultáneamente con asignacion 1 (mismo día 09-Jun)
-- asignacion 5: sin bus asignado para turno 07:00 Ruta A
-- asignacion 6: certif. Protransporte de Miguel Torres vence 2026-06-20 (12 días)
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion) VALUES
(4, 'solapamiento_turno',  'alta',   'Bus C1J-985 asignado simultáneamente a turno 05:00 y 06:30 en Ruta A del 09-Jun-2026. Reasignar unidad.'),
(5, 'bus_no_operativo',    'media',  'Turno 07:00 Ruta A del 09-Jun sin bus asignado. Pendiente confirmar unidad operativa.'),
(6, 'certif_prot_vencida', 'media',  'Certif. Protransporte del chofer Miguel Ángel Torres vence el 20-Jun-2026 (12 días). Gestionar renovación.');

-- =============================================================================
-- 17. PROGRAMACIÓN SEMANA 27 — SEMANA VIGENTE (29-Jun al 05-Jul-2026)
-- Propósito: datos reales para hoy (01-Jul-2026) que activan las alertas IA
--   • Chofer 16 (Alberto Paredes) → 4 turnos noche consecutivos  → alerta noche
--   • Chofer  6 (Miguel Torres)   → turno doble 30-Jun (70 min entre rutas) → alerta descanso
-- =============================================================================

INSERT INTO programaciones (nombre, fecha_inicio, fecha_fin, estado, creado_por, observaciones) VALUES
('Semana 27 — 29 Jun al 05 Jul 2026', '2026-06-29', '2026-07-05', 'aprobada', 1,
 'Semana activa. Fiestas Patrias fin de semana — operación reforzada sábado 04-Jul');

-- ── Horarios 29-Jun (Lunes) ────────────────────────────────────────────────
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(3,1,'2026-06-29','05:00','manana',35),(3,1,'2026-06-29','07:00','manana',45),
(3,1,'2026-06-29','13:00','tarde', 40),(3,1,'2026-06-29','18:30','tarde', 45),
(3,2,'2026-06-29','05:00','manana',50),(3,2,'2026-06-29','07:00','manana',55),
(3,2,'2026-06-29','14:00','tarde', 50),(3,2,'2026-06-29','18:30','tarde', 55),
(3,3,'2026-06-29','05:30','manana',75),(3,3,'2026-06-29','07:00','manana',80),
(3,3,'2026-06-29','14:00','tarde', 75),(3,3,'2026-06-29','19:00','tarde', 80),
(3,4,'2026-06-29','06:00','manana',68),(3,4,'2026-06-29','13:00','tarde', 68),
(3,4,'2026-06-29','18:00','tarde', 68),
(3,10,'2026-06-29','23:30','noche',35);   -- noche 1/4 → chofer 16

-- ── Horarios 30-Jun (Martes) ───────────────────────────────────────────────
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(3,1,'2026-06-30','05:00','manana',35),(3,1,'2026-06-30','07:00','manana',45),
(3,1,'2026-06-30','13:00','tarde', 40),(3,1,'2026-06-30','18:30','tarde', 45),
(3,2,'2026-06-30','05:00','manana',50),(3,2,'2026-06-30','07:00','manana',55),  -- ← doble turno chofer 6
(3,2,'2026-06-30','14:00','tarde', 50),(3,2,'2026-06-30','18:30','tarde', 55),
(3,3,'2026-06-30','05:30','manana',75),(3,3,'2026-06-30','07:00','manana',80),
(3,3,'2026-06-30','14:00','tarde', 75),(3,3,'2026-06-30','19:00','tarde', 80),
(3,4,'2026-06-30','06:00','manana',68),(3,4,'2026-06-30','13:00','tarde', 68),
(3,4,'2026-06-30','18:00','tarde', 68),
(3,10,'2026-06-30','23:30','noche',35);   -- noche 2/4 → chofer 16

-- ── Horarios 01-Jul (Miércoles) ────────────────────────────────────────────
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(3,1,'2026-07-01','05:00','manana',35),(3,1,'2026-07-01','07:00','manana',45),
(3,1,'2026-07-01','13:00','tarde', 40),(3,1,'2026-07-01','18:30','tarde', 45),
(3,2,'2026-07-01','05:00','manana',50),(3,2,'2026-07-01','07:00','manana',55),
(3,2,'2026-07-01','14:00','tarde', 50),(3,2,'2026-07-01','18:30','tarde', 55),
(3,3,'2026-07-01','05:30','manana',75),(3,3,'2026-07-01','07:00','manana',80),
(3,3,'2026-07-01','14:00','tarde', 75),(3,3,'2026-07-01','19:00','tarde', 80),
(3,4,'2026-07-01','06:00','manana',68),(3,4,'2026-07-01','13:00','tarde', 68),
(3,4,'2026-07-01','18:00','tarde', 68),
(3,10,'2026-07-01','23:30','noche',35);   -- noche 3/4 → chofer 16

-- ── Horarios 02-Jul (Jueves) ───────────────────────────────────────────────
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(3,1,'2026-07-02','05:00','manana',35),(3,1,'2026-07-02','07:00','manana',45),
(3,1,'2026-07-02','13:00','tarde', 40),(3,1,'2026-07-02','18:30','tarde', 45),
(3,2,'2026-07-02','05:00','manana',50),(3,2,'2026-07-02','07:00','manana',55),
(3,2,'2026-07-02','14:00','tarde', 50),(3,2,'2026-07-02','18:30','tarde', 55),
(3,3,'2026-07-02','05:30','manana',75),(3,3,'2026-07-02','07:00','manana',80),
(3,3,'2026-07-02','14:00','tarde', 75),(3,3,'2026-07-02','19:00','tarde', 80),
(3,4,'2026-07-02','06:00','manana',68),(3,4,'2026-07-02','13:00','tarde', 68),
(3,4,'2026-07-02','18:00','tarde', 68),
(3,10,'2026-07-02','23:30','noche',35);   -- noche 4/4 → ALERTA fatiga chofer 16

-- ── Horarios 03-Jul (Viernes) ──────────────────────────────────────────────
INSERT INTO horarios_servicio (programacion_id, ruta_id, fecha, hora_salida, turno, duracion_est_min) VALUES
(3,1,'2026-07-03','05:00','manana',35),(3,1,'2026-07-03','07:00','manana',45),
(3,1,'2026-07-03','13:00','tarde', 40),(3,1,'2026-07-03','18:30','tarde', 45),
(3,2,'2026-07-03','05:00','manana',50),(3,2,'2026-07-03','07:00','manana',55),
(3,2,'2026-07-03','14:00','tarde', 50),(3,2,'2026-07-03','18:30','tarde', 55),
(3,3,'2026-07-03','05:30','manana',75),(3,3,'2026-07-03','07:00','manana',80),
(3,3,'2026-07-03','14:00','tarde', 75),
(3,4,'2026-07-03','06:00','manana',68),(3,4,'2026-07-03','13:00','tarde', 68),
(3,4,'2026-07-03','18:00','tarde', 68);

-- ── Asignaciones 29-Jun (Lunes) ────────────────────────────────────────────
-- Ruta A (área 1)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,1,'C1J-985',1,'confirmada',2,'Ruta A mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-29' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,3,'C2K-334',1,'confirmada',2,'Ruta A mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-29' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,2,'C1J-986',1,'confirmada',2,'Ruta A tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-29' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,5,'C1J-985',1,'confirmada',2,'Ruta A tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-29' AND h.hora_salida='18:30:00';
-- Ruta B (área 2)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,6,'C1L-201',2,'confirmada',3,'Ruta B mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-29' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,7,'C1L-202',2,'confirmada',3,'Ruta B mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-29' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,8,'C1M-450',2,'confirmada',3,'Ruta B tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-29' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,9,'C1L-201',2,'confirmada',3,'Ruta B tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-29' AND h.hora_salida='18:30:00';
-- Ruta C (área 3)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,11,'C3A-001',3,'confirmada',4,'Ruta C mañana 05:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-29' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,12,'C3A-002',3,'confirmada',4,'Ruta C mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-29' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,13,'C4B-556',3,'confirmada',4,'Ruta C tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-29' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,15,'C3A-001',3,'confirmada',4,'Ruta C tarde 19:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-29' AND h.hora_salida='19:00:00';
-- Expreso 1 (área 4)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,17,'C5D-701',4,'confirmada',5,'Expreso 1 mañana 06:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-06-29' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,18,'C5D-702',4,'confirmada',5,'Expreso 1 tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-06-29' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,19,'C5E-890',4,'confirmada',5,'Expreso 1 tarde 18:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-06-29' AND h.hora_salida='18:00:00';
-- Ruta Nocturna 29-Jun → chofer 16 (turno noche 1/4)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,16,'C5D-701',4,'confirmada',5,'Ruta Nocturna — turno noche 1/4' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=10 AND h.fecha='2026-06-29' AND h.hora_salida='23:30:00';

-- ── Asignaciones 30-Jun (Martes) ───────────────────────────────────────────
-- Ruta A
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,2,'C1J-985',1,'confirmada',2,'Ruta A mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-30' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,1,'C2K-334',1,'confirmada',2,'Ruta A mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-30' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,3,'C1J-986',1,'confirmada',2,'Ruta A tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-30' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,5,'C1J-985',1,'confirmada',2,'Ruta A tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-06-30' AND h.hora_salida='18:30:00';
-- ⚠️ Ruta B: chofer 6 hace 05:00 (50 min, termina 05:50) y 07:00 → 70 min de descanso → ALERTA
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,6,'C1L-201',2,'confirmada',3,'Ruta B mañana 05:00 (turno doble)' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-30' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,6,'C1L-202',2,'confirmada',3,'Ruta B mañana 07:00 (descanso insuficiente 70 min)' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-30' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,7,'C1M-450',2,'confirmada',3,'Ruta B tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-30' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,9,'C1L-201',2,'confirmada',3,'Ruta B tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-06-30' AND h.hora_salida='18:30:00';
-- Ruta C
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,11,'C3A-001',3,'confirmada',4,'Ruta C mañana 05:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-30' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,15,'C3A-002',3,'confirmada',4,'Ruta C mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-30' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,12,'C4B-556',3,'confirmada',4,'Ruta C tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-30' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,13,'C3A-001',3,'confirmada',4,'Ruta C tarde 19:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-06-30' AND h.hora_salida='19:00:00';
-- Expreso 1
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,17,'C5D-701',4,'confirmada',5,'Expreso 1 mañana 06:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-06-30' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,18,'C5D-702',4,'confirmada',5,'Expreso 1 tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-06-30' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,19,'C5E-890',4,'confirmada',5,'Expreso 1 tarde 18:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-06-30' AND h.hora_salida='18:00:00';
-- Ruta Nocturna 30-Jun → chofer 16 (turno noche 2/4)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,16,'C5D-701',4,'confirmada',5,'Ruta Nocturna — turno noche 2/4' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=10 AND h.fecha='2026-06-30' AND h.hora_salida='23:30:00';

-- ── Asignaciones 01-Jul (Miércoles) ────────────────────────────────────────
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,3,'C1J-985',1,'confirmada',2,'Ruta A mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-01' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,2,'C2K-334',1,'confirmada',2,'Ruta A mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-01' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,1,'C1J-986',1,'confirmada',2,'Ruta A tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-01' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,5,'C1J-985',1,'confirmada',2,'Ruta A tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-01' AND h.hora_salida='18:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,8,'C1L-201',2,'confirmada',3,'Ruta B mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-01' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,9,'C1L-202',2,'confirmada',3,'Ruta B mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-01' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,7,'C1M-450',2,'confirmada',3,'Ruta B tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-01' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,6,'C1L-201',2,'confirmada',3,'Ruta B tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-01' AND h.hora_salida='18:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,12,'C3A-001',3,'confirmada',4,'Ruta C mañana 05:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-01' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,13,'C3A-002',3,'confirmada',4,'Ruta C mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-01' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,15,'C4B-556',3,'confirmada',4,'Ruta C tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-01' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,11,'C3A-001',3,'confirmada',4,'Ruta C tarde 19:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-01' AND h.hora_salida='19:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,18,'C5D-701',4,'confirmada',5,'Expreso 1 mañana 06:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-01' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,17,'C5D-702',4,'confirmada',5,'Expreso 1 tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-01' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,19,'C5E-890',4,'confirmada',5,'Expreso 1 tarde 18:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-01' AND h.hora_salida='18:00:00';
-- Ruta Nocturna 01-Jul → chofer 16 (turno noche 3/4)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,16,'C5D-701',4,'confirmada',5,'Ruta Nocturna — turno noche 3/4' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=10 AND h.fecha='2026-07-01' AND h.hora_salida='23:30:00';

-- ── Asignaciones 02-Jul (Jueves) ───────────────────────────────────────────
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,1,'C1J-985',1,'confirmada',2,'Ruta A mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-02' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,3,'C2K-334',1,'confirmada',2,'Ruta A mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-02' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,2,'C1J-986',1,'confirmada',2,'Ruta A tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-02' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,5,'C1J-985',1,'confirmada',2,'Ruta A tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-02' AND h.hora_salida='18:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,9,'C1L-201',2,'confirmada',3,'Ruta B mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-02' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,6,'C1L-202',2,'confirmada',3,'Ruta B mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-02' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,8,'C1M-450',2,'confirmada',3,'Ruta B tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-02' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,7,'C1L-201',2,'confirmada',3,'Ruta B tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-02' AND h.hora_salida='18:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,13,'C3A-001',3,'confirmada',4,'Ruta C mañana 05:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-02' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,15,'C3A-002',3,'confirmada',4,'Ruta C mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-02' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,11,'C4B-556',3,'confirmada',4,'Ruta C tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-02' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,12,'C3A-001',3,'confirmada',4,'Ruta C tarde 19:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-02' AND h.hora_salida='19:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,19,'C5D-701',4,'confirmada',5,'Expreso 1 mañana 06:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-02' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,18,'C5D-702',4,'confirmada',5,'Expreso 1 tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-02' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,17,'C5E-890',4,'confirmada',5,'Expreso 1 tarde 18:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-02' AND h.hora_salida='18:00:00';
-- ⚠️ Ruta Nocturna 02-Jul → chofer 16 (turno noche 4/4 — ALERTA fatiga acumulada)
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,16,'C5D-701',4,'confirmada',5,'Ruta Nocturna — turno noche 4/4 (riesgo fatiga)' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=10 AND h.fecha='2026-07-02' AND h.hora_salida='23:30:00';

-- ── Asignaciones 03-Jul (Viernes) ──────────────────────────────────────────
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,2,'C1J-985',1,'confirmada',2,'Ruta A mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-03' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,1,'C2K-334',1,'confirmada',2,'Ruta A mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-03' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,3,'C1J-986',1,'confirmada',2,'Ruta A tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-03' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,5,'C1J-985',1,'confirmada',2,'Ruta A tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=1 AND h.fecha='2026-07-03' AND h.hora_salida='18:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,6,'C1L-201',2,'confirmada',3,'Ruta B mañana 05:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-03' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,8,'C1L-202',2,'confirmada',3,'Ruta B mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-03' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,10,'C1M-450',2,'confirmada',3,'Ruta B tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-03' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,7,'C1L-201',2,'confirmada',3,'Ruta B tarde 18:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=2 AND h.fecha='2026-07-03' AND h.hora_salida='18:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,15,'C3A-001',3,'confirmada',4,'Ruta C mañana 05:30' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-03' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,11,'C3A-002',3,'confirmada',4,'Ruta C mañana 07:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-03' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,13,'C4B-556',3,'confirmada',4,'Ruta C tarde 14:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=3 AND h.fecha='2026-07-03' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,17,'C5D-701',4,'confirmada',5,'Expreso 1 mañana 06:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-03' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,19,'C5D-702',4,'confirmada',5,'Expreso 1 tarde 13:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-03' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id,chofer_id,bus_placa,area_id,estado,asignado_por,notas)
SELECT h.id,18,'C5E-890',4,'confirmada',5,'Expreso 1 tarde 18:00' FROM horarios_servicio h
WHERE h.programacion_id=3 AND h.ruta_id=4 AND h.fecha='2026-07-03' AND h.hora_salida='18:00:00';

-- ── Conflictos detectados semana 27 ────────────────────────────────────────
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion) VALUES
(
  (SELECT a.id FROM asignaciones a
   JOIN horarios_servicio h ON a.horario_id = h.id
   WHERE a.chofer_id = 6 AND h.programacion_id = 3
     AND h.fecha = '2026-06-30' AND h.hora_salida = '07:00:00' LIMIT 1),
  'descanso_insuficiente', 'alta',
  'Miguel Ángel Torres asignado a dos rutas el 30-Jun-2026 con solo 70 min de descanso entre turnos (05:00-05:50 → 07:00). Mínimo requerido: 8 horas.'
),
(
  (SELECT a.id FROM asignaciones a
   JOIN horarios_servicio h ON a.horario_id = h.id
   WHERE a.chofer_id = 16 AND h.programacion_id = 3
     AND h.fecha = '2026-07-02' AND h.hora_salida = '23:30:00' LIMIT 1),
  'otro', 'alta',
  'Alberto Paredes Yupanqui acumula 4 turnos noche consecutivos (29-Jun al 02-Jul). Riesgo de fatiga severa — se recomienda descanso nocturno obligatorio el 03-Jul.'
);

-- =============================================================================
-- 18. ASIGNACIONES CANCELADAS — choferes no disponibles (referencia para conflictos)
-- =============================================================================
-- Hugo Valencia (id=14, licencia_medica, area 3) — cancelada por baja médica
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id, 14, NULL, 3, 'cancelada', 4, 'Cancelada — chofer en licencia médica postoperatoria'
FROM horarios_servicio h
WHERE h.programacion_id = 1 AND h.ruta_id = 3
  AND h.fecha = '2026-06-11' AND h.hora_salida = '19:00:00' LIMIT 1;

-- Luis Gonzales (id=4, suspendido, area 1) — cancelada por suspensión
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id, 4, NULL, 1, 'cancelada', 1, 'Cancelada — chofer suspendido por incidente disciplinario (exp. #142)'
FROM horarios_servicio h
WHERE h.programacion_id = 1 AND h.ruta_id = 1
  AND h.fecha = '2026-06-11' AND h.hora_salida = '18:30:00' LIMIT 1;

-- Roberto Castillo (id=2) — tenía cita médica 07:00-12:00 el 11-Jun pero fue asignado por error (chofer_no_disponible)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id, 2, 'C1J-986', 1, 'cancelada', 2, 'Cancelada — chofer tenía cita médica 07:00-12:00 registrada (asignación por error)'
FROM horarios_servicio h
WHERE h.programacion_id = 1 AND h.ruta_id = 1
  AND h.fecha = '2026-06-11' AND h.hora_salida = '07:00:00' LIMIT 1;

-- Chofer 3 (Pedro Quispe, area 1) asignado erróneamente a Ruta C (area 3) el 12-Jun (area_incorrecta)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, area_id, estado, asignado_por, notas)
SELECT h.id, 3, 'C3A-001', 3, 'cancelada', 2, 'Cancelada — chofer de área Norte asignado por error a ruta de área Mantenimiento'
FROM horarios_servicio h
WHERE h.programacion_id = 1 AND h.ruta_id = 3
  AND h.fecha = '2026-06-12' AND h.hora_salida = '07:00:00' LIMIT 1;

-- =============================================================================
-- 19. CONFLICTOS ADICIONALES (completan variedad de tipos y severidades)
-- =============================================================================

-- certif_prot_vencida CRITICA: chofer 11 (Fernando Huertas) certif venció 25-Jun y sigue asignado
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion)
SELECT a.id, 'certif_prot_vencida', 'critica',
  'Fernando Huertas Ayala opera con certificado Protransporte VENCIDO desde 25-Jun-2026. Suspender asignaciones hasta renovación urgente.'
FROM asignaciones a
JOIN horarios_servicio h ON a.horario_id = h.id
WHERE a.chofer_id = 11 AND h.programacion_id = 3
  AND h.fecha = '2026-07-01' AND h.hora_salida = '05:30:00'
LIMIT 1;

-- licencia_vencida ALTA: chofer 14 (Hugo Valencia) licencia venció 20-Jun-2026
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion)
SELECT a.id, 'licencia_vencida', 'alta',
  'Hugo Valencia Chávez — licencia de conducir clase A-IIIA vencida el 20-Jun-2026. En licencia médica actualmente; gestionar renovación antes de reintegro.'
FROM asignaciones a WHERE a.chofer_id = 14 AND a.estado = 'cancelada' LIMIT 1;

-- baja BAJA: aviso temprano — certif de Roberto Castillo vence en 9 días
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion)
SELECT a.id, 'certif_prot_vencida', 'baja',
  'Roberto Castillo Vera — certificado Protransporte vence el 10-Jul-2026 (9 días). Iniciar trámite de renovación con anticipación.'
FROM asignaciones a
JOIN horarios_servicio h ON a.horario_id = h.id
WHERE a.chofer_id = 2 AND h.programacion_id = 3
  AND h.fecha = '2026-06-29' AND h.hora_salida = '13:00:00'
LIMIT 1;

-- chofer_no_disponible ALTA: Roberto Castillo asignado en horario de cita médica 11-Jun
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion)
SELECT a.id, 'chofer_no_disponible', 'alta',
  'Roberto Castillo Vera tenía cita médica registrada el 11-Jun-2026 de 07:00 a 12:00, pero fue asignado al turno 07:00 Ruta A. Asignación cancelada tras detección del conflicto.'
FROM asignaciones a
JOIN horarios_servicio h ON a.horario_id = h.id
WHERE a.chofer_id = 2 AND a.estado = 'cancelada'
  AND h.programacion_id = 1 AND h.fecha = '2026-06-11' AND h.hora_salida = '07:00:00' LIMIT 1;

-- area_incorrecta ALTA: chofer de área Norte asignado a Ruta C (área Mantenimiento) el 12-Jun
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion)
SELECT a.id, 'area_incorrecta', 'alta',
  'Pedro Quispe Mendoza (Área Norte) fue asignado erróneamente a Ruta C del 12-Jun-2026, que corresponde al Área de Mantenimiento de Flota. Asignación cancelada.'
FROM asignaciones a
JOIN horarios_servicio h ON a.horario_id = h.id
WHERE a.chofer_id = 3 AND a.estado = 'cancelada'
  AND h.programacion_id = 1 AND h.ruta_id = 3 AND h.fecha = '2026-06-12' LIMIT 1;

-- exceso_8h_dia MEDIA: chofer 17 (Daniel Rojas) cubrió turno extra en semana 25 superando 8h en un día
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion)
SELECT a.id, 'exceso_8h_dia', 'media',
  'Daniel Rojas Limachi superó el límite de 8 horas el 19-Jun-2026 al cubrir turno de emergencia adicional (Expreso 1 mañana + tarde + cobertura nocturna). Total: 9.8h en el día.'
FROM asignaciones a
JOIN horarios_servicio h ON a.horario_id = h.id
WHERE a.chofer_id = 17 AND h.programacion_id = 2
  AND h.fecha = '2026-06-19' AND h.hora_salida = '13:00:00' LIMIT 1;

-- otro MEDIA: chofer 4 (Luis Gonzales) con certif vencida y suspensión activa — pendiente resolución disciplinaria
INSERT INTO conflictos (asignacion_id, tipo, severidad, descripcion)
SELECT a.id, 'otro', 'media',
  'Luis Alberto Gonzales Pariona — suspensión disciplinaria activa (exp. #142) con certificado Protransporte también vencido (18-May-2026). Resolución pendiente antes de cualquier reintegro.'
FROM asignaciones a WHERE a.chofer_id = 4 AND a.estado = 'cancelada' LIMIT 1;

-- =============================================================================
-- 19. PROGRAMACIONES ADICIONALES (completan variedad de estados)
-- =============================================================================

-- Semana 26: en revisión (Jun 22-28, semana de Fiestas Patrias)
INSERT INTO programaciones (nombre, fecha_inicio, fecha_fin, estado, creado_por, observaciones) VALUES
('Semana 26 — 22 al 28 Jun 2026', '2026-06-22', '2026-06-28', 'revision', 2,
 'En revisión — operación reducida semana de Fiestas Patrias. Pendiente aprobación supervisor.');

-- Semana 28: borrador (Jul 6-12, próxima semana de planificación)
INSERT INTO programaciones (nombre, fecha_inicio, fecha_fin, estado, creado_por, observaciones) VALUES
('Semana 28 — 06 al 12 Jul 2026', '2026-07-06', '2026-07-12', 'borrador', 2,
 'En elaboración — pendiente completar turnos noche y expreso. Sin asignar aún.');

-- =============================================================================
-- VERIFICACIÓN
-- =============================================================================
SELECT 'Áreas operativas: ' || COUNT(*) FROM areas_operativas
UNION ALL SELECT 'Usuarios: '        || COUNT(*) FROM usuarios
UNION ALL SELECT 'Estaciones: '      || COUNT(*) FROM estaciones
UNION ALL SELECT 'Rutas: '           || COUNT(*) FROM rutas
UNION ALL SELECT 'Choferes: '        || COUNT(*) FROM choferes
UNION ALL SELECT 'Buses: '           || COUNT(*) FROM buses
UNION ALL SELECT 'Programaciones: '  || COUNT(*) FROM programaciones
UNION ALL SELECT 'Horarios: '        || COUNT(*) FROM horarios_servicio
UNION ALL SELECT 'Asignaciones: '    || COUNT(*) FROM asignaciones
UNION ALL SELECT 'Disponibilidades: '|| COUNT(*) FROM disponibilidad_chofer
UNION ALL SELECT 'Conflictos: '      || COUNT(*) FROM conflictos;
