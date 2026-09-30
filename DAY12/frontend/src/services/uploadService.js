import api from "./api";

export const uploadProjectImage = async (projectId, file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post(`/api/uploads/projects/${projectId}/image`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};
