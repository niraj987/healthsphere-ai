export default function RiskGauge({ label, percent = 0, size = 120 }) {
  const radius = (size - 14) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, percent ?? 0));
  const offset = circumference - (clamped / 100) * circumference;

  const color = clamped >= 60 ? "#d8420a" : clamped >= 30 ? "#d97706" : "#1f6f63";

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="#e8ecee" strokeWidth={10} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={10}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.8s ease" }}
        />
        <text
          x="50%"
          y="50%"
          transform={`rotate(90 ${size / 2} ${size / 2})`}
          textAnchor="middle"
          dominantBaseline="middle"
          className="font-display"
          fontSize={size * 0.2}
          fontWeight="700"
          fill="#1c2429"
        >
          {clamped}%
        </text>
      </svg>
      <span className="text-xs font-semibold uppercase tracking-wide text-ink-500">{label}</span>
    </div>
  );
}
