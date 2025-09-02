import axiosClient from "./axiosClient";

export const userApi = {
  getAll: () => axiosClient.get("/users/users/"),
  getById: (id: string) => axiosClient.get(`/users/users/${id}`),
  create: (data: any) => axiosClient.post("/users/users/", data),
  update: (id: string, data: any) => axiosClient.put(`/users/users/${id}`, data),
  delete: (id: string) => axiosClient.delete(`/users/users/${id}`),
};
