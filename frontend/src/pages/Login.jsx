import { useState } from "react";
import "../App.css";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("admin");
  const [attempts, setAttempts] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const BLOCKED = attempts >= 5;

  const handleSubmit = () => {
    if (BLOCKED) return;
    if (!email || !password) {
      setError("Completa todos los campos.");
      return;
    }
    setLoading(true);
    setError("");
    // Simula autenticación JWT (aquí irá el fetch al backend FastAPI)
    setTimeout(() => {
      setLoading(false);
      // Demo: cualquier credencial con dominio atu.gob.pe pasa
      if (email.endsWith("@atu.gob.pe") || email.endsWith("@metro.pe")) {
        onLogin({ email, role, name: email.split("@")[0] });
      } else {
        const next = attempts + 1;
        setAttempts(next);
        setError(
          next >= 5
            ? "Cuenta bloqueada tras 5 intentos fallidos."
            : `Credenciales incorrectas. Intento ${next}/5.`
        );
      }
    }, 800);
  };

  return (
    <div style={styles.wrapper}>
      {/* Panel izquierdo — marca */}
      <div style={styles.left}>
        <div style={styles.brandRow}>
          <div style={styles.logoBox}>
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
              <rect x="2" y="10" width="18" height="3" rx="1.5" fill="#E6F1FB" />
              <circle cx="5.5" cy="11.5" r="2.2" fill="#042C53" />
              <circle cx="11" cy="11.5" r="2.2" fill="#042C53" />
              <circle cx="16.5" cy="11.5" r="2.2" fill="#042C53" />
              <path d="M2 11.5 Q11 5.5 20 11.5" stroke="#85B7EB" strokeWidth="1.2" fill="none" />
            </svg>
          </div>
          <div>
            <div style={styles.brandName}>
              Metro<span style={{ color: "#378ADD" }}>Hub</span>
            </div>
            <div style={styles.tagline}>Metropolitano de Lima · ATU</div>
          </div>
        </div>

        <div style={styles.heroText}>
          <h1 style={styles.heroH1}>
            Programación <strong>inteligente</strong>
            <br />de horarios y choferes
          </h1>
          <p style={styles.heroP}>
            Plataforma interna de la Autoridad de Transporte Urbano para
            la gestión operativa del Metropolitano de Lima.
          </p>
        </div>

        <div style={styles.dots}>
          {[1,2,3,4,5].map(i => (
            <div key={i} style={{ ...styles.dot, background: i === 1 ? "#378ADD" : "#185FA5" }} />
          ))}
        </div>
      </div>

      {/* Panel derecho — formulario */}
      <div style={styles.right}>
        <h2 style={styles.formTitle}>Acceso al sistema</h2>
        <p style={styles.formSub}>Red interna ATU o VPN requerida</p>

        <Field label="Correo institucional">
          <input
            type="email"
            placeholder="usuario@atu.gob.pe"
            value={email}
            onChange={e => setEmail(e.target.value)}
            style={styles.input}
            disabled={BLOCKED}
          />
        </Field>

        <Field label="Contraseña">
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSubmit()}
            style={styles.input}
            disabled={BLOCKED}
          />
        </Field>

        <Field label="Rol">
          <div style={styles.roleRow}>
            {[["admin","Admin ATU"],["supervisor","Supervisor"]].map(([val, label]) => (
              <button
                key={val}
                onClick={() => setRole(val)}
                style={{
                  ...styles.roleBtn,
                  ...(role === val ? styles.roleBtnActive : {}),
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </Field>

        {error && (
          <div style={BLOCKED ? styles.boxDanger : styles.boxWarn}>
            {error}
          </div>
        )}

        {!error && (
          <div style={styles.boxWarn}>
            Acceso bloqueado tras 5 intentos fallidos
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={BLOCKED || loading}
          style={{ ...styles.submitBtn, opacity: BLOCKED || loading ? 0.6 : 1 }}
        >
          {loading ? "Verificando…" : "Ingresar a MetroHub"}
        </button>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
      <label style={{
        fontSize: 11, fontWeight: 500, color: "#666",
        textTransform: "uppercase", letterSpacing: "0.5px",
      }}>
        {label}
      </label>
      {children}
    </div>
  );
}

const styles = {
  wrapper: {
    display: "flex",
    minHeight: "100vh",
  },
  left: {
    flex: 1,
    background: "#042C53",
    padding: "48px 52px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
  },
  brandRow: { display: "flex", alignItems: "center", gap: 12 },
  logoBox: {
    width: 40, height: 40,
    background: "#185FA5",
    borderRadius: 10,
    display: "flex", alignItems: "center", justifyContent: "center",
  },
  brandName: {
    fontFamily: "'Space Mono', monospace",
    fontSize: 20, fontWeight: 700,
    color: "#E6F1FB", letterSpacing: "-0.5px",
  },
  tagline: { fontFamily: "'DM Sans',sans-serif", fontSize: 12, color: "#85B7EB", marginTop: 2 },
  heroText: {},
  heroH1: {
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 32, fontWeight: 300,
    color: "#E6F1FB", lineHeight: 1.3,
  },
  heroP: {
    fontFamily: "'DM Sans',sans-serif",
    fontSize: 14, color: "#85B7EB",
    marginTop: 12, lineHeight: 1.7, maxWidth: 380,
  },
  dots: { display: "flex", gap: 7 },
  dot: { width: 7, height: 7, borderRadius: "50%" },
  right: {
    width: 340,
    background: "#fff",
    padding: "48px 36px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    gap: 20,
  },
  formTitle: { fontFamily: "'DM Sans',sans-serif", fontSize: 20, fontWeight: 600, color: "#111" },
  formSub: { fontFamily: "'DM Sans',sans-serif", fontSize: 12, color: "#888", marginTop: -14 },
  input: {
    fontSize: 14, padding: "10px 13px",
    borderRadius: 8, border: "1px solid #ddd",
    background: "#f8f9fb", color: "#111", outline: "none", width: "100%",
  },
  roleRow: { display: "flex", gap: 8 },
  roleBtn: {
    flex: 1, padding: "9px 8px",
    borderRadius: 8, border: "1px solid #ddd",
    fontSize: 13, fontWeight: 400,
    background: "#f8f9fb", color: "#666", cursor: "pointer",
    transition: "all 0.12s",
  },
  roleBtnActive: {
    borderColor: "#185FA5",
    background: "#E6F1FB",
    color: "#0C447C",
    fontWeight: 500,
  },
  boxWarn: {
    background: "#FAEEDA", border: "1px solid #FAC775",
    borderRadius: 8, padding: "9px 13px",
    fontSize: 12, color: "#633806",
  },
  boxDanger: {
    background: "#FCEBEB", border: "1px solid #F7C1C1",
    borderRadius: 8, padding: "9px 13px",
    fontSize: 12, color: "#791F1F",
  },
  submitBtn: {
    background: "#185FA5", color: "#E6F1FB",
    border: "none", borderRadius: 8,
    padding: "12px", fontSize: 14, fontWeight: 500,
    cursor: "pointer", transition: "background 0.15s",
  },
};