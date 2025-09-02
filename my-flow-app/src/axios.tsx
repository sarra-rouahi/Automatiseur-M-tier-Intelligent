import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000', // Remplace par l'URL de ton backend
    headers: {
        'Content-Type': 'application/json',
    },
});

// Exemple d'appel GET
export const fetchData = async (endpoint: string, params?: any) => {
    const response = await api.get(endpoint, { params });
    return response.data;
};

// Exemple d'appel POST
export const postData = async (endpoint: string, data: any) => {
    const response = await api.post(endpoint, data);
    return response.data;
};

// Exemple d'appel PUT
export const putData = async (endpoint: string, data: any) => {
    const response = await api.put(endpoint, data);
    return response.data;
};

// Exemple d'appel DELETE
export const deleteData = async (endpoint: string) => {
    const response = await api.delete(endpoint);
    return response.data;
};

export default api;