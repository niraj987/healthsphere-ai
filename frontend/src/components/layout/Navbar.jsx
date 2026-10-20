import { Link, useNavigate } from "react-router-dom";
import { Activity, LogOut, Menu, Sparkles, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  const dashboardPath = user?.role === "doctor" ? "/doctor" : "/patient";

  return (
    <header className="sticky top-0 z-40 border-b border-ink-100 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3.5">
        <Link to="/" className="flex items-center gap-3 group">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-brand-800 text-white shadow-sm ring-2 ring-brand-100 group-hover:scale-105 transition-transform">
            <Activity size={22} className="text-white" />
          </span>
          <div className="flex flex-col text-left">
            <span className="font-display text-base md:text-lg font-extrabold tracking-tight text-ink-900 leading-tight">
              Smart Hospital
            </span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-brand-600 -mt-0.5 flex items-center gap-1.5">
              Management <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            </span>
          </div>
        </Link>

        <nav className="hidden items-center gap-7 text-sm font-medium text-ink-600 md:flex">
          <Link to="/examinations" className="flex items-center gap-1.5 rounded-lg bg-brand-50 px-3 py-1.5 font-semibold text-brand-700 hover:bg-brand-100 transition">
            <Sparkles size={15} /> Clinical Examinations
          </Link>
          <a href="/#features" className="hover:text-brand-700">Platform</a>
          <a href="/#how-it-works" className="hover:text-brand-700">How it works</a>
          <a href="/#safety" className="hover:text-brand-700">Clinical safety</a>
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {user ? (
            <>
              <Link to={dashboardPath} className="btn-secondary">Dashboard</Link>
              <button onClick={handleLogout} className="btn-primary">
                <LogOut size={16} /> Sign out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary">Sign in</Link>
              <Link to="/register" className="btn-primary">Get started</Link>
            </>
          )}
        </div>

        <button className="md:hidden" onClick={() => setOpen((o) => !o)} aria-label="Toggle menu">
          {open ? <X /> : <Menu />}
        </button>
      </div>

      {open && (
        <div className="border-t border-ink-100 bg-white px-6 py-4 md:hidden">
          <div className="flex flex-col gap-3">
            <Link to="/examinations" className="text-sm font-semibold text-brand-700">Clinical Examinations</Link>
            <a href="/#features" className="text-sm font-medium text-ink-600">Platform</a>
            <a href="/#how-it-works" className="text-sm font-medium text-ink-600">How it works</a>
            <a href="/#safety" className="text-sm font-medium text-ink-600">Clinical safety</a>
            {user ? (
              <>
                <Link to={dashboardPath} className="btn-secondary w-full">Dashboard</Link>
                <button onClick={handleLogout} className="btn-primary w-full">Sign out</button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn-secondary w-full">Sign in</Link>
                <Link to="/register" className="btn-primary w-full">Get started</Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
