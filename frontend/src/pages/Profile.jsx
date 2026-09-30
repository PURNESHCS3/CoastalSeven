import { useEffect, useState } from "react";
import { getCurrentUser, getUsers } from "../services/userService";
import Loading from "../components/Loading";

function Profile() {
  const [user, setUser] = useState(null);
  const [usersList, setUsersList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfileAndUsers = async () => {
      try {
        const [userData, allUsers] = await Promise.all([
          getCurrentUser(),
          getUsers().catch(() => []),
        ]);

        setUser(userData);
        setUsersList(allUsers);

        localStorage.setItem("user", JSON.stringify(userData));
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadProfileAndUsers();
  }, []);

  if (loading) {
    return <Loading />;
  }

  if (!user) {
    return <p>Unable to load profile.</p>;
  }

  return (
    <div>
      <h1>My Profile</h1>

      <div className="profile-card">
        <p>
          <strong>ID:</strong> {user.id}
        </p>
        <p>
          <strong>Username:</strong> {user.username}
        </p>
        <p>
          <strong>Email:</strong> {user.email}
        </p>
        <p>
          <strong>Role:</strong>{" "}
          <span style={{
            background: user.role === "admin" ? "#dc2626" : "#2563eb",
            color: "white",
            padding: "2px 8px",
            borderRadius: "4px",
            fontSize: "12px",
            fontWeight: "bold",
          }}>
            {user.role.toUpperCase()}
          </span>
        </p>
        <p>
          <strong>Active:</strong> {user.is_active ? "Yes" : "No"}
        </p>
        <p>
          <strong>Created:</strong> {new Date(user.created_at).toLocaleString()}
        </p>
      </div>

      <section className="section">
        <h2>Team Members & Users Directory ({usersList.length})</h2>
        <p style={{ color: "#4b5563" }}>
          Registered users who can be assigned tasks across projects.
        </p>

        <div className="card-grid">
          {usersList.map((u) => (
            <div className="card" key={u.id}>
              <h3>@{u.username}</h3>
              <p style={{ margin: "5px 0" }}>{u.email}</p>
              <p style={{ fontSize: "13px", color: "#6b7280" }}>
                Role: <strong>{u.role}</strong> | Status:{" "}
                <span style={{ color: u.is_active ? "#16a34a" : "#dc2626" }}>
                  {u.is_active ? "Active" : "Inactive"}
                </span>
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Profile;