-- =============================================================================
-- MetroHub v2.1 - Datos de Prueba
-- Datos representativos del Metropolitano de Lima (ATU)
-- Ejecutar DESPUÉS de 01_schema_metrohub.sql
-- Semana de referencia: junio 2026
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. CONCESIONARIOS (los 4 operadores reales del Metropolitano)
-- -----------------------------------------------------------------------------
INSERT INTO concesionarios (ruc, razon_social, nombre_corto, telefono, email_contacto) VALUES
('20513967720', 'Lima Vías Express S.A.',      'Lima Vías Express', '014567890', 'contacto@limaviasexpress.pe'),
('20524893451', 'Lima Bus Internacional S.A.', 'Lima Bus',          '014789012', 'operaciones@limabus.pe'),
('20545678901', 'Transvial Lima S.A.C.',        'Transvial',         '014234567', 'contacto@transvial.pe'),
('20556789234', 'Perú Masivo S.A.',             'Perú Masivo',       '014345678', 'info@perumasivo.pe');

-- -----------------------------------------------------------------------------
-- 2. USUARIOS (1 admin ATU + 4 supervisores)
-- Contraseña admin: admin2026 | supervisores: supervisor2026
-- -----------------------------------------------------------------------------
INSERT INTO usuarios (email, password_hash, nombre, apellidos, dni, rol, concesionario_id) VALUES
('admin.atu@metrohub.gob.pe',      '$2b$12$/AeChPKE1TQAUab7o1HKwO3lH9RfGcX3.3NMdRGzAPtjE4q5HF31m', 'María',   'Quispe Rivera',   '72839401', 'admin_atu',              NULL),
('sup.limavias@metrohub.gob.pe',   '$2b$12$OFC4W1UdQr.KnyEa6r27LuB7OULfwAjMOzoI7YezFBT6xWmmKsiou', 'Carlos',  'Ramírez Torres',  '45892013', 'supervisor_concesionario', 1),
('sup.limabus@metrohub.gob.pe',    '$2b$12$amWPw9JfxPrek9P0aomWsuG53GLsn1a591POfjsVBw8zAGARQcb7C', 'Lucía',   'Morales Salinas', '41203987', 'supervisor_concesionario', 2),
('sup.transvial@metrohub.gob.pe',  '$2b$12$5.SsXIRbctIEXjnWom4sN.b4dt.i4d7fb5nQx/oxX.oc8z7NbcL1q', 'Jorge',   'Vega Mendoza',    '43897201', 'supervisor_concesionario', 3),
('sup.perumasivo@metrohub.gob.pe', '$2b$12$Q3jY6rXAiH/0cwL53280q.WuQ9uCQGw4uvEpXvgrgoTHeaNE7txQ2', 'Ana',     'Ccahuana Pérez',  '47123890', 'supervisor_concesionario', 4);

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
INSERT INTO choferes (dni, nombres, apellidos, fecha_nacimiento, telefono, email, concesionario_id, numero_licencia, tipo_licencia, fec_vence_licencia, fec_vence_certif_prot, estado, anios_experiencia) VALUES
-- Lima Vías Express — id 1-5
('44156789', 'Juan Manuel',  'Huamán Flores',     '1985-03-12', '987654321', 'jhuaman@limaviasexpress.pe',    1, 'Q12345678', 'A-IIIA', '2027-06-30', '2026-12-15', 'activo',        12),
('45892314', 'Roberto',      'Castillo Vera',      '1979-11-23', '987123456', 'rcastillo@limaviasexpress.pe',  1, 'Q23456789', 'A-IIIA', '2026-12-15', '2026-07-10', 'activo',        15),
('46789012', 'Pedro',        'Quispe Mendoza',     '1988-07-04', '986543210', 'pquispe@limaviasexpress.pe',    1, 'Q34567890', 'A-IIIC', '2027-03-10', '2026-11-02', 'activo',         8),
('42345678', 'Luis Alberto', 'Gonzales Pariona',   '1975-02-18', '985432109', 'lgonzales@limaviasexpress.pe',  1, 'Q45678901', 'A-IIIA', '2026-09-25', '2026-05-18', 'suspendido',    20),
('47234567', 'Cinthia',      'Soldevilla Ríos',    '1986-09-15', '984321098', 'csoldevilla@limaviasexpress.pe',1, 'Q56789012', 'A-IIIC', '2028-01-20', '2027-02-10', 'activo',         6),
-- Lima Bus Internacional — id 6-10
('43678912', 'Miguel Ángel', 'Torres Huanca',      '1982-05-30', '983210987', 'mtorres@limabus.pe',            2, 'Q67890123', 'A-IIIA', '2026-11-12', '2026-06-20', 'activo',        14),
('44987654', 'Cesar',        'Ramos Vilca',        '1990-12-08', '982109876', 'cramos@limabus.pe',             2, 'Q78901234', 'A-IIIC', '2027-08-05', '2026-09-30', 'activo',         5),
('45123698', 'Walter',       'Gálvez Mamani',      '1984-04-22', '981098765', 'wgalvez@limabus.pe',            2, 'Q89012345', 'A-IIIA', '2027-05-18', '2026-08-14', 'vacaciones',    11),
('46456789', 'Arturo',       'Napa Marcos',        '1972-08-11', '980987654', 'anapa@limabus.pe',              2, 'Q90123456', 'A-IIIC', '2026-10-30', '2026-12-15', 'activo',        22),
('43852147', 'Ricardo',      'Suárez Ccopa',       '1987-01-25', '979876543', 'rsuarez@limabus.pe',            2, 'Q01234567', 'A-IIIA', '2027-11-08', '2027-01-22', 'activo',         9),
-- Transvial Lima — id 11-15
('44963852', 'Fernando',     'Huertas Ayala',      '1981-06-14', '978765432', 'fhuertas@transvial.pe',         3, 'Q11122233', 'A-IIIA', '2026-08-22', '2026-06-25', 'activo',        13),
('45741963', 'Víctor',       'Mellado Ramírez',    '1976-10-02', '977654321', 'vmellado@transvial.pe',         3, 'Q22233344', 'A-IIIA', '2027-02-14', '2026-10-18', 'activo',        18),
('46258147', 'Eduardo',      'Pérez Condori',      '1989-03-19', '976543210', 'eperez@transvial.pe',           3, 'Q33344455', 'A-IIIC', '2027-07-26', '2026-08-30', 'activo',         7),
('43159753', 'Hugo',         'Valencia Chávez',    '1978-12-05', '975432109', 'hvalencia@transvial.pe',        3, 'Q44455566', 'A-IIIA', '2026-07-11', '2026-05-02', 'licencia_medica',16),
('47852963', 'Junior',       'Córdova Fernández',  '1991-08-28', '974321098', 'jcordova@transvial.pe',         3, 'Q55566677', 'A-IIIC', '2028-04-03', '2027-03-15', 'activo',         4),
-- Perú Masivo — id 16-20
('44753159', 'Alberto',      'Paredes Yupanqui',   '1983-11-17', '973210987', 'aparedes@perumasivo.pe',        4, 'Q66677788', 'A-IIIA', '2027-01-29', '2026-06-28', 'activo',        11),
('45951357', 'Daniel',       'Rojas Limachi',      '1986-02-09', '972109876', 'drojas@perumasivo.pe',          4, 'Q77788899', 'A-IIIA', '2026-12-06', '2026-09-05', 'activo',        10),
('46357159', 'Raúl',         'Cárdenas Pérez',     '1980-07-21', '971098765', 'rcardenas@perumasivo.pe',       4, 'Q88899900', 'A-IIIC', '2027-06-14', '2026-07-20', 'activo',        15),
('43951753', 'Enrique',      'Lozano Machaca',     '1974-05-06', '970987654', 'elozano@perumasivo.pe',         4, 'Q99900011', 'A-IIIA', '2026-09-17', '2026-11-25', 'activo',        21),
('47159951', 'Jorge Luis',   'Tello Quiñones',     '1988-10-31', '969876543', 'jtello@perumasivo.pe',          4, 'Q00011122', 'A-IIIC', '2027-12-22', '2027-04-30', 'inactivo',       7);

-- Accesos al portal del chofer (tabla accesos_chofer — contraseña: chofer2026)
INSERT INTO accesos_chofer (chofer_id, email, password_hash, creado_por) VALUES
(1, 'jhuaman@metrohub.gob.pe',   '$2b$12$tGuyPseyX10WFRjikZJEk.CANmzW1TRtDZAQHGUm79ujaypT3KpW.', 2),
(2, 'rcastillo@metrohub.gob.pe', '$2b$12$tGuyPseyX10WFRjikZJEk.CANmzW1TRtDZAQHGUm79ujaypT3KpW.', 2),
(6, 'mtorres@metrohub.gob.pe',   '$2b$12$tGuyPseyX10WFRjikZJEk.CANmzW1TRtDZAQHGUm79ujaypT3KpW.', 3);

-- -----------------------------------------------------------------------------
-- 7. BUSES (16 unidades — estados variados)
-- -----------------------------------------------------------------------------
INSERT INTO buses (placa, concesionario_id, tipo, anio, capacidad_pasajeros, estado) VALUES
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
('Semana 24 — 09 al 15 Jun 2026', '2026-06-09', '2026-06-15', 'borrador', 1, 'Programación en preparación para esta semana'),
('Semana 25 — 16 al 22 Jun 2026', '2026-06-16', '2026-06-22', 'borrador', 1, 'Borrador anticipado semana siguiente');

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
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas) VALUES
(1,  1, 'C1J-985', 1, 'confirmada', 2, 'Turno mañana Ruta A 05:00'),
(2,  2, 'C1J-986', 1, 'confirmada', 2, 'Turno mañana Ruta A 05:30'),
(3,  3, 'C2K-334', 1, 'confirmada', 2, 'Turno mañana Ruta A 06:00'),
(4,  5, 'C1J-985', 1, 'propuesta',  2, 'Bus duplicado — detectar conflicto'),
(5,  3,  NULL,     1, 'propuesta',  2, 'Sin bus asignado — pendiente'),
(11, 6, 'C1L-201', 2, 'confirmada', 3, 'Turno mañana Ruta B 05:00'),
(12, 7, 'C1L-202', 2, 'confirmada', 3, 'Turno mañana Ruta B 05:30'),
(19, 9, 'C3A-001', 3, 'confirmada', 4, 'Turno mañana Ruta C 05:00'),
(20,10, 'C3A-002', 3, 'confirmada', 4, 'Turno mañana Ruta C 05:30'),
(27,16, 'C5D-701', 4, 'confirmada', 5, 'Turno mañana Expreso 1 06:30'),
(28,17, 'C5D-702', 4, 'confirmada', 5, 'Turno mañana Expreso 1 13:00'),
(31,18, 'C5E-890', 4, 'confirmada', 5, 'Turno mañana Expreso 2 05:30');

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
(20, '2026-06-09', '00:00', '23:59', 'otro',          'Chofer inactivo — pendiente renovación contrato',      1);

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
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-986',1,'confirmada',1,'Ruta A tarde (retorno de médico)'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-11' AND h.hora_salida='18:30:00';
-- 11-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-11' AND h.hora_salida='18:30:00';
-- 11-Jun: Ruta 3 (chofer11 en capacitación)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-11' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-11' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-11' AND h.hora_salida='14:00:00';
-- 11-Jun: Ruta 4
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-11' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-11' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-11' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=5 AND h.fecha='2026-06-11' AND h.hora_salida='06:30:00';

-- 12-Jun: Ruta 1 (chofer5 personal 14:00-18:00 → 13:00T OK termina 13:40)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde (antes de cita)'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-12' AND h.hora_salida='18:30:00';
-- 12-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-12' AND h.hora_salida='18:30:00';
-- 12-Jun: Ruta 3 (chofer11 disponible desde hoy)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-12' AND h.hora_salida='19:00:00';
-- 12-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-12' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-12' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-12' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=5 AND h.fecha='2026-06-12' AND h.hora_salida='06:30:00';

-- 13-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=1 AND h.fecha='2026-06-13' AND h.hora_salida='18:30:00';
-- 13-Jun: Ruta 2 (chofer10 descanso, chofer8 vacaciones)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-13' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-13' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=2 AND h.fecha='2026-06-13' AND h.hora_salida='14:00:00';
-- 13-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=3 AND h.fecha='2026-06-13' AND h.hora_salida='19:00:00';
-- 13-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-13' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-13' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=4 AND h.fecha='2026-06-13' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=1 AND h.ruta_id=5 AND h.fecha='2026-06-13' AND h.hora_salida='06:30:00';

-- -----------------------------------------------------------------------------
-- 15. ASIGNACIONES Semana 25 (16-20 Jun)
-- -----------------------------------------------------------------------------

-- 16-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-16' AND h.hora_salida='18:30:00';
-- 16-Jun: Ruta 2 (chofer8 regresa de vacaciones)
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,8,'C1M-450',2,'confirmada',1,'Ruta B tarde (regreso de vacaciones)'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-16' AND h.hora_salida='18:30:00';
-- 16-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-16' AND h.hora_salida='19:00:00';
-- 16-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-16' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-16' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-16' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-16' AND h.hora_salida='06:30:00';

-- 17-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-17' AND h.hora_salida='18:30:00';
-- 17-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-202',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,9,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,8,'C1L-202',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-17' AND h.hora_salida='18:30:00';
-- 17-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C3A-002',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-17' AND h.hora_salida='19:00:00';
-- 17-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-17' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-17' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-17' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,19,'C5E-890',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-17' AND h.hora_salida='06:30:00';

-- 18-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-986',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C1J-986',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-18' AND h.hora_salida='18:30:00';
-- 18-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,8,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,9,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,10,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-18' AND h.hora_salida='18:30:00';
-- 18-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-002',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-18' AND h.hora_salida='19:00:00';
-- 18-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-18' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-18' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-18' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-18' AND h.hora_salida='06:30:00';

-- 19-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C2K-334',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-985',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-19' AND h.hora_salida='18:30:00';
-- 19-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,9,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,10,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,7,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-19' AND h.hora_salida='18:30:00';
-- 19-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C4B-556',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C3A-001',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-19' AND h.hora_salida='19:00:00';
-- 19-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-19' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-19' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-19' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,19,'C5D-702',4,'confirmada',1,'Expreso 2 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=5 AND h.fecha='2026-06-19' AND h.hora_salida='06:30:00';

-- 20-Jun: Ruta 1
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,2,'C1J-985',1,'confirmada',1,'Ruta A mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,5,'C2K-334',1,'confirmada',1,'Ruta A mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,3,'C1J-986',1,'confirmada',1,'Ruta A tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,1,'C1J-985',1,'confirmada',1,'Ruta A tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=1 AND h.fecha='2026-06-20' AND h.hora_salida='18:30:00';
-- 20-Jun: Ruta 2
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,6,'C1L-201',2,'confirmada',1,'Ruta B mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='05:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,8,'C1L-202',2,'confirmada',1,'Ruta B mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,7,'C1M-450',2,'confirmada',1,'Ruta B tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,9,'C1L-201',2,'confirmada',1,'Ruta B tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=2 AND h.fecha='2026-06-20' AND h.hora_salida='18:30:00';
-- 20-Jun: Ruta 3
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,11,'C3A-001',3,'confirmada',1,'Ruta C mañana temprano'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='05:30:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,12,'C3A-002',3,'confirmada',1,'Ruta C mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='07:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,13,'C4B-556',3,'confirmada',1,'Ruta C tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='14:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,15,'C3A-001',3,'confirmada',1,'Ruta C noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=3 AND h.fecha='2026-06-20' AND h.hora_salida='19:00:00';
-- 20-Jun: Ruta 4 y 5
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,17,'C5D-701',4,'confirmada',1,'Expreso 1 mañana'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-20' AND h.hora_salida='06:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,16,'C5D-702',4,'confirmada',1,'Expreso 1 tarde'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-20' AND h.hora_salida='13:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
SELECT h.id,18,'C5E-890',4,'confirmada',1,'Expreso 1 tarde noche'
FROM horarios_servicio h WHERE h.programacion_id=2 AND h.ruta_id=4 AND h.fecha='2026-06-20' AND h.hora_salida='18:00:00';
INSERT INTO asignaciones (horario_id, chofer_id, bus_placa, concesionario_id, estado, asignado_por, notas)
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
-- VERIFICACIÓN
-- =============================================================================
SELECT 'Concesionarios: '   || COUNT(*) FROM concesionarios
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
