import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import gsap from "gsap";
import { Activity, LogIn } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
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
      const user = await login(form.email, form.password);
      navigate(user.role === "doctor" ? "/doctor" : "/patient");
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-50 px-6">
      <div ref={cardRef} className="card w-full max-w-md p-8">
        <Link to="/" className="mb-6 flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-white">
            <Activity size={18} />
          </span>
          <span className="font-display text-lg font-bold">HealthSphere AI</span>
        </Link>

        <h1 className="font-display text-2xl font-bold text-ink-900">Welcome back</h1>
        <p className="mt-1 text-sm text-ink-500">Sign in to your patient or clinician account.</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
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
            <input
              type="password"
              required
              className="input"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>

          {error && <p className="rounded-lg bg-accent-50 px-3 py-2 text-sm text-accent-700">{error}</p>}

          <button type="submit" disabled={loading} className="btn-primary w-full">
            <LogIn size={16} /> {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-ink-500">
          Don't have an account?{" "}
          <Link to="/register" className="font-semibold text-brand-700 hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
