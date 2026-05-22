const NAV = [
  {
    section: "Principal",
    items: [
      { key: "dashboard", label: "Dashboard", icon: <IconGrid /> },
      { key: "rutas", label: "Rutas y Estaciones", icon: <IconRoutes /> },
      { key: "grilla", label: "Programación", icon: <IconCal /> },
      { key: "choferes", label: "Choferes", icon: <IconUser /> },
    ],
  },
  {
    section: "IA",
    items: [
      { key: "optimizador", label: "Optimizador", icon: <IconAI /> },
    ],
  },
  {
    section: "Reportes",
    items: [
      { key: "reportes", label: "Exportar PDF/XLSX", icon: <IconDoc /> },
    ],
  },
];

export default function Sidebar({ active, onNav, onLogout, user }) {
  return (
    <aside style={styles.sidebar}>
      <div style={styles.brand}>
        Metro<span style={{ color: "#378ADD" }}>Hub</span>
      </div>

      <div style={styles.userBadge}>
        <div style={styles.avatar}>{user?.name?.[0]?.toUpperCase() ?? "U"}</div>
        <div>
          <div style={styles.userName}>{user?.name ?? "Usuario"}</div>
          <div style={styles.userRole}>
            {user?.role === "admin" ? "Admin ATU" : "Supervisor"}
          </div>
        </div>
      </div>

      {NAV.map(({ section, items }) => (
        <div key={section} style={styles.section}>
          <div style={styles.sectionLabel}>{section}</div>
          {items.map(({ key, label, icon }) => (
            <button
              key={key}
              onClick={() => onNav(key)}
              style={{
                ...styles.navItem,
                ...(active === key ? styles.navActive : {}),
              }}
            >
              <span style={styles.navIcon}>{icon}</span>
              {label}
            </button>
          ))}
        </div>
      ))}

      <button onClick={onLogout} style={styles.logoutBtn}>
        <IconLogout /> Cerrar sesión
      </button>
    </aside>
  );
}

// ── Icons ──────────────────────────────────────────────────────────
function IconGrid() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="1" y="1" width="6" height="6" rx="1" fill="currentColor" opacity="0.9"/>
      <rect x="9" y="1" width="6" height="6" rx="1" fill="currentColor" opacity="0.5"/>
      <rect x="1" y="9" width="6" height="6" rx="1" fill="currentColor" opacity="0.5"/>
      <rect x="9" y="9" width="6" height="6" rx="1" fill="currentColor" opacity="0.5"/>
    </svg>
  );
}
function IconRoutes() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M2 4h12M2 8h8M2 12h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  );
}
function IconCal() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="2" y="2" width="12" height="12" rx="1.5" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M5 2v2M11 2v2M2 6h12" stroke="currentColor" strokeWidth="1.2"/>
    </svg>
  );
}
function IconUser() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M2 14c0-3 2.7-5 6-5s6 2 6 5" stroke="currentColor" strokeWidth="1.2"/>
    </svg>
  );
}
function IconAI() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M3 12L8 4L13 12" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M5 9h6" stroke="currentColor" strokeWidth="1.2"/>
    </svg>
  );
}
function IconDoc() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <rect x="3" y="1" width="10" height="14" rx="1.5" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M6 5h4M6 8h4M6 11h2" stroke="currentColor" strokeWidth="1.2"/>
    </svg>
  );
}
function IconLogout() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" style={{marginRight:6}}>
      <path d="M6 14H3a1 1 0 01-1-1V3a1 1 0 011-1h3" stroke="currentColor" strokeWidth="1.3"/>
      <path d="M11 11l3-3-3-3M14 8H6" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
    </svg>
  );
}

// ── Styles ─────────────────────────────────────────────────────────
const styles = {
  sidebar: {
    width: 220,
    minHeight: "100vh",
    background: "#042C53",
    padding: "24px 14px",
    display: "flex",
    flexDirection: "column",
    gap: 0,
    flexShrink: 0,
  },
  brand: {
    fontFamily: "'Space Mono', monospace",
    fontSize: 16, fontWeight: 700,
    color: "#E6F1FB",
    padding: "0 8px",
    marginBottom: 20,
    letterSpacing: "-0.3px",
  },
  userBadge: {
    display: "flex", alignItems: "center", gap: 10,
    background: "rgba(55,138,221,0.12)",
    borderRadius: 8, padding: "10px 10px",
    marginBottom: 24,
  },
  avatar: {
    width: 32, height: 32,
    borderRadius: "50%",
    background: "#185FA5",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: 13, fontWeight: 600, color: "#E6F1FB",
    flexShrink: 0,
  },
  userName: { fontSize: 13, fontWeight: 500, color: "#E6F1FB" },
  userRole: { fontSize: 11, color: "#85B7EB", marginTop: 1 },
  section: { marginBottom: 20 },
  sectionLabel: {
    fontSize: 10, fontWeight: 500,
    color: "#378ADD",
    textTransform: "uppercase", letterSpacing: "1px",
    padding: "0 8px", marginBottom: 6,
  },
  navItem: {
    display: "flex", alignItems: "center", gap: 9,
    width: "100%", padding: "9px 8px",
    borderRadius: 6, border: "none",
    background: "transparent",
    fontSize: 13, color: "#85B7EB",
    cursor: "pointer", textAlign: "left",
    transition: "all 0.12s",
    marginBottom: 2,
  },
  navActive: {
    background: "rgba(55,138,221,0.2)",
    color: "#E6F1FB",
    fontWeight: 500,
  },
  navIcon: { display: "flex", alignItems: "center", color: "inherit" },
  logoutBtn: {
    display: "flex", alignItems: "center",
    marginTop: "auto",
    padding: "9px 8px",
    background: "transparent",
    border: "none",
    borderRadius: 6,
    fontSize: 13, color: "#85B7EB",
    cursor: "pointer",
    width: "100%",
  },
};