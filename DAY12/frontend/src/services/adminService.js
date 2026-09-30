import api from "./api";

export const getAdminStats = async () => {
  const response = await api.get("/api/admin/stats");
  return response.data;
};

export const getUsersWithTasks = async () => {
  const response = await api.get("/api/admin/users-with-tasks");
  return response.data;
};

export const updateUserRole = async (userId, role) => {
  const response = await api.put(`/api/admin/users/${userId}/role`, {
    role,
  });
  return response.data;
};

export const adminUpdateTask = async (taskId, taskData) => {
  const response = await api.put(`/api/admin/tasks/${taskId}`, taskData);
  return response.data;
};

export const assignProjectMember = async (projectId, userId) => {
  const response = await api.post(`/api/projects/${projectId}/assign`, {
    user_id: userId,
  });
  return response.data;
};

export const removeProjectMember = async (projectId, userId) => {
  await api.delete(`/api/projects/${projectId}/assign/${userId}`);
};

export const getProjectMembers = async (projectId) => {
  const response = await api.get(`/api/projects/${projectId}/members`);
  return response.data;
};
