import api from "./api";

export const getTasks = async (params = {}) => {
  const response = await api.get("/api/tasks/", {
    params,
  });

  return response.data;
};

export const getTask = async (taskId) => {
  const response = await api.get(`/api/tasks/${taskId}`);
  return response.data;
};

export const createTask = async (projectId, taskData) => {
  const response = await api.post(
    "/api/tasks/",
    taskData,
    {
      params: {
        project_id: projectId,
      },
    }
  );

  return response.data;
};

export const updateTask = async (taskId, taskData) => {
  const response = await api.put(
    `/api/tasks/${taskId}`,
    taskData
  );

  return response.data;
};

export const deleteTask = async (taskId) => {
  await api.delete(`/api/tasks/${taskId}`);
};