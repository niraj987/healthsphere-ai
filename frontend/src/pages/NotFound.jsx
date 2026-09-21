import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-ink-50 text-center">
      <p className="font-display text-6xl font-bold text-brand-600">404</p>
      <p className="text-ink-600">This page doesn't exist.</p>
      <Link to="/" className="btn-primary">Back to home</Link>
    </div>
  );
}
