const DOT_COLORS = {
  danger: "#E24B4A",
  warn: "#EF9F27",
  info: "#378ADD",
};

export default function AlertPanel({ alerts }) {
  return (
    <div style={styles.panel}>
      <div style={styles.title}>Alertas activas</div>
      {alerts.length === 0 && (
        <p style={{ fontSize: 12, color: "#888", textAlign: "center", padding: "20px 0" }}>
          Sin alertas activas
        </p>
      )}
      {alerts.map((alert, i) => (
        <div key={i} style={{ ...styles.item, borderBottom: i < alerts.length - 1 ? "0.5px solid #f0f0f0" : "none" }}>
          <div style={{ ...styles.dot, background: DOT_COLORS[alert.type] ?? "#888" }} />
          <div>
            <div style={styles.text}>{alert.text}</div>
            <div style={styles.time}>{alert.time}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

const styles = {
  panel: {
    background: "#fff",
    border: "0.5px solid #e8e8e8",
    borderRadius: 8,
    padding: 14,
  },
  title: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 13,
    fontWeight: 500,
    color: "#111",
    marginBottom: 12,
  },
  item: {
    display: "flex",
    alignItems: "flex-start",
    gap: 9,
    padding: "8px 0",
  },
  dot: {
    width: 7, height: 7,
    borderRadius: "50%",
    flexShrink: 0,
    marginTop: 4,
  },
  text: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 12, color: "#222", lineHeight: 1.45,
  },
  time: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 11, color: "#999", marginTop: 2,
  },
};