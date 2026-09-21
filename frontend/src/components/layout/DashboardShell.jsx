import { Link, useLocation, useNavigate } from "react-router-dom";
import { Activity, Bell, LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function DashboardShell({ title, subtitle, navItems, children, headerRight }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen bg-ink-50">
      {/* Sidebar */}
      <aside className="hidden w-64 flex-shrink-0 flex-col border-r border-ink-100 bg-white px-4 py-6 md:flex">
        <Link to="/" className="mb-8 flex items-center gap-2 px-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
            <Activity size={16} />
          </span>
          <span className="font-display text-base font-bold text-ink-900">HealthSphere</span>
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
