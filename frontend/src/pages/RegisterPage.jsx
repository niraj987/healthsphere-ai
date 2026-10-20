import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import gsap from "gsap";
import { Activity, Eye, EyeOff, Stethoscope, User, UserPlus } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "Niraj Kumar", email: "kumarniraj11045@gmail.com", password: "", role: "patient" });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const cardRef = useRef(null);

  useEffect(() => {
    gsap.fromTo(cardRef.current, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await register(form);
      navigate(user.role === "doctor" ? "/doctor" : "/patient");
    } catch (err) {
      setError(err?.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-50 px-6 py-12">
      <div ref={cardRef} className="card w-full max-w-md p-8 shadow-soft">
        <Link to="/" className="mb-6 flex items-center gap-3 group">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-600 to-brand-800 text-white shadow-sm ring-2 ring-brand-100 group-hover:scale-105 transition-transform">
            <Activity size={20} className="text-white" />
          </span>
          <div className="flex flex-col text-left">
            <span className="font-display text-base font-extrabold tracking-tight text-ink-900 leading-tight">
              Smart Hospital
            </span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-brand-600 -mt-0.5 flex items-center gap-1.5">
              Management <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            </span>
          </div>
        </Link>

        <h1 className="font-display text-2xl font-bold text-ink-900">Create your account</h1>
        <p className="mt-1 text-sm text-ink-500">Access Smart Hospital Management platform.</p>

        <div className="mt-5 grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => setForm({ ...form, role: "patient" })}
            className={`flex flex-col items-center gap-2 rounded-xl border p-4 text-sm font-semibold transition ${
              form.role === "patient" ? "border-brand-500 bg-brand-50 text-brand-700" : "border-ink-200 text-ink-500"
            }`}
          >
            <User size={20} /> Patient
          </button>
          <button
            type="button"
            onClick={() => setForm({ ...form, role: "doctor" })}
            className={`flex flex-col items-center gap-2 rounded-xl border p-4 text-sm font-semibold transition ${
              form.role === "doctor" ? "border-brand-500 bg-brand-50 text-brand-700" : "border-ink-200 text-ink-500"
            }`}
          >
            <Stethoscope size={20} /> Clinician
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="label">Full name</label>
            <input
              required
              className="input"
              placeholder="Jane Doe"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Email</label>
            <input
              type="email"
              required
              className="input"
              placeholder="you@example.com"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div>
            <label className="label">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                minLength={6}
                className="input pr-10"
                placeholder="At least 6 characters"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-800 focus:outline-none transition"
                title={showPassword ? "Hide password" : "Show password"}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} className="text-brand-600 font-bold" /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {error && <p className="rounded-lg bg-accent-50 px-3 py-2 text-sm text-accent-700">{error}</p>}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            <UserPlus size={16} /> {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-500">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-brand-700 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
