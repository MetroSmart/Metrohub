const TIPO_STYLE = {
  regular:  { bg: "#E6F1FB", color: "#0C447C" },
  expreso:  { bg: "#EAF3DE", color: "#27500A" },
  nocturna: { bg: "#F3E6FB", color: "#4A0C7C" },
};

export default function RouteBar({ code, name, tipo }) {
  const ts = TIPO_STYLE[tipo] ?? { bg: "#f0f0f0", color: "#444" };

  return (
    <div style={styles.row}>
      <span style={styles.code}>{code}</span>
      <span style={styles.name}>{name}</span>
      <span style={{ ...styles.tipoBadge, background: ts.bg, color: ts.color }}>
        {tipo ?? "—"}
      </span>
    </div>
  );
}

const styles = {
  row: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "8px 0",
    borderBottom: "0.5px solid #f0f0f0",
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 12,
  },
  code: {
    background: "#E6F1FB",
    color: "#0C447C",
    fontFamily: "'Space Mono', monospace",
    fontSize: 10,
    fontWeight: 700,
    padding: "3px 7px",
    borderRadius: 4,
    flexShrink: 0,
  },
  name: { flex: 1, color: "#333" },
  tipoBadge: {
    fontSize: 10,
    fontWeight: 500,
    padding: "2px 8px",
    borderRadius: 4,
    flexShrink: 0,
  },
};
