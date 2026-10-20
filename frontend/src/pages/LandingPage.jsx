import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  Activity, Bot, FileScan, HeartPulse, MessagesSquare, Pill,
  ShieldCheck, Sparkles, Stethoscope, TimerReset, TrendingUp, Users, Wind,
} from "lucide-react";
import HeroScene from "../components/three/HeroScene";
import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";

gsap.registerPlugin(ScrollTrigger);

const FEATURES = [
  {
    icon: Sparkles,
    title: "Breast Cancer & Oncology ML",
    desc: "Diagnostic fine needle aspirate (FNA) biopsy analysis (97.4% accuracy) and tumor cell morphology screening.",
  },
  {
    icon: HeartPulse,
    title: "Cardiovascular Heart Disease",
    desc: "Clinical heart disease examination predicting coronary risk using resting BP, cholesterol, ECG, and vessel stenosis.",
  },
  {
    icon: FileScan,
    title: "OCR Lab Report Ingestion",
    desc: "Upload lab reports as PDFs or photos — extracts biomarkers (HbA1c, BP, cholesterol, SpO2) automatically.",
  },
  {
    icon: Wind,
    title: "Cardiopulmonary Monitoring",
    desc: "Real-time SpO2, ECG rhythm, HRV, respiratory rate, and airway FEV1/PEFR pulmonary metrics assessment.",
  },
  {
    icon: TrendingUp,
    title: "Explainable & Longitudinal",
    desc: "Every risk score comes with plain-language explanations and trend analysis against patient history.",
  },
  {
    icon: Bot,
    title: "Patient Care Agent",
    desc: "Daily digests, friendly adherence nudges, and plain-language explanations of clinical vitals.",
  },
  {
    icon: Stethoscope,
    title: "Clinician Assist Agent",
    desc: "Prioritized patient worklists, chart-prep summaries, and draft care plans for doctor approval.",
  },
  {
    icon: Pill,
    title: "Medicine Decision Support",
    desc: "Pulls general drug-class information from RxNav and openFDA for clinician review.",
  },
  {
    icon: MessagesSquare,
    title: "RAG Assistant & Escalation",
    desc: "Grounded health chatbot with automatic human-in-the-loop escalation for urgent or red-flag symptoms.",
  },
  {
    icon: ShieldCheck,
    title: "Clinical Safety First",
    desc: "Every AI output is advisory. Diagnosis, prescriptions, and care plans always require doctor approval.",
  },
];

const STEPS = [
  { title: "Upload & Register", desc: "Patients register, log vitals, and upload lab reports through the portal." },
  { title: "AI Assessment", desc: "OCR + multi-disease ML engine generate a risk score with a SHAP-style explanation." },
  { title: "Agents Assist", desc: "Patient Care Agent summarizes results; Clinician Assist Agent preps the doctor's worklist." },
  { title: "Doctor Reviews", desc: "The doctor reviews the draft care plan and medicine candidates, then approves or edits." },
  { title: "Ongoing Monitoring", desc: "Reminders, longitudinal trend tracking, and the assistant chatbot keep care on track." },
];

export default function LandingPage() {
  const heroTextRef = useRef(null);
  const statsRef = useRef(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.fromTo(
        heroTextRef.current.children,
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, duration: 0.9, stagger: 0.12, ease: "power3.out" }
      );

      gsap.utils.toArray(".reveal-up").forEach((el) => {
        gsap.fromTo(
          el,
          { opacity: 0, y: 40 },
          {
            opacity: 1,
            y: 0,
            duration: 0.8,
            ease: "power3.out",
            scrollTrigger: { trigger: el, start: "top 85%" },
          }
        );
      });

      gsap.utils.toArray(".reveal-stagger").forEach((group) => {
        gsap.fromTo(
          group.children,
          { opacity: 0, y: 30 },
          {
            opacity: 1,
            y: 0,
            duration: 0.6,
            stagger: 0.08,
            ease: "power3.out",
            scrollTrigger: { trigger: group, start: "top 85%" },
          }
        );
      });

      if (statsRef.current) {
        gsap.utils.toArray(".stat-number").forEach((el) => {
          const target = Number(el.dataset.value);
          const obj = { val: 0 };
          gsap.to(obj, {
            val: target,
            duration: 1.6,
            ease: "power2.out",
            scrollTrigger: { trigger: el, start: "top 90%" },
            onUpdate: () => {
              el.textContent = Math.round(obj.val) + (el.dataset.suffix || "");
            },
          });
        });
      }
    });

    return () => ctx.revert();
  }, []);

  return (
    <div className="overflow-x-hidden">
      <Navbar />

      {/* HERO */}
      <section className="relative mx-auto flex max-w-7xl flex-col items-center gap-10 px-6 pb-20 pt-16 md:flex-row md:pt-24">
        <div ref={heroTextRef} className="relative z-10 flex-1">
          <span className="badge bg-brand-100 text-brand-700 shadow-sm border border-brand-200/60">
            <ShieldCheck size={14} className="text-brand-600" /> AI-Powered Clinical Care Platform
          </span>
          <h1 className="mt-5 font-display text-4xl font-extrabold leading-tight text-ink-900 md:text-5xl lg:text-6xl">
            Smart Hospital Management <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-brand-600 via-teal-600 to-indigo-600 bg-clip-text text-transparent">Clinical Decision Platform</span>
          </h1>
          <p className="mt-5 max-w-xl text-base text-ink-600 md:text-lg">
            Empowering modern healthcare with automated lab report OCR, multi-disease & cardiorespiratory risk assessment, intelligent Patient & Clinician workflows, and doctor-approved care plans.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/examinations" className="btn-primary flex items-center gap-2 !bg-gradient-to-r !from-brand-600 !to-teal-600 shadow-md hover:shadow-lg">
              <Sparkles size={16} /> Clinical AI Examinations
            </Link>
            <Link to="/register" className="btn-secondary">Get started as a patient</Link>
            <Link to="/login" className="btn-secondary">Clinician sign in</Link>
          </div>

          <div ref={statsRef} className="mt-10 grid grid-cols-3 gap-6">
            <div>
              <p className="stat-number font-display text-3xl font-bold text-ink-900" data-value="4" data-suffix="">0</p>
              <p className="text-xs text-ink-500">Diseases/vitals modeled per patient</p>
            </div>
            <div>
              <p className="stat-number font-display text-3xl font-bold text-ink-900" data-value="2" data-suffix=" agents">0</p>
              <p className="text-xs text-ink-500">Patient + clinician assistants</p>
            </div>
            <div>
              <p className="stat-number font-display text-3xl font-bold text-ink-900" data-value="100" data-suffix="%">0</p>
              <p className="text-xs text-ink-500">Care decisions doctor-approved</p>
            </div>
          </div>
        </div>

        <div className="relative h-80 w-full flex-1 md:h-[26rem]">
          <div className="absolute inset-0 rounded-xl2 bg-gradient-to-br from-brand-50 via-white to-accent-50" />
          <HeroScene className="relative h-full w-full" />
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-6">
          <div className="reveal-up mx-auto max-w-2xl text-center">
            <h2 className="font-display text-3xl font-bold text-ink-900">A complete clinical workflow, not just a model</h2>
            <p className="mt-3 text-ink-600">
              From document upload to a doctor-approved care plan, every step is designed around
              explainability and human oversight.
            </p>
          </div>

          <div className="reveal-stagger mt-14 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f) => (
              <div key={f.title} className="card p-6 transition hover:-translate-y-1 hover:shadow-soft">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
                  <f.icon size={20} />
                </span>
                <h3 className="mt-4 font-display text-base font-semibold text-ink-900">{f.title}</h3>
                <p className="mt-2 text-sm text-ink-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="py-20">
        <div className="mx-auto max-w-5xl px-6">
          <div className="reveal-up mx-auto max-w-2xl text-center">
            <h2 className="font-display text-3xl font-bold text-ink-900">How it works</h2>
            <p className="mt-3 text-ink-600">One continuous loop from upload to ongoing care.</p>
          </div>

          <div className="reveal-stagger mt-14 space-y-4">
            {STEPS.map((step, idx) => (
              <div key={step.title} className="card flex items-start gap-5 p-6">
                <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-brand-600 font-display font-bold text-white">
                  {idx + 1}
                </span>
                <div>
                  <h3 className="font-display text-base font-semibold text-ink-900">{step.title}</h3>
                  <p className="mt-1 text-sm text-ink-500">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SAFETY */}
      <section id="safety" className="bg-brand-800 py-20 text-white">
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-10 px-6 md:grid-cols-2 md:items-center">
          <div className="reveal-up">
            <span className="badge bg-white/10 text-white">
              <ShieldCheck size={14} /> Clinical safety
            </span>
            <h2 className="mt-5 font-display text-3xl font-bold">Decision support, not a diagnosis machine</h2>
            <p className="mt-4 text-brand-100">
              Every AI-generated risk score, medicine candidate, and draft care plan is clearly labeled
              and held in a pending state until a licensed clinician reviews it. Our agents summarize,
              prioritize, and remind — they never decide.
            </p>
          </div>
          <div className="reveal-stagger grid grid-cols-1 gap-4 sm:grid-cols-2">
            {[
              { icon: Users, text: "Human-in-the-loop on every care plan and prescription candidate." },
              { icon: TimerReset, text: "Red-flag symptoms are escalated instantly, never answered by the bot." },
              { icon: Activity, text: "Risk scores are screening signals, not medical diagnoses." },
              { icon: ShieldCheck, text: "Built for an academic capstone — transparent thresholds throughout." },
            ].map((item) => (
              <div key={item.text} className="rounded-xl2 bg-white/10 p-5">
                <item.icon size={20} />
                <p className="mt-3 text-sm text-brand-50">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="reveal-up mx-auto max-w-4xl rounded-xl2 bg-gradient-to-br from-brand-600 to-brand-800 px-8 py-14 text-center text-white shadow-soft">
          <h2 className="font-display text-3xl font-bold">Ready to see it in action?</h2>
          <p className="mx-auto mt-3 max-w-xl text-brand-100">
            Create a patient or clinician account and explore the full workflow — assessment, agents,
            and the RAG assistant — in a live demo environment.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/register" className="btn-primary bg-white !text-brand-700 hover:bg-brand-50">Create an account</Link>
            <Link to="/login" className="btn-secondary !border-white/30 !bg-transparent !text-white hover:!bg-white/10">Sign in</Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
