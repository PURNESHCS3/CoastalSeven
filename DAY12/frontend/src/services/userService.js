import api from "./api";

export const getCurrentUser = async () => {
  const response = await api.get("/api/users/me");
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get("/api/users/");
  return response.data;
};