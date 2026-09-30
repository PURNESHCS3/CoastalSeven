import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getAdminStats,
  getUsersWithTasks,
  updateUserRole,
  adminUpdateTask,
  assignProjectMember,
  removeProjectMember,
} from "../services/adminService";
import { getProjects } from "../services/projectService";
import Loading from "../components/Loading";
import { cn } from "../lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/Table";

function AdminPanel() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Assign Project State
  const [selectedProject, setSelectedProject] = useState("");
  const [selectedUserToAssign, setSelectedUserToAssign] = useState("");

  // Task Editing Modal/State
  const [editingTask, setEditingTask] = useState(null);
  const [taskForm, setTaskForm] = useState({
    title: "",
    status: "pending",
    priority: "medium",
  });

  const loadData = async () => {
    try {
      const [statsData, usersData, projectsData] = await Promise.all([
        getAdminStats(),
        getUsersWithTasks(),
        getProjects(),
      ]);
      setStats(statsData);
      setUsers(usersData);
      setProjects(projectsData);
      if (projectsData.length > 0 && !selectedProject) {
        setSelectedProject(String(projectsData[0].id));
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || "Admin access required or failed to load data."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Promote / Demote User Role
  const handleRoleChange = async (userId, newRole) => {
    setError("");
    setSuccess("");
    try {
      await updateUserRole(userId, newRole);
      setSuccess(`User role updated to ${newRole.toUpperCase()} successfully!`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update user role");
    }
  };

  // Assign User to Project
  const handleAssignProject = async (e) => {
    e.preventDefault();
    if (!selectedProject || !selectedUserToAssign) return;

    setError("");
    setSuccess("");
    try {
      await assignProjectMember(
        parseInt(selectedProject, 10),
        parseInt(selectedUserToAssign, 10)
      );
      setSuccess("User assigned to project successfully!");
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to assign project");
    }
  };

  // Unassign User from Project
  const handleUnassignProject = async (projectId, userId) => {
    setError("");
    setSuccess("");
    try {
      await removeProjectMember(projectId, userId);
      setSuccess("User removed from project membership.");
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to unassign user");
    }
  };

  // Edit Task Handlers
  const handleOpenEditTask = (task) => {
    setEditingTask(task);
    setTaskForm({
      title: task.title,
      status: task.status,
      priority: task.priority,
    });
  };

  const handleSaveTask = async (e) => {
    e.preventDefault();
    if (!editingTask) return;

    setError("");
    setSuccess("");
    try {
      await adminUpdateTask(editingTask.id, taskForm);
      setSuccess(`Task #${editingTask.id} updated successfully!`);
      setEditingTask(null);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update task");
    }
  };

  if (loading) {
    return <Loading />;
  }

  const currentSelectedProj = projects.find(
    (p) => String(p.id) === String(selectedProject)
  );

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Admin Control Panel</h1>
        <span style={{
          background: "#dc2626",
          color: "white",
          padding: "5px 12px",
          borderRadius: "6px",
          fontWeight: "bold",
          fontSize: "14px",
        }}>
          ADMIN PRIVILEGES ACTIVE
        </span>
      </div>
      <p style={{ color: "#4b5563" }}>
        Manage all users, oversee assigned tasks, assign projects to members, and grant admin roles.
      </p>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* 1. Admin System Stats */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Users</h3>
            <p>{stats.total_users}</p>
          </div>
          <div className="stat-card">
            <h3>Total Projects</h3>
            <p>{stats.total_projects}</p>
          </div>
          <div className="stat-card">
            <h3>Total Tasks</h3>
            <p>{stats.total_tasks}</p>
          </div>
          <div className="stat-card">
            <h3>Completed</h3>
            <p style={{ color: "#16a34a" }}>{stats.completed_tasks}</p>
          </div>
        </div>
      )}

      {/* 2. Assign Projects to Users */}
      <section className="section">
        <div className="form-card">
          <h2>Assign Project to Users</h2>
          <form onSubmit={handleAssignProject} style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: "15px", alignItems: "end" }}>
            <div>
              <label><strong>Select Project</strong></label>
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                required
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} (ID: {p.id})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label><strong>Select User to Assign</strong></label>
              <select
                value={selectedUserToAssign}
                onChange={(e) => setSelectedUserToAssign(e.target.value)}
                required
              >
                <option value="">-- Choose User --</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    @{u.username} ({u.email})
                  </option>
                ))}
              </select>
            </div>

            <button type="submit" style={{ height: "42px" }}>
              + Assign User
            </button>
          </form>

          {currentSelectedProj && (
            <div style={{ marginTop: "20px" }}>
              <h4 style={{ margin: "0 0 10px" }}>
                Assigned Members for: <em>{currentSelectedProj.name}</em>
              </h4>
              <p style={{ fontSize: "14px", color: "#6b7280" }}>
                Project Owner ID: <strong>{currentSelectedProj.owner_id}</strong>
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Task Edit Form (If Selected) */}
      {editingTask && (
        <div className="form-card" style={{ border: "2px solid #2563eb" }}>
          <h2>Admin Edit Task #{editingTask.id}</h2>
          <form onSubmit={handleSaveTask}>
            <label><strong>Task Title</strong></label>
            <input
              type="text"
              value={taskForm.title}
              onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
              required
            />

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
              <div>
                <label><strong>Status</strong></label>
                <select
                  value={taskForm.status}
                  onChange={(e) => setTaskForm({ ...taskForm, status: e.target.value })}
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </div>

              <div>
                <label><strong>Priority</strong></label>
                <select
                  value={taskForm.priority}
                  onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>

            <div className="button-group">
              <button type="submit">Save Changes as Admin</button>
              <button
                type="button"
                onClick={() => setEditingTask(null)}
                style={{ background: "#6b7280" }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 3. Users, Roles & Assigned Tasks */}
      <section className="section">
        <h2>Users Directory & Assigned Tasks ({users.length} Users)</h2>
        <Table className="min-w-[56rem] text-[var(--text-primary)]">
          <TableHeader>
            <TableRow>
              <TableHead scope="col">User</TableHead>
              <TableHead scope="col">Email</TableHead>
              <TableHead scope="col">Role</TableHead>
              <TableHead scope="col">Status</TableHead>
              <TableHead scope="col">Assigned Tasks</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center text-[var(--text-secondary)]">
                  No users found.
                </TableCell>
              </TableRow>
            ) : users.map((user) => (
              <TableRow key={user.id}>
                <TableCell className="font-medium">
                  @{user.username}
                  <div className="text-xs font-normal text-[var(--text-secondary)]">ID: {user.id}</div>
                </TableCell>
                <TableCell>{user.email}</TableCell>
                <TableCell>
                  <select
                    aria-label={`Role for ${user.username}`}
                    value={user.role}
                    onChange={(event) => handleRoleChange(user.id, event.target.value)}
                    className="rounded-sm border border-[var(--border-color)] bg-[var(--input-bg)] px-2 py-1 font-semibold"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </TableCell>
                <TableCell>
                  <span className={cn(
                    "inline-flex rounded-sm px-2 py-1 text-xs font-medium",
                    user.is_active
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  )}>
                    {user.is_active ? "Active" : "Inactive"}
                  </span>
                </TableCell>
                <TableCell>
                  <div className="min-w-72 space-y-2">
                    <div className="text-xs text-[var(--text-secondary)]">
                      {user.assigned_tasks?.length || 0} tasks
                    </div>
                    {user.assigned_tasks?.length ? user.assigned_tasks.map((task) => (
                      <div key={task.id} className="flex items-center justify-between gap-3 border-t border-[var(--border-color)] pt-2">
                        <div>
                          <div className="font-medium">{task.title}</div>
                          <div className="text-xs text-[var(--text-secondary)]">
                            {task.status} · {task.priority} priority
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleOpenEditTask(task)}
                          className="shrink-0 rounded-sm bg-amber-500 px-2 py-1 text-xs font-medium text-white hover:bg-amber-600"
                        >
                          Edit Task
                        </button>
                      </div>
                    )) : (
                      <span className="text-sm text-[var(--text-secondary)]">No tasks assigned.</span>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>
    </div>
  );
}

export default AdminPanel;
