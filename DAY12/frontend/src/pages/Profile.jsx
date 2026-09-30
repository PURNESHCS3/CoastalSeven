import { useEffect, useState } from "react";
import { getCurrentUser, getUsers } from "../services/userService";
import Loading from "../components/Loading";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/Table";

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

        <Table className="min-w-[40rem] text-[var(--text-primary)]">
          <TableHeader>
            <TableRow>
              <TableHead scope="col">User</TableHead>
              <TableHead scope="col">Email</TableHead>
              <TableHead scope="col">Role</TableHead>
              <TableHead scope="col">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {usersList.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="h-24 text-center text-[var(--text-secondary)]">
                  No users found.
                </TableCell>
              </TableRow>
            ) : usersList.map((directoryUser) => (
              <TableRow key={directoryUser.id}>
                <TableCell className="font-medium">
                  @{directoryUser.username}
                  <div className="text-xs font-normal text-[var(--text-secondary)]">
                    ID: {directoryUser.id}
                  </div>
                </TableCell>
                <TableCell>{directoryUser.email}</TableCell>
                <TableCell className="capitalize">{directoryUser.role}</TableCell>
                <TableCell>
                  <span className={directoryUser.is_active
                    ? "inline-flex rounded-sm bg-green-100 px-2 py-1 text-xs font-medium text-green-800"
                    : "inline-flex rounded-sm bg-red-100 px-2 py-1 text-xs font-medium text-red-800"
                  }>
                    {directoryUser.is_active ? "Active" : "Inactive"}
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>
    </div>
  );
}

export default Profile;