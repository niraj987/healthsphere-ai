export default function StatCard({ icon: Icon, label, value, hint, tone = "brand" }) {
  const toneClasses = {
    brand: "bg-brand-50 text-brand-700",
    accent: "bg-accent-50 text-accent-700",
    ink: "bg-ink-100 text-ink-700",
  };
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-ink-400">{label}</span>
        {Icon && (
          <span className={`flex h-8 w-8 items-center justify-center rounded-lg ${toneClasses[tone]}`}>
            <Icon size={16} />
          </span>
        )}
      </div>
      <p className="mt-3 font-display text-2xl font-bold text-ink-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-ink-500">{hint}</p>}
    </div>
  );
}
