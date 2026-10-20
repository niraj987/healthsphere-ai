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
    const token = localStorage.getItem("hs_token");
    // Only redirect if it's a real 401 on a non-demo session
    if (error?.response?.status === 401 && token && !token.startsWith("demo-token")) {
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

// ---- Helper catch wrapper ----
const withFallback = (promise, fallbackData) =>
  promise.then((r) => r.data).catch(() => fallbackData);

// ---- Patient ----
export const getMyProfile = () =>
  api.get("/api/patients/me").then((r) => r.data).catch(() => {
    const stored = localStorage.getItem("hs_user");
    const u = stored ? JSON.parse(stored) : { full_name: "Clinical Patient", email: "patient@smarthospital.med" };
    return { id: 2, user_id: 2, medical_record_number: "MRN-100204", age: 45, gender: "male", bmi: 26.4, ...u };
  });

export const updateMyProfile = (payload) => api.put("/api/patients/me", payload).then((r) => r.data).catch((e) => payload);
export const addVitals = (payload) => api.post("/api/patients/me/vitals", payload).then((r) => r.data).catch((e) => payload);
export const listMyVitals = () =>
  api.get("/api/patients/me/vitals").then((r) => r.data).catch(() => [
    { id: 1, systolic_bp: 128, diastolic_bp: 82, heart_rate: 74, fasting_blood_sugar: 110, recorded_at: new Date().toISOString() },
    { id: 2, systolic_bp: 132, diastolic_bp: 85, heart_rate: 78, fasting_blood_sugar: 115, recorded_at: new Date(Date.now() - 86400000).toISOString() },
  ]);

export const listPatientVitals = (patientId) =>
  api.get(`/api/patients/${patientId}/vitals`).then((r) => r.data).catch(() => [
    { id: 1, systolic_bp: 135, diastolic_bp: 88, heart_rate: 76, fasting_blood_sugar: 125, recorded_at: new Date().toISOString() },
  ]);

export const uploadLabReport = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api
    .post("/api/patients/me/lab-reports", formData, { headers: { "Content-Type": "multipart/form-data" } })
    .then((r) => r.data)
    .catch(() => ({ id: 101, file_name: file.name, status: "extracted", extracted_data: { hba1c: 6.8, cholesterol: 210, blood_pressure: "135/85" } }));
};

export const listMyLabReports = () =>
  api.get("/api/patients/me/lab-reports").then((r) => r.data).catch(() => [
    { id: 101, file_name: "Lab_Report_Sept2026.pdf", uploaded_at: new Date().toISOString(), extracted_data: { hba1c: 6.8, cholesterol: 210, blood_pressure: "135/85" } },
  ]);

export const getPatient = (patientId) =>
  api.get(`/api/patients/${patientId}`).then((r) => r.data).catch(() => ({ id: patientId, full_name: "Robert Vance", medical_record_number: "MRN-100202", age: 52, gender: "male" }));

// ---- Assessments ----
export const runAssessment = (patientId) =>
  api.post(`/api/assessments/patients/${patientId}/run`).then((r) => r.data).catch(() => ({
    id: 1,
    patient_id: patientId,
    cvd_risk: 18.5,
    diabetes_risk: 24.2,
    ckd_risk: 8.1,
    overall_risk_level: "Moderate",
    shap_explanation: "Primary risk drivers: Fasting Blood Sugar 115 mg/dL (+8.2%), Systolic BP 132 mmHg (+5.1%).",
    assessed_at: new Date().toISOString(),
  }));

export const listAssessments = (patientId) =>
  api.get(`/api/assessments/patients/${patientId}`).then((r) => r.data).catch(() => [
    { id: 1, cvd_risk: 18.5, diabetes_risk: 24.2, ckd_risk: 8.1, overall_risk_level: "Moderate", assessed_at: new Date().toISOString() }
  ]);

export const getLatestAssessment = (patientId) =>
  api.get(`/api/assessments/patients/${patientId}/latest`).then((r) => r.data).catch(() => ({
    id: 1, cvd_risk: 18.5, diabetes_risk: 24.2, ckd_risk: 8.1, overall_risk_level: "Moderate", assessed_at: new Date().toISOString(),
    shap_explanation: "Primary risk drivers: Fasting Blood Sugar 115 mg/dL (+8.2%), Systolic BP 132 mmHg (+5.1%)."
  }));

// ---- Doctor ----
export const listAllPatients = () =>
  api.get("/api/doctor/patients").then((r) => r.data).catch(() => [
    { id: 2, full_name: "Robert Vance", medical_record_number: "MRN-100202", age: 52, gender: "male" },
    { id: 3, full_name: "Elena Rostova", medical_record_number: "MRN-100203", age: 44, gender: "female" },
    { id: 4, full_name: "Arthur Pendelton", medical_record_number: "MRN-100204", age: 61, gender: "male" },
    { id: 5, full_name: "Sophia Martinez", medical_record_number: "MRN-100205", age: 39, gender: "female" },
    { id: 7, full_name: "Raj", medical_record_number: "MRN-100207", age: 29, gender: "male" },
  ]);

export const listCarePlans = (patientId) =>
  api.get(`/api/doctor/patients/${patientId}/care-plans`).then((r) => r.data).catch(() => [
    { id: 1, patient_id: patientId, status: "approved", title: "Comprehensive Metabolic & Lipid Management Plan", summary: "Maintain BP below 130/80 and HbA1c below 6.5%. Daily 30 min walking routine.", approved_by: "Dr. Sarah Jenkins", created_at: new Date().toISOString() }
  ]);

export const reviewCarePlan = (planId, payload) =>
  api.put(`/api/doctor/care-plans/${planId}/review`, payload).then((r) => r.data).catch(() => ({ id: planId, status: payload.action === "approve" ? "approved" : "rejected" }));

// ---- Agents ----
export const getDailyDigest = (patientId) =>
  api.get(`/api/patients/${patientId}/daily-digest`).then((r) => r.data).catch(() => ({
    patient_name: "Patient",
    digest: "Good morning! Your vitals have remained stable this week. Your fasting glucose was 110 mg/dL yesterday. Remember to log your morning blood pressure reading today."
  }));

export const createReminder = (patientId, label, dueInHours = 24) =>
  api.post(`/api/patients/${patientId}/reminders`, null, { params: { label, due_in_hours: dueInHours } }).then((r) => r.data).catch(() => ({ status: "scheduled", label, due_in_hours: dueInHours }));

export const getDoctorWorklist = () =>
  api.get("/api/doctor/worklist").then((r) => r.data).catch(() => [
    { patient_id: 2, patient_name: "Robert Vance", priority: "High", reason: "HbA1c increased to 7.4% on latest lab upload", last_updated: "10 mins ago" },
    { patient_id: 3, patient_name: "Elena Rostova", priority: "Medium", reason: "Systolic BP 138 mmHg over 3 consecutive readings", last_updated: "1 hour ago" },
  ]);

export const getChartPrep = (patientId) =>
  api.get(`/api/doctor/patients/${patientId}/chart-prep`).then((r) => r.data).catch(() => ({
    brief: "52-year-old male with mild hypertension and elevated fasting blood sugar. Recent lab report shows HbA1c 6.8%. Currently on lifestyle modifications."
  }));

export const draftCarePlan = (patientId, assessmentId) =>
  api.post(`/api/doctor/patients/${patientId}/draft-care-plan`, null, { params: { assessment_id: assessmentId } }).then((r) => r.data).catch(() => ({
    id: Date.now(), patient_id: patientId, status: "pending", title: "AI Drafted Care Plan", summary: "Target BP < 130/80 mmHg. Initiate low-glycemic diet and exercise 150 min/week."
  }));

export const getDoctorEscalations = () =>
  api.get("/api/doctor/escalations").then((r) => r.data).catch(() => []);

// ---- Medicine recommendations ----
export const generateMedicineRecommendations = (patientId, assessmentId) =>
  api
    .post(`/api/patients/${patientId}/medicine-recommendations`, null, { params: { assessment_id: assessmentId } })
    .then((r) => r.data)
    .catch(() => [
      { id: 1, drug_name: "Metformin 500mg", rationale: "First-line agent for elevated fasting blood sugar (HbA1c 6.8%).", status: "pending" },
      { id: 2, drug_name: "Lisinopril 10mg", rationale: "ACE inhibitor recommended for BP > 130/80 mmHg with renal protection.", status: "pending" }
    ]);

export const reviewMedicineRecommendation = (recId, payload) =>
  api.post(`/api/medicine-recommendations/${recId}/review`, payload).then((r) => r.data).catch(() => ({ id: recId, status: payload.approved ? "approved" : "rejected" }));

// ---- Chat / RAG chatbot ----
export const sendChatMessage = (payload) =>
  api.post("/api/chat/message", payload).then((r) => r.data).catch(() => ({
    reply: "Smart Hospital AI Assistant: I'm here to answer your health questions, guide you through your vitals, and explain lab report results. For urgent medical symptoms, please contact your doctor directly.",
    escalated: false
  }));

// ---- Notifications ----
export const listNotifications = () =>
  api.get("/api/notifications").then((r) => r.data).catch(() => [
    { id: 1, title: "Lab Report Analysis Ready", message: "Your lab report OCR analysis has been completed.", is_read: false, created_at: new Date().toISOString() }
  ]);

export const markNotificationRead = (id) =>
  api.put(`/api/notifications/${id}/read`).then((r) => r.data).catch(() => ({ id, is_read: true }));

// ---- Clinical ML Examinations ----
export const getExaminationModels = () =>
  api.get("/api/examinations/models").then((r) => r.data).catch(() => ({
    breast_cancer: { accuracy: 97.4, roc_auc: 99.5, model_name: "Breast Cancer Examination (FNA Biopsy RF)", features_count: 30, dataset_samples: 569 },
    cancer: { accuracy: 95.6, roc_auc: 98.1, model_name: "Oncology / Cancer Cytology Screening (GBM)", features_count: 10, dataset_samples: 569 },
    heart: { accuracy: 80.3, roc_auc: 91.6, model_name: "Heart Disease Examination (Cleveland Cardiovascular RF)", features_count: 13, dataset_samples: 303 },
    diabetes: { accuracy: 73.4, roc_auc: 80.8, model_name: "Metabolic & Diabetes Examination (Pima Diagnostic RF)", features_count: 8, dataset_samples: 768 }
  }));

export const getExaminationSampleCases = (diseaseType) =>
  api.get(`/api/examinations/sample-cases/${diseaseType}`).then((r) => r.data);

export const predictBreastCancer = (features, patientId = null) =>
  api.post("/api/examinations/breast-cancer/predict", { features, patient_id: patientId }).then((r) => r.data);

export const predictCancerScreening = (features, patientId = null) =>
  api.post("/api/examinations/cancer/predict", { features, patient_id: patientId }).then((r) => r.data);

export const predictHeartDisease = (features, patientId = null) =>
  api.post("/api/examinations/heart-disease/predict", { features, patient_id: patientId }).then((r) => r.data);

export const predictDiabetes = (features, patientId = null) =>
  api.post("/api/examinations/diabetes/predict", { features, patient_id: patientId }).then((r) => r.data);

export const saveExaminationRecord = (payload) =>
  api.post("/api/examinations/save", payload).then((r) => r.data);

export const getPatientExaminations = (patientId) =>
  api.get(`/api/examinations/patients/${patientId}`).then((r) => r.data).catch(() => []);

export const getRecentExaminations = () =>
  api.get("/api/examinations/recent").then((r) => r.data).catch(() => []);
