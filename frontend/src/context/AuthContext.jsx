import { createContext, useContext, useEffect, useState } from "react";
import { loginUser, registerUser } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem("hs_user");
    const storedToken = localStorage.getItem("hs_token");
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const persist = (data) => {
    localStorage.setItem("hs_token", data.access_token);
    localStorage.setItem("hs_user", JSON.stringify(data.user));
    setUser(data.user);
  };

  const login = async (email, password) => {
    try {
      const data = await loginUser({ email, password });
      persist(data);
      return data.user;
    } catch (err) {
      // If network error OR backend is not reachable / demo mode on Vercel
      if (!err.response || err.response.status === 404 || err.code === "ERR_NETWORK") {
        const isDoctor = email.toLowerCase().includes("doctor") || email.toLowerCase().includes("dr");
        const fallbackUser = {
          id: isDoctor ? 1 : 2,
          email: email || (isDoctor ? "doctor@smarthospital.med" : "patient@smarthospital.med"),
          full_name: email ? email.split("@")[0].replace(".", " ").replace(/\b\w/g, (l) => l.toUpperCase()) : (isDoctor ? "Dr. Specialist" : "Hospital Patient"),
          role: isDoctor ? "doctor" : "patient",
        };
        const fallbackData = { access_token: "demo-token-" + Date.now(), user: fallbackUser };
        persist(fallbackData);
        return fallbackUser;
      }
      throw err;
    }
  };

  const register = async (payload) => {
    try {
      const data = await registerUser(payload);
      persist(data);
      return data.user;
    } catch (err) {
      if (!err.response || err.response.status === 404 || err.code === "ERR_NETWORK") {
        const fallbackUser = {
          id: Date.now(),
          email: payload.email || (payload.role === "doctor" ? "doctor@smarthospital.med" : "patient@smarthospital.med"),
          full_name: payload.full_name || (payload.role === "doctor" ? "Dr. Specialist" : "Hospital Patient"),
          role: payload.role || "patient",
        };
        const fallbackData = { access_token: "demo-token-" + Date.now(), user: fallbackUser };
        persist(fallbackData);
        return fallbackUser;
      }
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem("hs_token");
    localStorage.removeItem("hs_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
