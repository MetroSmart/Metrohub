export default function RouteBar({ code, name, pct }) {
  const color =
    pct >= 85 ? "#639922" :
    pct >= 70 ? "#EF9F27" :
    "#E24B4A";

  const textColor =
    pct >= 85 ? "#3B6D11" :
    pct >= 70 ? "#854F0B" :
    "#A32D2D";

  return (
    <div style={styles.row}>
      <span style={styles.code}>{code}</span>
      <span style={styles.name}>{name}</span>
      <div style={styles.barWrap}>
        <div style={{ ...styles.bar, width: `${pct}%`, background: color }} />
      </div>
      <span style={{ ...styles.pct, color: textColor }}>{pct}%</span>
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
  barWrap: {
    width: 64,
    height: 4,
    background: "#eee",
    borderRadius: 2,
    overflow: "hidden",
    flexShrink: 0,
  },
  bar: { height: "100%", borderRadius: 2, transition: "width 0.4s ease" },
  pct: {
    fontSize: 11,
    fontWeight: 500,
    width: 30,
    textAlign: "right",
    flexShrink: 0,
  },
};