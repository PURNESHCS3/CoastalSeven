import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { logoutUser } from "../services/authService";
import { getCurrentUser } from "../services/userService";
import ThemeToggle from "./ui/ThemeToggle";

function Navbar() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    let active = true;
    getCurrentUser()
      .then((userData) => {
        if (!active) return;
        setUser(userData);
        localStorage.setItem("user", JSON.stringify(userData));
      })
      .catch(() => {
        if (!active) return;
        setUser(null);
        localStorage.removeItem("user");
      });

    return () => { active = false; };
  }, []);

  const handleLogout = () => { logoutUser(); navigate("/login"); };
  return (
    <nav className="sticky top-0 z-40 border-b border-gray-200 bg-white/95 shadow-sm backdrop-blur dark:border-gray-800 dark:bg-gray-950/95">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4">
        <Link to="/dashboard" className="text-xl font-bold text-blue-600">Task Manager</Link>
        <div className="flex flex-wrap items-center gap-3 text-sm">
          <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 dark:text-gray-200">Dashboard</Link>
          <Link to="/projects" className="text-gray-700 hover:text-blue-600 dark:text-gray-200">Projects</Link>
          <Link to="/profile" className="text-gray-700 hover:text-blue-600 dark:text-gray-200">Profile</Link>
          {user?.role === "admin" && <Link to="/admin" className="rounded-md border border-red-200 bg-red-50 px-3 py-1.5 font-medium text-red-600">Admin</Link>}
          {user && <span className="hidden text-gray-600 sm:inline dark:text-gray-300">{user.username}</span>}
          <ThemeToggle />
          <button type="button" onClick={handleLogout} className="rounded-md bg-red-600 px-3 py-2 text-white hover:bg-red-700">Logout</button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
