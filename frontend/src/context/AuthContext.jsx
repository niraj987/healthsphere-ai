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
    const data = await loginUser({ email, password });
    persist(data);
    return data.user;
  };

  const register = async (payload) => {
    const data = await registerUser(payload);
    persist(data);
    return data.user;
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
