import axiosClient from "./axiosClient";

export const sentimentApi = {
  analyze: (data: { text: string }) => axiosClient.post("/sentiment/", data),
};
