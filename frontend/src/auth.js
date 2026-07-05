import API from "./axios";

export const registerUser = async (data) => {
  return await API.post("/register", data);
};

export const loginUser = async (data) => {
  return await API.post("/login", data);
};

export const getCurrentUser = async () => {
  return await API.get("/me");
};
