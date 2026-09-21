import { useCallback, useEffect, useState } from "react";
import gsap from "gsap";
import {
  Activity, FileText, HeartPulse, LayoutDashboard, Loader2, Sparkles, Stethoscope, Upload,
} from "lucide-react";
import DashboardShell from "../../components/layout/DashboardShell";
import ChatWidget from "../../components/ChatWidget";
import RiskGauge from "../../components/RiskGauge";
import VitalsChart from "../../components/VitalsChart";
import SeverityBadge from "../../components/SeverityBadge";
import StatCard from "../../components/StatCard";
import {
  addVitals, getDailyDigest, getLatestAssessment, getMyProfile, listMyLabReports,
  listMyVitals, runAssessment, updateMyProfile, uploadLabReport,
} from "../../api/client";
import { useAuth } from "../../context/AuthContext";

const NAV_ITEMS = [
  { path: "/patient", label: "Overview", icon: LayoutDashboard },
];

export default function PatientDashboard() {
  const { user } = useAuth();

  const [profile, setProfile] = useState(null);
  const [vitals, setVitals] = useState([]);
  const [labReports, setLabReports] = useState([]);
  const [assessment, setAssessment] = useState(null);
  const [digest, setDigest] = useState(null);

  const [loading, setLoading] = useState(true);
  const [runningAssessment, setRunningAssessment] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [profileFormOpen, setProfileFormOpen] = useState(false);
  const [vitalsFormOpen, setVitalsFormOpen] = useState(false);
  const [profileForm, setProfileForm] = useState({});
  const [vitalsForm, setVitalsForm] = useState({});
  const [message, setMessage] = useState("");

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const p = await getMyProfile();
      setProfile(p);
      setProfileForm(p);

      const [v, reports] = await Promise.all([listMyVitals(), listMyLabReports()]);
      setVitals(v);
      setLabReports(reports);

      try {
        const latest = await getLatestAssessment(p.id);
        setAssessment(latest);
      } catch {
        setAssessment(null);
      }

      try {
        const d = await getDailyDigest(p.id);
        setDigest(d);
      } catch {
        setDigest(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  useEffect(() => {
    if (!loading) {
      gsap.fromTo(".dash-fade", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.06, ease: "power3.out" });
    }
  }, [loading]);

  const handleProfileSave = async (e) => {
    e.preventDefault();
    const updated = await updateMyProfile({
      age: Number(profileForm.age) || 0,
      gender: profileForm.gender || "",
      blood_group: profileForm.blood_group || "",
      height_cm: Number(profileForm.height_cm) || null,
      weight_kg: Number(profileForm.weight_kg) || null,
      primary_condition: profileForm.primary_condition || "",
    });
    setProfile(updated);
    setProfileFormOpen(false);
  };

  const handleVitalsSave = async (e) => {
    e.preventDefault();
    const numeric = Object.fromEntries(
      Object.entries(vitalsForm).map(([k, v]) => [k, v === "" ? null : Number(v)])
    );
    const record = await addVitals(numeric);
    setVitals((prev) => [...prev, record]);
    setVitalsForm({});
    setVitalsFormOpen(false);
    setMessage("Vitals logged. Run a new assessment to see updated risk.");
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadLabReport(file);
      const [reports, v] = await Promise.all([listMyLabReports(), listMyVitals()]);
      setLabReports(reports);
      setVitals(v);
      setMessage("Report uploaded — biomarkers extracted and added to your timeline.");
    } catch (err) {
      setMessage("Could not process that file. Try a clearer PDF/image, or add vitals manually.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleRunAssessment = async () => {
    if (!profile) return;
    setRunningAssessment(true);
    try {
      const result = await runAssessment(profile.id);
      setAssessment(result);
      setMessage("New risk assessment generated.");
    } catch (err) {
      setMessage(err?.response?.data?.detail || "Add at least one vitals reading before running an assessment.");
    } finally {
      setRunningAssessment(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-ink-500">
        <Loader2 className="mr-2 animate-spin" /> Loading your dashboard…
      </div>
    );
  }

  return (
    <DashboardShell
      title={`Hi, ${user?.full_name?.split(" ")[0] || "there"}`}
      subtitle="Your personal health overview"
      navItems={NAV_ITEMS}
    >
      {message && (
        <div className="dash-fade mb-6 rounded-xl bg-brand-50 px-4 py-3 text-sm text-brand-700">{message}</div>
      )}

      {digest && (
        <div className="dash-fade card mb-8 flex items-start gap-4 border-brand-100 bg-gradient-to-r from-brand-50 to-white p-6">
          <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white">
            <Sparkles size={18} />
          </span>
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-brand-600">Patient Care Agent · Daily digest</p>
            <p className="mt-1 text-sm text-ink-700">{digest.plain_summary}</p>
          </div>
        </div>
      )}

      <div className="dash-fade grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={HeartPulse} label="Overall Risk" value={assessment ? `${assessment.overall_risk_score}%` : "—"} hint={assessment ? <SeverityBadge value={assessment.overall_severity} /> : "Run an assessment"} />
        <StatCard icon={Activity} label="Vitals Logged" value={vitals.length} hint="Readings on file" tone="ink" />
        <StatCard icon={FileText} label="Lab Reports" value={labReports.length} hint="Uploaded documents" tone="ink" />
        <StatCard icon={Stethoscope} label="Primary Condition" value={profile?.primary_condition || "—"} hint="From your profile" tone="accent" />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="dash-fade card p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-lg font-semibold text-ink-900">Health timeline</h2>
            <button onClick={() => setVitalsFormOpen((o) => !o)} className="btn-secondary !px-3 !py-1.5 text-xs">
              + Log vitals
            </button>
          </div>

          {vitalsFormOpen && (
            <form onSubmit={handleVitalsSave} className="mt-4 grid grid-cols-2 gap-3 rounded-xl bg-ink-50 p-4 sm:grid-cols-3">
              {[
                ["systolic_bp", "Systolic BP"], ["diastolic_bp", "Diastolic BP"], ["heart_rate", "Heart Rate"],
                ["fasting_glucose", "Fasting Glucose"], ["cholesterol", "Cholesterol"],
                ["serum_creatinine", "Serum Creatinine"], ["bmi", "BMI"],
              ].map(([key, label]) => (
                <div key={key}>
                  <label className="label">{label}</label>
                  <input
                    type="number"
                    step="0.1"
                    className="input"
                    value={vitalsForm[key] ?? ""}
                    onChange={(e) => setVitalsForm({ ...vitalsForm, [key]: e.target.value })}
                  />
                </div>
              ))}
              <div className="col-span-2 flex items-end gap-2 sm:col-span-3">
                <button type="submit" className="btn-primary !px-4 !py-2 text-xs">Save vitals</button>
                <button type="button" onClick={() => setVitalsFormOpen(false)} className="btn-secondary !px-4 !py-2 text-xs">Cancel</button>
              </div>
            </form>
          )}

          <div className="mt-4">
            <VitalsChart vitals={vitals} />
          </div>
        </div>

        <div className="dash-fade card p-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-lg font-semibold text-ink-900">Risk assessment</h2>
            <button onClick={handleRunAssessment} disabled={runningAssessment} className="btn-primary !px-3 !py-1.5 text-xs">
              {runningAssessment ? "Running…" : "Run assessment"}
            </button>
          </div>

          {assessment ? (
            <>
              <div className="mt-5 grid grid-cols-3 gap-2">
                <RiskGauge label="Heart" percent={assessment.heart_risk_pct} size={92} />
                <RiskGauge label="Diabetes" percent={assessment.diabetes_risk_pct} size={92} />
                <RiskGauge label="CKD" percent={assessment.ckd_risk_pct} size={92} />
              </div>
              <div className="mt-5">
                <p className="text-xs font-semibold uppercase tracking-wide text-ink-500">Why this score?</p>
                <ul className="mt-2 space-y-1.5">
                  {assessment.shap_explanation?.top_factors?.slice(0, 4).map((f) => (
                    <li key={f.factor} className="flex items-center justify-between text-sm text-ink-600">
                      <span>{f.factor}</span>
                      <span className="font-semibold text-ink-800">+{f.contribution}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <p className="mt-6 text-sm text-ink-500">
              No assessment yet. Log a vitals reading or upload a lab report, then run an assessment.
            </p>
          )}
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="dash-fade card p-6">
          <h2 className="font-display text-lg font-semibold text-ink-900">Upload lab report</h2>
          <p className="mt-1 text-sm text-ink-500">PDF or photo — biomarkers are extracted automatically.</p>
          <label className="mt-4 flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-ink-200 p-6 text-center text-sm text-ink-500 hover:border-brand-400 hover:text-brand-600">
            <Upload size={22} />
            {uploading ? "Processing…" : "Click to choose a file"}
            <input type="file" accept=".pdf,.png,.jpg,.jpeg" className="hidden" onChange={handleUpload} disabled={uploading} />
          </label>

          {labReports.length > 0 && (
            <ul className="mt-4 space-y-2">
              {labReports.slice(0, 4).map((r) => (
                <li key={r.id} className="flex items-center justify-between rounded-lg bg-ink-50 px-3 py-2 text-xs">
                  <span className="truncate text-ink-700">{r.filename}</span>
                  <span className="text-ink-400">{new Date(r.uploaded_at).toLocaleDateString()}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="dash-fade card p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-lg font-semibold text-ink-900">Your profile</h2>
            <button onClick={() => setProfileFormOpen((o) => !o)} className="btn-secondary !px-3 !py-1.5 text-xs">
              {profileFormOpen ? "Close" : "Edit"}
            </button>
          </div>

          {profileFormOpen ? (
            <form onSubmit={handleProfileSave} className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
              <div>
                <label className="label">Age</label>
                <input type="number" className="input" value={profileForm.age ?? ""} onChange={(e) => setProfileForm({ ...profileForm, age: e.target.value })} />
              </div>
              <div>
                <label className="label">Gender</label>
                <input className="input" value={profileForm.gender ?? ""} onChange={(e) => setProfileForm({ ...profileForm, gender: e.target.value })} />
              </div>
              <div>
                <label className="label">Blood group</label>
                <input className="input" value={profileForm.blood_group ?? ""} onChange={(e) => setProfileForm({ ...profileForm, blood_group: e.target.value })} />
              </div>
              <div>
                <label className="label">Height (cm)</label>
                <input type="number" className="input" value={profileForm.height_cm ?? ""} onChange={(e) => setProfileForm({ ...profileForm, height_cm: e.target.value })} />
              </div>
              <div>
                <label className="label">Weight (kg)</label>
                <input type="number" className="input" value={profileForm.weight_kg ?? ""} onChange={(e) => setProfileForm({ ...profileForm, weight_kg: e.target.value })} />
              </div>
              <div>
                <label className="label">Primary condition</label>
                <input className="input" value={profileForm.primary_condition ?? ""} onChange={(e) => setProfileForm({ ...profileForm, primary_condition: e.target.value })} />
              </div>
              <div className="col-span-2 sm:col-span-3">
                <button type="submit" className="btn-primary !px-4 !py-2 text-xs">Save profile</button>
              </div>
            </form>
          ) : (
            <dl className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3">
              {[
                ["Age", profile?.age], ["Gender", profile?.gender], ["Blood group", profile?.blood_group],
                ["Height", profile?.height_cm ? `${profile.height_cm} cm` : "—"],
                ["Weight", profile?.weight_kg ? `${profile.weight_kg} kg` : "—"],
                ["MRN", profile?.medical_record_number],
              ].map(([label, value]) => (
                <div key={label}>
                  <dt className="text-xs font-semibold uppercase tracking-wide text-ink-400">{label}</dt>
                  <dd className="mt-0.5 text-sm text-ink-800">{value || "—"}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      </div>

      <ChatWidget />
    </DashboardShell>
  );
}
