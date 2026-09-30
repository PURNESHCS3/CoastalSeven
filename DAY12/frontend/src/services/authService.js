import api from "./api";

export const registerUser = async (userData) => {
  const response = await api.post("/api/auth/register", userData);
  return response.data;
};

export const loginUser = async (email, password) => {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  const response = await api.post(
    "/api/auth/login",
    formData,
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
};

export const logoutUser = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
};