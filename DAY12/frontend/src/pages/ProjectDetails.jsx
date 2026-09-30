import { useEffect, useState } from "react";
import {
  Link,
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  getProject,
  updateProject,
  deleteProject,
} from "../services/projectService";

import {
  createTask,
  deleteTask,
  getTasks,
  updateTask,
} from "../services/taskService";

import { getCurrentUser, getUsers } from "../services/userService";
import { assignProjectMember, removeProjectMember } from "../services/adminService";
import Loading from "../components/Loading";

function ProjectDetails() {
  const { projectId } = useParams();
  const navigate = useNavigate();

  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState("all");

  const [editingProject, setEditingProject] = useState(false);
  const [projectForm, setProjectForm] = useState({
    name: "",
    description: "",
  });

  const [taskForm, setTaskForm] = useState({
    title: "",
    description: "",
    priority: "medium",
    due_date: "",
    assignee_id: "",
  });

  const [editingTaskId, setEditingTaskId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadData = async () => {
    try {
      const [projectData, taskData, usersData, userData] = await Promise.all([
        getProject(projectId),
        getTasks({ project_id: projectId }),
        getUsers().catch(() => []),
        getCurrentUser(),
      ]);

      setProject(projectData);
      setProjectForm({
        name: projectData.name,
        description: projectData.description || "",
      });
      setTasks(taskData);
      setUsers(usersData);
      setCurrentUser(userData);
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load project");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  // Project Edit Handlers
  const handleProjectUpdate = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      const updated = await updateProject(projectId, projectForm);
      setProject(updated);
      setEditingProject(false);
      setSuccess("Project details updated successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update project");
    }
  };

  const handleProjectDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this project and all its tasks?")) {
      return;
    }
    try {
      await deleteProject(projectId);
      navigate("/projects");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete project");
    }
  };

  const [selectedUserToAssign, setSelectedUserToAssign] = useState("");

  const handleAssignUser = async (e) => {
    e.preventDefault();
    if (!selectedUserToAssign) return;
    setError("");
    setSuccess("");
    try {
      const updatedProj = await assignProjectMember(projectId, parseInt(selectedUserToAssign, 10));
      setProject(updatedProj);
      setSelectedUserToAssign("");
      setSuccess("User assigned to project successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to assign user");
    }
  };

  const handleRemoveMember = async (userId) => {
    setError("");
    setSuccess("");
    try {
      await removeProjectMember(projectId, userId);
      setSuccess("User removed from project membership.");
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to remove member");
    }
  };

  // Task Handlers
  const handleTaskChange = (event) => {
    setTaskForm({
      ...taskForm,
      [event.target.name]: event.target.value,
    });
  };

  const handleTaskSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    try {
      const data = {
        title: taskForm.title,
        description: taskForm.description || null,
        priority: taskForm.priority,
        due_date: taskForm.due_date || null,
        assignee_id: taskForm.assignee_id ? parseInt(taskForm.assignee_id, 10) : null,
      };

      if (editingTaskId) {
        await updateTask(editingTaskId, data);
        setSuccess("Task updated successfully!");
      } else {
        await createTask(projectId, data);
        setSuccess("Task created successfully!");
      }

      setTaskForm({
        title: "",
        description: "",
        priority: "medium",
        due_date: "",
        assignee_id: "",
      });
      setEditingTaskId(null);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Task operation failed");
    }
  };

  const handleEditTask = (task) => {
    setEditingTaskId(task.id);
    setTaskForm({
      title: task.title,
      description: task.description || "",
      priority: task.priority,
      due_date: task.due_date || "",
      assignee_id: task.assignee_id ? String(task.assignee_id) : "",
    });
    window.scrollTo({ top: 300, behavior: "smooth" });
  };

  const handleStatusChange = async (task, status) => {
    setError("");
    try {
      await updateTask(task.id, { status });
      setSuccess(status === "completed" ? "Task marked complete." : "Task status updated.");
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to update status");
    }
  };

  const handleDeleteTask = async (id) => {
    if (!window.confirm("Are you sure you want to delete this task?")) {
      return;
    }
    setError("");
    try {
      await deleteTask(id);
      setSuccess("Task deleted successfully.");
      await loadData();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete task");
    }
  };

  if (loading) {
    return <Loading />;
  }

  if (!project) {
    return (
      <div>
        <p>Project not found.</p>
        <Link to="/projects">← Back to Projects</Link>
      </div>
    );
  }

  const displayedTasks = tasks.filter((t) => {
    if (filterStatus === "all") return true;
    return t.status === filterStatus;
  });

  const isAdmin = currentUser?.role === "admin";

  return (
    <div className="project-details-page">
      <Link className="back-link" to="/projects">
        ← Back to Projects
      </Link>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* Project Header & Controls */}
      <div className="card project-header-card">
        {editingProject ? (
          <form onSubmit={handleProjectUpdate}>
            <h3>Edit Project Info</h3>
            <input
              type="text"
              name="name"
              value={projectForm.name}
              onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
              required
            />
            <textarea
              name="description"
              value={projectForm.description}
              onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
            />
            <div className="button-group">
              <button type="submit">Save Changes</button>
              <button
                type="button"
                onClick={() => setEditingProject(false)}
                style={{ background: "#6b7280" }}
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div className="project-header-content">
              <div>
                <h1 style={{ margin: "0 0 10px" }}>{project.name}</h1>
                <p className="project-description">
                  {project.description || "No description provided."}
                </p>
              </div>
              <div className="button-group project-header-actions">
                {isAdmin && (
                  <button
                    className="project-action-button edit-project-button"
                    type="button"
                    onClick={() => setEditingProject(true)}
                  >
                    Edit Project
                  </button>
                )}
                {isAdmin && (
                  <button
                    className="project-action-button delete-project-button"
                    type="button"
                    onClick={handleProjectDelete}
                  >
                    Delete Project
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Project Members Section */}
      <div className="card project-members-card">
        <h3 style={{ margin: "0 0 10px" }}>
          Project Members ({project.members ? project.members.length : 0})
        </h3>

        {isAdmin && (
          <form className="project-members-form" onSubmit={handleAssignUser}>
            <select
              value={selectedUserToAssign}
              onChange={(e) => setSelectedUserToAssign(e.target.value)}
              style={{ maxWidth: "320px" }}
              required
            >
              <option value="">-- Assign a User to this Project --</option>
              {users
                .filter((u) => !project.members?.some((m) => m.id === u.id))
                .map((u) => (
                  <option key={u.id} value={u.id}>
                    @{u.username} ({u.email})
                  </option>
                ))}
            </select>
            <button type="submit" style={{ padding: "8px 16px" }}>
              + Assign Member
            </button>
          </form>
        )}

        {(!project.members || project.members.length === 0) ? (
          <p style={{ color: "#6b7280", margin: 0 }}>
            No members assigned yet. {isAdmin ? "Assign team members using the dropdown above." : ""}
          </p>
        ) : (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
            {project.members.map((member) => (
              <div
                key={member.id}
                style={{
                  background: "#f3f4f6",
                  border: "1px solid #d1d5db",
                  padding: "6px 12px",
                  borderRadius: "20px",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  fontSize: "14px",
                }}
              >
                <span><strong>@{member.username}</strong> ({member.email})</span>
                {isAdmin && (
                  <button
                    type="button"
                    onClick={() => handleRemoveMember(member.id)}
                    style={{
                      background: "#ef4444",
                      color: "white",
                      border: "none",
                      borderRadius: "50%",
                      width: "18px",
                      height: "18px",
                      lineHeight: "18px",
                      padding: 0,
                      cursor: "pointer",
                      fontSize: "10px",
                    }}
                    title="Remove user from project"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Task Creation / Edit Form */}
      {isAdmin && (
      <div className="form-card task-form-card">
        <h2>{editingTaskId ? "Edit Task" : "Create New Task"}</h2>
        <form className="task-form" onSubmit={handleTaskSubmit}>
          <label><strong>Task Title *</strong></label>
          <input
            type="text"
            name="title"
            placeholder="e.g. Design wireframes, setup database"
            value={taskForm.title}
            onChange={handleTaskChange}
            required
            minLength={1}
            maxLength={200}
          />

          <label><strong>Task Description</strong></label>
          <textarea
            name="description"
            placeholder="Describe what needs to be done..."
            value={taskForm.description}
            onChange={handleTaskChange}
          />

          <div className="task-form-fields">
            <div>
              <label><strong>Priority</strong></label>
              <select
                name="priority"
                value={taskForm.priority}
                onChange={handleTaskChange}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div>
              <label><strong>Due Date</strong></label>
              <input
                type="date"
                name="due_date"
                value={taskForm.due_date}
                onChange={handleTaskChange}
              />
            </div>

            <div>
              <label><strong>Assignee</strong></label>
              <select
                name="assignee_id"
                value={taskForm.assignee_id}
                onChange={handleTaskChange}
              >
                <option value="">Unassigned</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.username} ({u.email})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="button-group">
            <button className="task-submit-button" type="submit">
              {editingTaskId ? "Update Task" : "+ Add Task"}
            </button>
            {editingTaskId && (
              <button
                type="button"
                onClick={() => {
                  setEditingTaskId(null);
                  setTaskForm({
                    title: "",
                    description: "",
                    priority: "medium",
                    due_date: "",
                    assignee_id: "",
                  });
                }}
                style={{ background: "#6b7280" }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>
      )}

      {/* Task Filters & Task List */}
      <section className="section tasks-section">
        <div className="task-list-header">
          <h2>Tasks ({displayedTasks.length} of {tasks.length})</h2>
          <div className="task-filters">
            {["all", "pending", "in_progress", "completed"].map((st) => (
              <button
                key={st}
                className={`task-filter-button task-filter-${st}${filterStatus === st ? " is-active" : ""}`}
                type="button"
                onClick={() => setFilterStatus(st)}
                aria-pressed={filterStatus === st}
              >
                {st.replace("_", " ").toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {displayedTasks.length === 0 ? (
          <p>No tasks match this filter. Add a new task above!</p>
        ) : (
          <div className="task-list">
            {displayedTasks.map((task) => {
              const assignedUser = users.find((u) => u.id === task.assignee_id);
              return (
                <div className="task-card" key={task.id}>
                  <div>
                    <h3 style={{ margin: "0 0 8px" }}>{task.title}</h3>
                    <p style={{ margin: "0 0 10px" }}>
                      {task.description || "No description provided."}
                    </p>
                    <div className="task-metadata" style={{ fontSize: "13px" }}>
                      <span>
                        Priority:{" "}
                        <strong style={{
                          color: task.priority === "high" ? "#dc2626" : task.priority === "medium" ? "#d97706" : "#2563eb"
                        }}>
                          {task.priority.toUpperCase()}
                        </strong>
                      </span>
                      <span>
                        Status: <strong>{task.status.replace("_", " ").toUpperCase()}</strong>
                      </span>
                      {task.due_date && <span>Due: <strong>{task.due_date}</strong></span>}
                      {assignedUser && (
                        <span>Assigned to: <strong>@{assignedUser.username}</strong></span>
                      )}
                    </div>
                  </div>

                  {isAdmin ? <div className="button-group task-actions">
                    <select
                      value={task.status}
                      onChange={(event) => handleStatusChange(task, event.target.value)}
                      style={{ padding: "6px 10px" }}
                    >
                      <option value="pending">Pending</option>
                      <option value="in_progress">In Progress</option>
                      <option value="completed">Completed</option>
                    </select>

                    <button
                      className="task-action-button edit-task-button"
                      type="button"
                      onClick={() => handleEditTask(task)}
                    >
                      Edit
                    </button>

                    <button
                      className="task-action-button delete-task-button"
                      type="button"
                      onClick={() => handleDeleteTask(task.id)}
                    >
                      Delete
                    </button>
                  </div> : task.assignee_id === currentUser?.id && task.status !== "completed" ? (
                    <button
                      className="task-submit-button"
                      type="button"
                      onClick={() => handleStatusChange(task, "completed")}
                    >
                      Mark Complete
                    </button>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default ProjectDetails;