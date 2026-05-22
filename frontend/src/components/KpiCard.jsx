export default function KpiCard({ label, value, sub, tone = "neutral" }) {
  const subColors = {
    good: "#3B6D11",
    warn: "#854F0B",
    danger: "#A32D2D",
    neutral: "#888",
  };

  return (
    <div style={styles.card}>
      <div style={styles.label}>{label}</div>
      <div style={styles.value}>{value}</div>
      {sub && (
        <div style={{ ...styles.sub, color: subColors[tone] }}>{sub}</div>
      )}
    </div>
  );
}

const styles = {
  card: {
    background: "#fff",
    border: "0.5px solid #e8e8e8",
    borderRadius: 8,
    padding: "14px 16px",
  },
  label: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 11,
    color: "#888",
    textTransform: "uppercase",
    letterSpacing: "0.4px",
    marginBottom: 6,
  },
  value: {
    fontFamily: "'Space Mono', monospace",
    fontSize: 26,
    fontWeight: 700,
    color: "#111",
  },
  sub: {
    fontFamily: "'DM Sans', sans-serif",
    fontSize: 11,
    marginTop: 3,
  },
};