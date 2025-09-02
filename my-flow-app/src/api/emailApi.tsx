import axiosClient from "./axiosClient";

export const emailApi = {
  getAll: () => axiosClient.get("/emails/"),
  getById: (id: string) => axiosClient.get(`/emails/${id}`),
  create: (data: any) => axiosClient.post("/emails/", data),
  update: (id: string, data: any) => axiosClient.put(`/emails/${id}`, data),
  delete: (id: string) => axiosClient.delete(`/emails/${id}`),
};
