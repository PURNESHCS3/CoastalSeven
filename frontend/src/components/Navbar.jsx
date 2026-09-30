import { Link, useNavigate } from "react-router-dom";
import { logoutUser } from "../services/authService";

function Navbar() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("user") || "null"
  );

  const handleLogout = () => {
    logoutUser();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/dashboard">
          Task Manager
        </Link>
      </div>

      <div className="navbar-links">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/projects">Projects</Link>
        <Link to="/profile">Profile</Link>
        {user?.role === "admin" && (
          <Link
            to="/admin"
            style={{
              color: "#f87171",
              fontWeight: "bold",
              border: "1px solid #ef4444",
              padding: "4px 10px",
              borderRadius: "4px",
            }}
          >
            Admin Panel
          </Link>
        )}

        {user && (
          <span className="username">
            {user.username}
          </span>
        )}

        <button onClick={handleLogout}>
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;