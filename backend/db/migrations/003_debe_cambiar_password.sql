-- Migración: flag de cambio obligatorio de contraseña en primer ingreso
ALTER TABLE accesos_chofer
    ADD COLUMN IF NOT EXISTS debe_cambiar_password BOOLEAN NOT NULL DEFAULT FALSE;

-- Cuentas demo del seed conservan acceso directo (ya tienen contraseña propia)
UPDATE accesos_chofer SET debe_cambiar_password = FALSE;
