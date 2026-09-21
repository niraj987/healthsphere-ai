import { Link, useNavigate } from "react-router-dom";
import { Activity, LogOut, Menu, X } from "lucide-react";
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
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-white">
            <Activity size={18} />
          </span>
          <span className="font-display text-lg font-bold text-ink-900">
            HealthSphere <span className="text-brand-600">AI</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-8 text-sm font-medium text-ink-600 md:flex">
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
