import { Activity, Heart, Wind, Zap, AlertTriangle, CheckCircle2 } from "lucide-react";
import RiskGauge from "./RiskGauge";

export default function CardiopulmonaryCard({ assessment, latestVital }) {
  if (!assessment && !latestVital) {
    return null;
  }

  const heartRisk = assessment?.heart_risk_pct ?? 0;
  const lungRisk = assessment?.lung_risk_pct ?? 0;
  const lungSeverity = assessment?.lung_severity || "Normal Pulmonary Function";
  const cardiacEfficiency = assessment?.cardiac_efficiency_score || 85.0;

  const spo2 = latestVital?.spo2 ?? 98;
  const respRate = latestVital?.respiratory_rate ?? 16;
  const hrv = latestVital?.hrv ?? 45;
  const fev1 = latestVital?.fev1 ?? 3.2;
  const pefr = latestVital?.pefr ?? 450;
  const ecgRhythm = latestVital?.ecg_rhythm || "Normal Sinus Rhythm";

  const getSpo2Badge = (val) => {
    if (val < 90) return { label: "Severe Hypoxia", color: "bg-red-100 text-red-800 border-red-300" };
    if (val < 94) return { label: "Moderate Hypoxia", color: "bg-amber-100 text-amber-800 border-amber-300" };
    return { label: "Normal SpO2", color: "bg-emerald-100 text-emerald-800 border-emerald-300" };
  };

  const spo2Badge = getSpo2Badge(spo2);

  return (
    <div className="card p-6 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white shadow-xl border border-slate-700/60 rounded-2xl">
      <div className="flex items-center justify-between pb-4 border-b border-slate-700/80">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30">
            <Heart size={20} className="animate-pulse" />
          </span>
          <div>
            <h3 className="font-display text-base font-bold text-white flex items-center gap-2">
              Heart & Lung Health Monitoring
              <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
            </h3>
            <p className="text-xs text-slate-400">Cardiorespiratory Vitals & Pulmonary Risk AI Assessment</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold border ${spo2Badge.color}`}>
            <Wind size={12} /> {spo2Badge.label} ({spo2}%)
          </span>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Heart Section */}
        <div className="rounded-xl bg-slate-800/80 p-4 border border-slate-700">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-rose-300 flex items-center gap-2">
              <Heart size={16} /> Heart & Cardiac Monitoring
            </h4>
            <span className="text-xs text-slate-400">Efficiency: <strong className="text-emerald-400">{cardiacEfficiency}%</strong></span>
          </div>

          <div className="mt-4 flex items-center justify-around">
            <RiskGauge label="Heart Risk" percent={heartRisk} size={84} />
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Resting HR:</span>
                <span className="font-semibold text-slate-200">{latestVital?.heart_rate ?? "—"} bpm</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Blood Pressure:</span>
                <span className="font-semibold text-slate-200">
                  {latestVital?.systolic_bp ?? "—"}/{latestVital?.diastolic_bp ?? "—"} mmHg
                </span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">HRV (Autonomic):</span>
                <span className="font-semibold text-slate-200">{hrv} ms</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">ECG Rhythm:</span>
                <span className="font-semibold text-rose-300 truncate max-w-[120px]">{ecgRhythm}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Lung Section */}
        <div className="rounded-xl bg-slate-800/80 p-4 border border-slate-700">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-sky-300 flex items-center gap-2">
              <Wind size={16} /> Lung & Pulmonary Assessment
            </h4>
            <span className="text-xs text-sky-400 font-medium truncate max-w-[150px]">{lungSeverity}</span>
          </div>

          <div className="mt-4 flex items-center justify-around">
            <RiskGauge label="Lung Risk" percent={lungRisk} size={84} />
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Oxygen Saturation:</span>
                <span className="font-semibold text-sky-300">{spo2}% SpO₂</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Respiratory Rate:</span>
                <span className="font-semibold text-slate-200">{respRate} breaths/min</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Airway FEV₁:</span>
                <span className="font-semibold text-slate-200">{fev1} L</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span className="text-slate-400">Peak Flow (PEFR):</span>
                <span className="font-semibold text-slate-200">{pefr} L/min</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* SHAP Factors for Heart & Lung */}
      {assessment?.shap_explanation && (
        <div className="mt-4 pt-3 border-t border-slate-700/80 text-xs">
          <p className="font-semibold text-slate-300 flex items-center gap-1.5 mb-2">
            <Zap size={14} className="text-amber-400" /> Key Cardiorespiratory Risk Drivers:
          </p>
          <div className="flex flex-wrap gap-2">
            {(assessment.shap_explanation.heart_factors || [])
              .concat(assessment.shap_explanation.lung_factors || [])
              .slice(0, 4)
              .map((f, idx) => (
                <span key={idx} className="rounded-md bg-slate-800 px-2.5 py-1 text-slate-300 border border-slate-700 flex items-center gap-1">
                  <span>{f.factor}</span>
                  <strong className="text-rose-400">+{f.contribution}%</strong>
                </span>
              ))}
            {(!assessment.shap_explanation.heart_factors?.length && !assessment.shap_explanation.lung_factors?.length) && (
              <span className="text-slate-400">No high cardiorespiratory risk factors detected.</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
