import axiosClient from "./axiosClient";

export const authApi = {
   register: (data: { email: string; password: string; nom?: string; prenom?: string }) =>
    axiosClient.post("/auth/register", data),

  login: (data: { email: string; password: string }) =>
  axiosClient.post("/auth/login", data),



  loginGoogle: (data: { id_token: string }) =>
    axiosClient.post("/auth/login/google", data),

  me: () => axiosClient.get("/auth/me"),
};
