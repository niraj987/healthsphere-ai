import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import gsap from "gsap";
import { AlertTriangle, ClipboardList, LayoutDashboard, Loader2, Users } from "lucide-react";
import DashboardShell from "../../components/layout/DashboardShell";
import ChatWidget from "../../components/ChatWidget";
import StatCard from "../../components/StatCard";
import SeverityBadge from "../../components/SeverityBadge";
import { getDoctorEscalations, getDoctorWorklist, listAllPatients } from "../../api/client";

const NAV_ITEMS = [
  { path: "/doctor", label: "Worklist", icon: LayoutDashboard },
];

export default function DoctorDashboard() {
  const [worklist, setWorklist] = useState([]);
  const [escalations, setEscalations] = useState([]);
  const [patientCount, setPatientCount] = useState(0);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const [w, e, patients] = await Promise.all([
      getDoctorWorklist(),
      getDoctorEscalations(),
      listAllPatients(),
    ]);
    setWorklist(w);
    setEscalations(e);
    setPatientCount(patients.length);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!loading) {
      gsap.fromTo(".dash-fade", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.06, ease: "power3.out" });
    }
  }, [loading]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-ink-500">
        <Loader2 className="mr-2 animate-spin" /> Loading your worklist…
      </div>
    );
  }

  const urgentCount = worklist.filter((p) => p.severity === "high").length;

  return (
    <DashboardShell title="Clinician Worklist" subtitle="Prioritized by the Clinician Assist Agent" navItems={NAV_ITEMS}>
      <div className="dash-fade grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard icon={Users} label="Total Patients" value={patientCount} tone="ink" />
        <StatCard icon={AlertTriangle} label="High Risk Today" value={urgentCount} tone="accent" />
        <StatCard icon={ClipboardList} label="Open Escalations" value={escalations.length} tone="brand" />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="dash-fade card p-6 lg:col-span-2">
          <h2 className="font-display text-lg font-semibold text-ink-900">Today's prioritized worklist</h2>
          <p className="mt-1 text-sm text-ink-500">
            Ranked by risk severity, open escalations, and days since last review.
          </p>

          {worklist.length === 0 ? (
            <p className="mt-6 text-sm text-ink-500">No assessed patients yet.</p>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-ink-100 text-xs uppercase tracking-wide text-ink-400">
                    <th className="pb-2">Patient</th>
                    <th className="pb-2">Severity</th>
                    <th className="pb-2">Last review</th>
                    <th className="pb-2">Escalations</th>
                    <th className="pb-2">Priority</th>
                    <th className="pb-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {worklist.map((p) => (
                    <tr key={p.patient_id} className="border-b border-ink-50 last:border-0">
                      <td className="py-3 font-medium text-ink-800">{p.patient_name}</td>
                      <td className="py-3"><SeverityBadge value={p.severity} /></td>
                      <td className="py-3 text-ink-500">{p.days_since_last_assessment}d ago</td>
                      <td className="py-3 text-ink-500">{p.open_escalations}</td>
                      <td className="py-3 font-semibold text-ink-800">{p.priority_score}</td>
                      <td className="py-3">
                        <Link to={`/doctor/patients/${p.patient_id}`} className="text-xs font-semibold text-brand-600 hover:underline">
                          View chart →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="dash-fade card p-6">
          <h2 className="font-display text-lg font-semibold text-ink-900">Escalation queue</h2>
          <p className="mt-1 text-sm text-ink-500">Flagged by the RAG assistant or symptom screen.</p>

          {escalations.length === 0 ? (
            <p className="mt-6 text-sm text-ink-500">No open escalations right now.</p>
          ) : (
            <ul className="mt-4 space-y-3">
              {escalations.map((t) => (
                <li key={t.id} className="rounded-xl border border-ink-100 p-3">
                  <div className="flex items-center justify-between">
                    <SeverityBadge value={t.urgency} />
                    <span className="text-xs text-ink-400">{t.category}</span>
                  </div>
                  <p className="mt-2 text-sm text-ink-700">{t.summary}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <ChatWidget />
    </DashboardShell>
  );
}
