import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import gsap from "gsap";
import { ArrowLeft, ClipboardCheck, FileWarning, LayoutDashboard, Loader2, PenSquare, Pill } from "lucide-react";
import DashboardShell from "../../components/layout/DashboardShell";
import ChatWidget from "../../components/ChatWidget";
import RiskGauge from "../../components/RiskGauge";
import VitalsChart from "../../components/VitalsChart";
import SeverityBadge from "../../components/SeverityBadge";
import {
  draftCarePlan, generateMedicineRecommendations, getChartPrep, getLatestAssessment,
  getPatient, listCarePlans, listPatientVitals, reviewCarePlan,
} from "../../api/client";

const NAV_ITEMS = [{ path: "/doctor", label: "Worklist", icon: LayoutDashboard }];

export default function PatientDetail() {
  const { patientId } = useParams();
  const [patient, setPatient] = useState(null);
  const [vitals, setVitals] = useState([]);
  const [assessment, setAssessment] = useState(null);
  const [brief, setBrief] = useState("");
  const [carePlans, setCarePlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [drafting, setDrafting] = useState(false);
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    const [p, v, chartPrep, plans] = await Promise.all([
      getPatient(patientId),
      listPatientVitals(patientId),
      getChartPrep(patientId),
      listCarePlans(patientId),
    ]);
    setPatient(p);
    setVitals(v);
    setBrief(chartPrep.brief);
    setCarePlans(plans);

    try {
      const latest = await getLatestAssessment(patientId);
      setAssessment(latest);
    } catch {
      setAssessment(null);
    }
    setLoading(false);
  }, [patientId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!loading) {
      gsap.fromTo(".dash-fade", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.06, ease: "power3.out" });
    }
  }, [loading]);

  const handleDraftCarePlan = async () => {
    if (!assessment) return;
    setDrafting(true);
    try {
      await generateMedicineRecommendations(patientId, assessment.id);
      await draftCarePlan(patientId, assessment.id);
      const plans = await listCarePlans(patientId);
      setCarePlans(plans);
      setMessage("Draft care plan generated from the Clinician Assist Agent — review below.");
    } catch (err) {
      setMessage(err?.response?.data?.detail || "Could not generate a draft care plan.");
    } finally {
      setDrafting(false);
    }
  };

  const handleReview = async (planId, approval_status) => {
    await reviewCarePlan(planId, { approval_status });
    const plans = await listCarePlans(patientId);
    setCarePlans(plans);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-ink-500">
        <Loader2 className="mr-2 animate-spin" /> Loading patient chart…
      </div>
    );
  }

  return (
    <DashboardShell title={patient?.full_name || `Patient #${patientId}`} subtitle="Patient chart" navItems={NAV_ITEMS}>
      <Link to="/doctor" className="dash-fade mb-6 inline-flex items-center gap-1 text-sm font-medium text-ink-500 hover:text-brand-600">
        <ArrowLeft size={16} /> Back to worklist
      </Link>

      {message && <div className="dash-fade mb-6 rounded-xl bg-brand-50 px-4 py-3 text-sm text-brand-700">{message}</div>}

      {/* Chart-prep brief */}
      <div className="dash-fade card mb-8 flex items-start gap-4 border-brand-100 bg-gradient-to-r from-brand-50 to-white p-6">
        <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white">
          <FileWarning size={18} />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-brand-600">Clinician Assist Agent · Chart prep</p>
          <p className="mt-1 whitespace-pre-line text-sm text-ink-700">{brief}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Vitals trend */}
        <div className="dash-fade card p-6 lg:col-span-2">
          <h2 className="font-display text-lg font-semibold text-ink-900">Vitals trend</h2>
          <div className="mt-4">
            <VitalsChart vitals={vitals} />
          </div>
        </div>

        {/* Risk breakdown */}
        <div className="dash-fade card p-6">
          <h2 className="font-display text-lg font-semibold text-ink-900">Latest assessment</h2>
          {assessment ? (
            <>
              <div className="mt-5 grid grid-cols-3 gap-2">
                <RiskGauge label="Heart" percent={assessment.heart_risk_pct} size={88} />
                <RiskGauge label="Diabetes" percent={assessment.diabetes_risk_pct} size={88} />
                <RiskGauge label="CKD" percent={assessment.ckd_risk_pct} size={88} />
              </div>
              <div className="mt-4"><SeverityBadge value={assessment.overall_severity} /></div>
              <button
                onClick={handleDraftCarePlan}
                disabled={drafting}
                className="btn-primary mt-5 w-full !py-2 text-xs"
              >
                <Pill size={14} /> {drafting ? "Drafting…" : "Draft care plan + medicine candidates"}
              </button>
            </>
          ) : (
            <p className="mt-4 text-sm text-ink-500">No assessment on file for this patient yet.</p>
          )}
        </div>
      </div>

      {/* Care plans */}
      <div className="dash-fade card mt-8 p-6">
        <h2 className="font-display text-lg font-semibold text-ink-900">Care plans</h2>
        <p className="mt-1 text-sm text-ink-500">
          Drafts from the Clinician Assist Agent require your review before becoming active.
        </p>

        {carePlans.length === 0 ? (
          <p className="mt-6 text-sm text-ink-500">No care plans yet.</p>
        ) : (
          <div className="mt-4 space-y-4">
            {carePlans.map((plan) => (
              <div key={plan.id} className="rounded-xl border border-ink-100 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <SeverityBadge value={plan.approval_status} />
                  <span className="text-xs text-ink-400">{new Date(plan.created_at).toLocaleString()}</span>
                </div>
                <p className="mt-2 text-sm text-ink-700">{plan.clinical_summary}</p>

                {plan.prescriptions?.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">Candidate medicine info (pending your approval)</p>
                    {plan.prescriptions.map((rx, i) => (
                      <div key={i} className="rounded-lg bg-ink-50 p-3 text-xs text-ink-600">
                        <p className="font-semibold text-ink-800">{rx.candidate_drug_name} <span className="font-normal text-ink-400">· {rx.drug_class}</span></p>
                        <p className="mt-1">{rx.general_info}</p>
                        {rx.warnings?.length > 0 && (
                          <p className="mt-1 text-accent-600">⚠ {rx.warnings.join(" ")}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {plan.approval_status === "pending" && (
                  <div className="mt-4 flex gap-2">
                    <button onClick={() => handleReview(plan.id, "approved")} className="btn-primary !px-3 !py-1.5 text-xs">
                      <ClipboardCheck size={14} /> Approve
                    </button>
                    <button onClick={() => handleReview(plan.id, "modified")} className="btn-secondary !px-3 !py-1.5 text-xs">
                      <PenSquare size={14} /> Mark modified
                    </button>
                    <button onClick={() => handleReview(plan.id, "rejected")} className="btn-secondary !px-3 !py-1.5 text-xs !text-accent-600">
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <ChatWidget />
    </DashboardShell>
  );
}
