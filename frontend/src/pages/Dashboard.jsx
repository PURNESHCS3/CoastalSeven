import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  getProjects,
} from "../services/projectService";

import {
  getTasks,
} from "../services/taskService";

import Loading from "../components/Loading";

function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [projectsData, tasksData] =
          await Promise.all([
            getProjects(),
            getTasks(),
          ]);

        setProjects(projectsData);
        setTasks(tasksData);
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

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Dashboard</h1>
        <Link to="/projects">
          <button type="button">+ Prepare New Project</button>
        </Link>
      </div>

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

      <section className="section">
        <h2>My Projects</h2>

        {projects.length === 0 ? (
          <p>No projects available.</p>
        ) : (
          <div className="card-grid">
            {projects.map((project) => (
              <div
                className="card"
                key={project.id}
              >
                <h3>{project.name}</h3>

                <p>
                  {project.description ||
                    "No description"}
                </p>

                <Link
                  to={`/projects/${project.id}`}
                >
                  View Project
                </Link>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

export default Dashboard;