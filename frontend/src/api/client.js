import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("hs_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem("hs_token");
      localStorage.removeItem("hs_user");
      if (!window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ---- Auth ----
export const registerUser = (payload) => api.post("/api/auth/register", payload).then((r) => r.data);
export const loginUser = (payload) => api.post("/api/auth/login", payload).then((r) => r.data);

// ---- Patient ----
export const getMyProfile = () => api.get("/api/patients/me").then((r) => r.data);
export const updateMyProfile = (payload) => api.put("/api/patients/me", payload).then((r) => r.data);
export const addVitals = (payload) => api.post("/api/patients/me/vitals", payload).then((r) => r.data);
export const listMyVitals = () => api.get("/api/patients/me/vitals").then((r) => r.data);
export const listPatientVitals = (patientId) => api.get(`/api/patients/${patientId}/vitals`).then((r) => r.data);
export const uploadLabReport = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api
    .post("/api/patients/me/lab-reports", formData, { headers: { "Content-Type": "multipart/form-data" } })
    .then((r) => r.data);
};
export const listMyLabReports = () => api.get("/api/patients/me/lab-reports").then((r) => r.data);
export const getPatient = (patientId) => api.get(`/api/patients/${patientId}`).then((r) => r.data);

// ---- Assessments ----
export const runAssessment = (patientId) => api.post(`/api/assessments/patients/${patientId}/run`).then((r) => r.data);
export const listAssessments = (patientId) => api.get(`/api/assessments/patients/${patientId}`).then((r) => r.data);
export const getLatestAssessment = (patientId) =>
  api.get(`/api/assessments/patients/${patientId}/latest`).then((r) => r.data);

// ---- Doctor ----
export const listAllPatients = () => api.get("/api/doctor/patients").then((r) => r.data);
export const listCarePlans = (patientId) => api.get(`/api/doctor/patients/${patientId}/care-plans`).then((r) => r.data);
export const reviewCarePlan = (planId, payload) => api.put(`/api/doctor/care-plans/${planId}/review`, payload).then((r) => r.data);

// ---- Agents ----
export const getDailyDigest = (patientId) => api.get(`/api/patients/${patientId}/daily-digest`).then((r) => r.data);
export const createReminder = (patientId, label, dueInHours = 24) =>
  api.post(`/api/patients/${patientId}/reminders`, null, { params: { label, due_in_hours: dueInHours } }).then((r) => r.data);
export const getDoctorWorklist = () => api.get("/api/doctor/worklist").then((r) => r.data);
export const getChartPrep = (patientId) => api.get(`/api/doctor/patients/${patientId}/chart-prep`).then((r) => r.data);
export const draftCarePlan = (patientId, assessmentId) =>
  api.post(`/api/doctor/patients/${patientId}/draft-care-plan`, null, { params: { assessment_id: assessmentId } }).then((r) => r.data);
export const getDoctorEscalations = () => api.get("/api/doctor/escalations").then((r) => r.data);

// ---- Medicine recommendations ----
export const generateMedicineRecommendations = (patientId, assessmentId) =>
  api
    .post(`/api/patients/${patientId}/medicine-recommendations`, null, { params: { assessment_id: assessmentId } })
    .then((r) => r.data);
export const reviewMedicineRecommendation = (recId, payload) =>
  api.post(`/api/medicine-recommendations/${recId}/review`, payload).then((r) => r.data);

// ---- Chat / RAG chatbot ----
export const sendChatMessage = (payload) => api.post("/api/chat/message", payload).then((r) => r.data);

// ---- Notifications ----
export const listNotifications = () => api.get("/api/notifications").then((r) => r.data);
export const markNotificationRead = (id) => api.put(`/api/notifications/${id}/read`).then((r) => r.data);
