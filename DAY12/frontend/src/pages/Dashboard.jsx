import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getProjects,
} from "../services/projectService";

import {
  getTasks,
  getMyTasks,
} from "../services/taskService";

import { getCurrentUser } from "../services/userService";
import Loading from "../components/Loading";

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [assignedTasks, setAssignedTasks] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [projectsData, tasksData, assignedTasksData, currentUserData] =
          await Promise.all([
            getProjects(),
            getTasks({ limit: 100 }),
            getMyTasks(),
            getCurrentUser(),
          ]);

        setProjects(projectsData);
        setTasks(tasksData);
        setAssignedTasks(assignedTasksData);
        setCurrentUser(currentUserData);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return <Loading />;
  }

  const completedTasks = tasks.filter(
    (task) => task.status === "completed"
  ).length;

  const pendingTasks = tasks.filter(
    (task) => task.status === "pending"
  ).length;
  const isAdmin = currentUser?.role === "admin";

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        {isAdmin && (
          <Link className="primary-button" to="/projects">
            + Create Project
          </Link>
        )}
      </div>

      {isAdmin && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Projects</h3>
            <p>{projects.length}</p>
          </div>

          <div className="stat-card">
            <h3>Total Tasks</h3>
            <p>{tasks.length}</p>
          </div>

          <div className="stat-card">
            <h3>Completed</h3>
            <p>{completedTasks}</p>
          </div>

          <div className="stat-card">
            <h3>Pending</h3>
            <p>{pendingTasks}</p>
          </div>
        </div>
      )}

      <section className="section assigned-tasks-section">
        <h2>My Assigned Tasks</h2>

        {assignedTasks.length === 0 ? (
          <p>No tasks are assigned to you.</p>
        ) : (
          <div className="assigned-task-list">
            {assignedTasks.map((task) => {
              const project = projects.find((item) => item.id === task.project_id);
              return (
                <article className="assigned-task-card" key={task.id}>
                  <div className="assigned-task-content">
                    <h3>{task.title}</h3>
                    {task.description && <p>{task.description}</p>}
                    <div className="assigned-task-meta">
                      <span>{project?.name || `Project #${task.project_id}`}</span>
                      <span className={`task-status status-${task.status}`}>
                        {task.status.replace("_", " ")}
                      </span>
                      <span>Priority: {task.priority}</span>
                      {task.due_date && <span>Due: {task.due_date}</span>}
                    </div>
                  </div>
                  <Link to={`/projects/${task.project_id}`}>View Task</Link>
                </article>
              );
            })}
          </div>
        )}
      </section>

      {isAdmin && (
        <section className="section">
          <h2>My Projects</h2>
          {projects.length === 0 ? (
            <p>No projects available.</p>
          ) : (
            <div className="card-grid">
              {projects.map((project) => (
                <div className="card" key={project.id}>
                  <h3>{project.name}</h3>
                  <p>{project.description || "No description"}</p>
                  <Link to={`/projects/${project.id}`}>View Project</Link>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default Dashboard;