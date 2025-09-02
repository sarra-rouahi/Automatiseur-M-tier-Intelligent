import axiosClient from "./axiosClient";

export const triggerApi = {
  startEmailListener: (data: any) => axiosClient.post("/triggers/start", data),
};
