import { useState } from "react";
import { api } from "../api";

export default function CambioPasswordPrimerIngreso({ user, onComplete, onLogout }) {
  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!actual || !nueva || !confirmar) {
      setError("Completa todos los campos.");
      return;
    }
    if (nueva.length < 8) {
      setError("La nueva contraseña debe tener al menos 8 caracteres.");
      return;
    }
    if (nueva !== confirmar) {
      setError("La confirmación no coincide con la nueva contraseña.");
      return;
    }
    setSaving(true);
    try {
      await api.post("/api/auth/cambiar-password-primer-ingreso", {
        password_actual: actual,
        password_nueva:  nueva,
      });
      onComplete();
    } catch (err) {
      setError(err.message || "No se pudo actualizar la contraseña.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <h2 style={styles.title}>Cambio de contraseña obligatorio</h2>
        <p style={styles.sub}>
          Hola, {user?.name}. Por seguridad debes cambiar tu contraseña inicial
          antes de continuar.
        </p>
        <div style={styles.hint}>
          Tu contraseña temporal es tu número de DNI.
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label style={styles.label}>Contraseña actual (DNI)</label>
          <input
            type="password"
            value={actual}
            onChange={e => setActual(e.target.value)}
            style={styles.input}
            autoComplete="current-password"
          />

          <label style={styles.label}>Nueva contraseña</label>
          <input
            type="password"
            value={nueva}
            onChange={e => setNueva(e.target.value)}
            style={styles.input}
            autoComplete="new-password"
          />

          <label style={styles.label}>Confirmar nueva contraseña</label>
          <input
            type="password"
            value={confirmar}
            onChange={e => setConfirmar(e.target.value)}
            style={styles.input}
            autoComplete="new-password"
          />

          {error && <div style={styles.error}>{error}</div>}

          <button type="submit" disabled={saving} style={styles.btnPrimary}>
            {saving ? "Guardando…" : "Actualizar contraseña"}
          </button>
          <button type="button" onClick={onLogout} style={styles.btnGhost}>
            Cerrar sesión
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: "fixed", inset: 0, zIndex: 1000,
    background: "rgba(4, 44, 83, 0.72)",
    display: "flex", alignItems: "center", justifyContent: "center",
    padding: 24,
  },
  modal: {
    width: "100%", maxWidth: 420,
    background: "#fff", borderRadius: 12,
    padding: "28px 24px",
    boxShadow: "0 12px 40px rgba(0,0,0,0.2)",
  },
  title: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 20, fontWeight: 600, color: "#111", marginBottom: 8,
  },
  sub: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 14, color: "#555", lineHeight: 1.5, marginBottom: 12,
  },
  hint: {
    background: "#E6F1FB", color: "#0C447C",
    borderRadius: 8, padding: "10px 12px",
    fontSize: 12, marginBottom: 18,
  },
  form: { display: "flex", flexDirection: "column", gap: 10 },
  label: {
    fontSize: 11, fontWeight: 500, color: "#666",
    textTransform: "uppercase", letterSpacing: "0.5px",
  },
  input: {
    fontSize: 14, padding: "10px 13px",
    borderRadius: 8, border: "1px solid #ddd",
    background: "#f8f9fb", color: "#111", outline: "none",
  },
  error: {
    background: "#FCEBEB", border: "1px solid #F7C1C1",
    color: "#791F1F", borderRadius: 8, padding: "9px 12px", fontSize: 12,
  },
  btnPrimary: {
    marginTop: 8,
    background: "#185FA5", color: "#E6F1FB",
    border: "none", borderRadius: 8, padding: "12px",
    fontSize: 14, fontWeight: 500, cursor: "pointer",
  },
  btnGhost: {
    background: "transparent", color: "#666",
    border: "none", padding: "8px", fontSize: 13, cursor: "pointer",
  },
};
