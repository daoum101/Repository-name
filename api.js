import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API });

export const listSectors = () => api.get("/sectors").then((r) => r.data);
export const listProjects = () => api.get("/projects").then((r) => r.data);
export const getProject = (id) => api.get(`/projects/${id}`).then((r) => r.data);
export const createProject = (data) => api.post("/projects", data).then((r) => r.data);
export const updateProject = (id, data) => api.patch(`/projects/${id}`, data).then((r) => r.data);
export const deleteProject = (id) => api.delete(`/projects/${id}`).then((r) => r.data);
export const duplicateProject = (id) => api.post(`/projects/${id}/duplicate`).then((r) => r.data);
export const generateProject = (id) => api.post(`/projects/${id}/generate`).then((r) => r.data);
export const getSeoScore = (id) => api.get(`/projects/${id}/seo-score`).then((r) => r.data);
export const exportUrl = (id) => `${API}/projects/${id}/export`;
export const previewUrl = (id) => `${API}/projects/${id}/preview`;
