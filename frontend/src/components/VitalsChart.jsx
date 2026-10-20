import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { format } from "date-fns";

export default function VitalsChart({ vitals = [] }) {
  const data = vitals.map((v) => ({
    date: format(new Date(v.recorded_at), "MMM d"),
    "Systolic BP": v.systolic_bp,
    "Heart Rate": v.heart_rate,
    "SpO2 (%)": v.spo2,
    "Resp Rate": v.respiratory_rate,
    "Glucose": v.fasting_glucose,
  }));

  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-ink-400">
        No vitals recorded yet — add a reading or upload a lab report to start your health timeline.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e8ecee" />
        <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#5e7580" }} axisLine={{ stroke: "#e8ecee" }} />
        <YAxis tick={{ fontSize: 12, fill: "#5e7580" }} axisLine={{ stroke: "#e8ecee" }} />
        <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #e8ecee", fontSize: 12 }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line type="monotone" dataKey="Systolic BP" stroke="#f2590f" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line type="monotone" dataKey="Heart Rate" stroke="#e11d48" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line type="monotone" dataKey="SpO2 (%)" stroke="#0284c7" strokeWidth={2.5} dot={{ r: 3 }} connectNulls />
        <Line type="monotone" dataKey="Resp Rate" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line type="monotone" dataKey="Glucose" stroke="#2f8b7c" strokeWidth={2} dot={{ r: 3 }} connectNulls />
      </LineChart>
    </ResponsiveContainer>
  );
}
