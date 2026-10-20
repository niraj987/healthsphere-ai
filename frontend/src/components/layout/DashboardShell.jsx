import { Link, useLocation, useNavigate } from "react-router-dom";
import { Activity, Bell, LogOut, Sparkles } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function DashboardShell({ title, subtitle, navItems, children, headerRight }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-ink-50">
      {/* Sidebar */}
      <aside className="hidden w-64 flex-shrink-0 flex-col border-r border-ink-100 bg-white px-4 py-6 md:flex">
        <Link to="/" className="mb-8 flex items-center gap-3 px-2 group">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-brand-800 text-white shadow-sm ring-2 ring-brand-100 group-hover:scale-105 transition-transform">
            <Activity size={18} className="text-white" />
          </span>
          <div className="flex flex-col text-left">
            <span className="font-display text-sm font-extrabold tracking-tight text-ink-900 leading-tight">
              Smart Hospital
            </span>
            <span className="text-[10px] font-bold uppercase tracking-wider text-brand-600 -mt-0.5 flex items-center gap-1">
              Management <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            </span>
          </div>
        </Link>

        <nav className="flex flex-1 flex-col gap-1">
          {navItems.map((item) => {
            const active = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                  active ? "bg-brand-50 text-brand-700" : "text-ink-600 hover:bg-ink-50 hover:text-ink-900"
                }`}
              >
                <item.icon size={18} />
                {item.label}
              </Link>
            );
          })}

          <div className="my-2 border-t border-ink-100 pt-2">
            <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-ink-400">Clinical AI Hub</p>
            <Link
              to="/examinations"
              className={`mt-1 flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${
                location.pathname === "/examinations"
                  ? "bg-brand-50 text-brand-700 font-semibold shadow-xs"
                  : "text-ink-700 hover:bg-brand-50/50 hover:text-brand-700"
              }`}
            >
              <Sparkles size={18} className="text-brand-600" />
              Clinical Examinations
            </Link>
          </div>
        </nav>

        <div className="mt-auto rounded-xl bg-ink-50 p-3">
          <p className="truncate text-sm font-semibold text-ink-900">{user?.full_name}</p>
          <p className="truncate text-xs capitalize text-ink-500">{user?.role}</p>
          <button
            onClick={() => {
              logout();
              navigate("/");
            }}
            className="mt-2 flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-xs font-semibold text-ink-500 hover:bg-white hover:text-accent-600"
          >
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1">
        <header className="sticky top-0 z-20 border-b border-ink-100 bg-white/80 px-6 py-5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-display text-xl font-bold text-ink-900">{title}</h1>
              {subtitle && <p className="text-sm text-ink-500">{subtitle}</p>}
            </div>
            <div className="flex items-center gap-3">
              {headerRight}
              <button className="rounded-full border border-ink-200 p-2 text-ink-500 hover:text-brand-600">
                <Bell size={18} />
              </button>
            </div>
          </div>
        </header>
        <main className="px-6 py-8">{children}</main>
      </div>
    </div>
  );
}
