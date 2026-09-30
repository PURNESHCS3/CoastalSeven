import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Plus, Trash2, Pencil, Image as ImageIcon } from "lucide-react";
import { getProjects, createProject, updateProject, deleteProject } from "../services/projectService";
import { getCurrentUser } from "../services/userService";
import { uploadProjectImage } from "../services/uploadService";
import { projectSchema } from "../schemas/projectSchema";
import Loading from "../components/Loading";
import FormField from "../components/forms/FormField";
import ImageUpload from "../components/forms/ImageUpload";
import Button from "../components/ui/Button";
import Dialog from "../components/ui/Dialog";
import Dropdown from "../components/ui/Dropdown";
import Toast from "../components/ui/Toast";

const emptyDefaults = { name: "", description: "", priority: "medium" };

function Projects() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingProject, setEditingProject] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [step, setStep] = useState(1);
  const [image, setImage] = useState(null);
  const [toast, setToast] = useState(null);
  const [serverError, setServerError] = useState("");
  const [priority, setPriority] = useState("medium");
  const [isAdmin, setIsAdmin] = useState(false);
  const apiBaseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
  const imageUrl = (url) => url ? (url.startsWith("http") ? url : `${apiBaseUrl}${url}`) : "";

  const { register, handleSubmit, reset, watch, trigger, formState: { errors, isSubmitting } } = useForm({ resolver: zodResolver(projectSchema), defaultValues: emptyDefaults });

  const loadProjects = async () => {
    try {
      const [projectData, userData] = await Promise.all([getProjects(), getCurrentUser()]);
      setProjects(projectData);
      setIsAdmin(userData.role === "admin");
      setServerError("");
    }
    catch (err) {
      console.error("Failed to load projects", err);
      setIsAdmin(false);
      if (err.response?.status === 401) {
        setServerError("Your session expired. Please sign in again.");
        navigate("/login", { replace: true });
      } else if (!err.response) {
        setServerError(`Unable to load projects: ${err.message || "network error"}`);
      } else {
        setServerError(err.response.data?.detail || "Unable to load projects.");
      }
    }
    finally { setLoading(false); }
  };
  useEffect(() => { loadProjects(); }, []);

  const openCreate = () => { reset(emptyDefaults); setPriority("medium"); setImage(null); setStep(1); setEditingProject(null); setServerError(""); setDialogOpen(true); };
  const openEdit = (project) => { reset({ name: project.name, description: project.description || "", priority: "medium" }); setPriority("medium"); setImage(null); setStep(1); setEditingProject(project); setServerError(""); setDialogOpen(true); };
  const closeDialog = () => { if (!isSubmitting) setDialogOpen(false); };

  const nextStep = async () => {
    const valid = await trigger(["name", "description"]);
    if (valid) setStep(2);
  };

  const onSubmit = async (data) => {
    setServerError("");
    try {
      const payload = { name: data.name, description: data.description || null };
      const project = editingProject ? await updateProject(editingProject.id, payload) : await createProject(payload);
      if (image) await uploadProjectImage(project.id, image);
      setDialogOpen(false);
      setToast({ type: "success", message: editingProject ? "Project updated successfully." : "Project created successfully." });
      await loadProjects();
    } catch (err) {
      setServerError(err.response?.data?.detail || "Project operation failed.");
    }
  };

  const handleDelete = async (projectId) => {
    if (!window.confirm("Are you sure you want to delete this project and all its tasks?")) return;
    try { await deleteProject(projectId); setToast({ type: "success", message: "Project deleted successfully." }); await loadProjects(); }
    catch (err) { setToast({ type: "error", message: err.response?.data?.detail || "Failed to delete project." }); }
  };

  if (loading) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div><h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1><p className="mt-1 text-gray-600 dark:text-gray-300">Responsive project management with validated multi-step forms.</p></div>
        {isAdmin && <Button onClick={openCreate}><Plus size={18} className="mr-2" />New Project</Button>}
      </div>
      {serverError && !dialogOpen && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{serverError}</div>}
      <div className="project-card-grid">
        {projects.length === 0 ? <p className="text-gray-500">No projects available.</p> : projects.map((project) => (
          <article className="card project-list-card" key={project.id}>
            <div className="project-list-card-header">
              <div className="project-list-card-copy">
                <h2>{project.name}</h2>
                <p className="project-list-description">{project.description || "No description provided."}</p>
              </div>
              {project.image_url ? (
                <img className="project-list-image" src={imageUrl(project.image_url)} alt={`${project.name} preview`} />
              ) : (
                <span className="project-image-empty">Not uploaded</span>
              )}
            </div>
            <p className="project-list-created">Created {new Date(project.created_at).toLocaleDateString()}</p>
            <div className="project-list-actions">
              <Link to={`/projects/${project.id}`}><Button size="small">View Tasks</Button></Link>
              {isAdmin && <Button size="small" variant="outline" onClick={() => openEdit(project)}><Pencil size={14} className="mr-1" />Edit</Button>}
              {isAdmin && <Button size="small" variant="destructive" onClick={() => handleDelete(project.id)}><Trash2 size={14} className="mr-1" />Delete</Button>}
            </div>
          </article>
        ))}
      </div>

      <Dialog open={dialogOpen} onClose={closeDialog} title={editingProject ? "Edit Project" : "Create Project"}>
        <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
          <div className="flex items-center gap-2 text-xs font-medium"><span className={`rounded-full px-3 py-1 ${step === 1 ? "bg-blue-600 text-white" : "bg-green-100 text-green-700"}`}>1. Details</span><span className="h-px flex-1 bg-gray-200" /><span className={`rounded-full px-3 py-1 ${step === 2 ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-500"}`}>2. Media & Review</span></div>
          {serverError && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700" role="alert">{serverError}</div>}
          {step === 1 ? <>
            <FormField id="project-name" label="Project Name" error={errors.name?.message} required><input id="project-name" {...register("name")} placeholder="e.g. Website Redesign" className="w-full rounded-md border border-gray-300 px-3 py-2.5" /></FormField>
            <FormField id="project-description" label="Description" error={errors.description?.message}><textarea id="project-description" rows={5} {...register("description")} placeholder="Project goals and details" className="w-full rounded-md border border-gray-300 px-3 py-2.5" /></FormField>
            <div><label className="mb-2 block text-sm font-medium text-gray-700">Priority</label><Dropdown label="Select priority" value={priority} options={[{ label: "Low", value: "low" }, { label: "Medium", value: "medium" }, { label: "High", value: "high" }]} onChange={(value) => { setPriority(value); setValue("priority", value, { shouldValidate: true }); }} /></div>
            <Button type="button" className="w-full" size="large" onClick={nextStep}>Continue</Button>
          </> : <>
            <div><div className="mb-2 flex items-center gap-2"><ImageIcon size={18} /><h3 className="font-semibold">Project Image</h3></div><ImageUpload value={image} onChange={setImage} /></div>
            <div className="rounded-lg border bg-gray-50 p-4"><h3 className="mb-3 font-semibold">Review</h3><dl className="space-y-2 text-sm"><div className="flex justify-between gap-4"><dt className="font-medium">Name</dt><dd className="text-right">{watch("name")}</dd></div><div className="flex justify-between gap-4"><dt className="font-medium">Priority</dt><dd className="capitalize">{priority}</dd></div></dl></div>
            <div className="flex gap-3"><Button type="button" variant="secondary" onClick={() => setStep(1)}>Back</Button><Button type="submit" disabled={isSubmitting} className="flex-1">{isSubmitting ? "Saving..." : editingProject ? "Save Changes" : "Create Project"}</Button></div>
          </>}
        </form>
      </Dialog>
      <Toast message={toast?.message} type={toast?.type} onClose={() => setToast(null)} />
    </div>
  );
}

export default Projects;
