import axios from "axios";

// ---------------------- CONFIG ----------------------
const api = axios.create({
  baseURL: "http://localhost:8000", // Backend FastAPI
  headers: {
    "Content-Type": "application/json",
  },
});
export interface User {
  id?: number;
  nom: string;
  prenom: string;
  email: string;
  password?: string;
}

export interface AuthData {
  email: string;
  password: string;
}

export interface EmailData {
  id?: number;
  sujet: string;
  corps: string;
  expediteur: string;
}

export interface OCRData {
  imageBase64: string;
}

export interface SentimentData {
  text: string;
}

export interface SummaryData {
  text: string;
}

export interface TriggerEmailData {
  userId: number;
  templateId: number;
}

// ---------------------- FONCTIONS GÉNÉRIQUES ----------------------
export const fetchData = async (endpoint: string, params?: any) => {
  const response = await api.get(endpoint, { params });
  return response.data;
};

export const postData = async (endpoint: string, data: any) => {
  const response = await api.post(endpoint, data);
  return response.data;
};

export const putData = async (endpoint: string, data: any) => {
  const response = await api.put(endpoint, data);
  return response.data;
};

export const deleteData = async (endpoint: string) => {
  const response = await api.delete(endpoint);
  return response.data;
};

// ---------------------- ROUTES USERS ----------------------
export const getUsers = () => fetchData("/users/");
export const getUserById = (id: number) => fetchData(`/users/${id}`);
export const createUser = (data: any) => postData("/users/", data);
export const updateUser = (id: number, data: any) => putData(`/users/${id}`, data);
export const deleteUser = (id: number) => deleteData(`/users/${id}`);

// ---------------------- AUTH ----------------------
export const login = (data: { email: string; password: string }) =>
  postData("/auth/login", data);

export const signup = (data: any) => postData("/auth/signup", data);

// ---------------------- EMAILS ----------------------
export const sendEmail = (data: any) => postData("/emails/send", data);
export const getEmails = () => fetchData("/emails/");

// ---------------------- OCR ----------------------
export const extractTextFromImage = (data: { imageBase64: string }) =>
  postData("/ocr/extract", data);

// ---------------------- SENTIMENT ----------------------
export const analyzeSentiment = (data: { text: string }) =>
  postData("/sentiment/analyze", data);

// ---------------------- SUMMARY ----------------------
export const summarizeText = (data: { text: string }) =>
  postData("/summary/", data);

// ---------------------- TRIGGER EMAIL ----------------------
export const triggerEmail = (data: { userId: number; templateId: number }) =>
  postData("/trigger-email/", data);

export default api;
