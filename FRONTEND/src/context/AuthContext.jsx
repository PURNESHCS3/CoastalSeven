import { createContext, useContext, useEffect, useState } from "react";
import { getCurrentUser, loginUser } from "../services/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  const login = async (email, password) => {
    const tokens = await loginUser({ email, password });
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    return currentUser;
  };

  useEffect(() => {
    const bootstrap = async () => {
      if (!localStorage.getItem("access_token")) {
        setLoading(false);
        return;
      }
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    };

    const handleLogout = () => setUser(null);
    window.addEventListener("auth:logout", handleLogout);
    bootstrap();

    return () => window.removeEventListener("auth:logout", handleLogout);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);