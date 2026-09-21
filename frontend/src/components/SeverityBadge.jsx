const STYLES = {
  high: "bg-accent-100 text-accent-700",
  moderate: "bg-amber-100 text-amber-700",
  low: "bg-brand-100 text-brand-700",
  emergency: "bg-red-100 text-red-700",
  normal: "bg-ink-100 text-ink-600",
  pending: "bg-ink-100 text-ink-600",
  approved: "bg-brand-100 text-brand-700",
  rejected: "bg-accent-100 text-accent-700",
  open: "bg-amber-100 text-amber-700",
  resolved: "bg-brand-100 text-brand-700",
};

export default function SeverityBadge({ value }) {
  const key = (value || "").toLowerCase();
  const cls = STYLES[key] || "bg-ink-100 text-ink-600";
  return <span className={`badge ${cls}`}>{value || "Unknown"}</span>;
}
