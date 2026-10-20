import { Activity } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-ink-100 bg-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-brand-800 text-white shadow-sm ring-2 ring-brand-100">
              <Activity size={18} className="text-white" />
            </span>
            <div className="flex flex-col text-left">
              <span className="font-display text-base font-extrabold tracking-tight text-ink-900 leading-tight">
                Smart Hospital
              </span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-brand-600 -mt-0.5">
                Management
              </span>
            </div>
          </div>
          <p className="max-w-xl text-sm text-ink-500">
            Smart Hospital Management is a clinical decision-support and hospital workflow platform.
            It is designed for clinical monitoring, cardiorespiratory risk assessment, and decision support with human doctor oversight.
          </p>
        </div>
        <div className="mt-8 flex flex-col gap-2 text-xs text-ink-400 md:flex-row md:items-center md:justify-between">
          <span>© {new Date().getFullYear()} Smart Hospital Management · Account: kumarniraj11045@gmail.com</span>
          <span>Decision support only · Human review required</span>
        </div>
      </div>
    </footer>
  );
}
