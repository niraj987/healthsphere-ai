import { Activity } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-ink-100 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
              <Activity size={16} />
            </span>
            <span className="font-display font-bold text-ink-900">HealthSphere AI</span>
          </div>
          <p className="max-w-xl text-sm text-ink-500">
            HealthSphere AI is a clinical decision-support and monitoring platform. It is not a
            substitute for professional medical advice, diagnosis, or treatment. Always consult a
            qualified clinician for medical decisions.
          </p>
        </div>
        <div className="mt-8 flex flex-col gap-2 text-xs text-ink-400 md:flex-row md:items-center md:justify-between">
          <span>© {new Date().getFullYear()} HealthSphere AI — Academic Capstone Project</span>
          <span>Decision support only · Human review required</span>
        </div>
      </div>
    </footer>
  );
}
