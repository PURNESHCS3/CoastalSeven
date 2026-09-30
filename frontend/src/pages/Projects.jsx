import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getProjects,
  createProject,
  updateProject,
  deleteProject,
} from "../services/projectService";
import Loading from "../components/Loading";

function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [projectForm, setProjectForm] = useState({
    name: "",
    description: "",
  });

  const [editingProjectId, setEditingProjectId] = useState(null);

  const loadProjects = async () => {
    try {
      const data = await getProjects();
      setProjects(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleChange = (event) => {
    setProjectForm({
      ...projectForm,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");

    try {
      if (editingProjectId) {
        await updateProject(editingProjectId, projectForm);
        setSuccess("Project updated successfully!");
      } else {
        await createProject(projectForm);
        setSuccess("Project prepared and created successfully!");
      }

      setProjectForm({
        name: "",
        description: "",
      });
      setEditingProjectId(null);
      await loadProjects();
    } catch (err) {
      setError(err.response?.data?.detail || "Project operation failed");
    }
  };

  const handleEdit = (project) => {
    setEditingProjectId(project.id);
    setProjectForm({
      name: project.name,
      description: project.description || "",
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleCancelEdit = () => {
    setEditingProjectId(null);
    setProjectForm({
      name: "",
      description: "",
    });
  };

  const handleDelete = async (projectId) => {
    if (!window.confirm("Are you sure you want to delete this project and all its tasks?")) {
      return;
    }

    setError("");
    setSuccess("");

    try {
      await deleteProject(projectId);
      setSuccess("Project deleted successfully.");
      await loadProjects();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to delete project");
    }
  };

  if (loading) {
    return <Loading />;
  }

  const currentUser = JSON.parse(localStorage.getItem("user") || "null");
  const isAdmin = currentUser?.role === "admin";

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Projects</h1>
        {isAdmin && (
          <span style={{
            background: "#dc2626",
            color: "white",
            padding: "4px 10px",
            borderRadius: "4px",
            fontSize: "12px",
            fontWeight: "bold",
          }}>
            ADMIN ACCESS
          </span>
        )}
      </div>

      <p style={{ color: "#4b5563" }}>
        {isAdmin
          ? "As an Admin, you can prepare and create projects, assign members, and manage tasks."
          : "View and manage tasks for your assigned projects. (Project creation is managed by Admins)."}
      </p>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* Prepare / Create Project Form (Admin Only or Editing) */}
      {(isAdmin || editingProjectId) ? (
        <div className="form-card">
          <h2>{editingProjectId ? "Edit Project" : "Prepare New Project (Admin Only)"}</h2>
          <form onSubmit={handleSubmit}>
            <label><strong>Project Name *</strong></label>
            <input
              type="text"
              name="name"
              placeholder="e.g. Website Redesign, Marketing Campaign"
              value={projectForm.name}
              onChange={handleChange}
              required
              minLength={1}
              maxLength={100}
            />

          <label><strong>Description</strong></label>
          <textarea
            name="description"
            placeholder="Provide context, goals, and details for this project..."
            value={projectForm.description}
            onChange={handleChange}
          />

          <div className="button-group">
            <button type="submit">
              {editingProjectId ? "Save Changes" : "+ Prepare & Create Project"}
            </button>
            {editingProjectId && (
              <button
                type="button"
                onClick={handleCancelEdit}
                style={{ background: "#6b7280" }}
              >
                Cancel
              </button>
            )}
          </div>
        </form>
      </div>
      ) : null}

      {/* Projects List */}
      <section className="section">
        <h2>My Projects ({projects.length})</h2>

        {projects.length === 0 ? (
          <p>No projects yet. {isAdmin ? "Use the form above to prepare and create your first project!" : "Waiting for an admin to assign projects to you."}</p>
        ) : (
          <div className="card-grid">
            {projects.map((project) => (
              <div className="card" key={project.id}>
                <h3>{project.name}</h3>
                <p>{project.description || "No description provided."}</p>
                <p style={{ fontSize: "12px", color: "#6b7280" }}>
                  Created: {new Date(project.created_at).toLocaleDateString()}
                </p>

                <div className="button-group">
                  <Link to={`/projects/${project.id}`}>
                    <button type="button" style={{ background: "#2563eb" }}>
                      View & Manage Tasks
                    </button>
                  </Link>

                  <button
                    type="button"
                    onClick={() => handleEdit(project)}
                    style={{ background: "#f59e0b" }}
                  >
                    Edit
                  </button>

                  {isAdmin && (
                    <button
                      type="button"
                      onClick={() => handleDelete(project.id)}
                      style={{ background: "#dc2626" }}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Projects;