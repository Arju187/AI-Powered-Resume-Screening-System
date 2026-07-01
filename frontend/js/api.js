const API_BASE = "http://127.0.0.1:8000";

const Auth = {
  getToken() { return localStorage.getItem("ats_token"); },
  setSession({ access_token, role, full_name, user_id }) {
    localStorage.setItem("ats_token", access_token);
    localStorage.setItem("ats_role", role);
    localStorage.setItem("ats_name", full_name);
    localStorage.setItem("ats_user_id", user_id);
  },
  getRole() { return localStorage.getItem("ats_role"); },
  getName() { return localStorage.getItem("ats_name") || ""; },
  isLoggedIn() { return !!this.getToken(); },
  logout() {
    localStorage.removeItem("ats_token");
    localStorage.removeItem("ats_role");
    localStorage.removeItem("ats_name");
    localStorage.removeItem("ats_user_id");
    window.location.href = "login.html";
  },
};

async function apiRequest(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  const token = Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isForm && body !== undefined) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : (isForm ? body : JSON.stringify(body)),
  });

  if (res.status === 204) return null;

  let data;
  try { data = await res.json(); } catch { data = null; }

  if (!res.ok) {
    const detail = data && data.detail;
    let message = "Something went wrong. Please try again.";
    if (typeof detail === "string") message = detail;
    else if (Array.isArray(detail) && detail.length) message = detail.map(d => d.msg).join(" · ");

    if (res.status === 401 && token) {
      Auth.logout();
    }
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  return data;
}

const Api = {
  register: (payload) => apiRequest("/api/auth/register", { method: "POST", body: payload }),
  login: (payload) => apiRequest("/api/auth/login", { method: "POST", body: payload }),
  me: () => apiRequest("/api/auth/me"),
  changePassword: (payload) => apiRequest("/api/auth/change-password", { method: "PUT", body: payload }),

  getMyProfile: () => apiRequest("/api/candidates/me"),
  updateMyProfile: (payload) => apiRequest("/api/candidates/me", { method: "PUT", body: payload }),
  uploadResume: (formData) => apiRequest("/api/candidates/me/resume", { method: "POST", body: formData, isForm: true }),
  deleteResume: () => apiRequest("/api/candidates/me/resume", { method: "DELETE" }),
  getRecommendations: () => apiRequest("/api/candidates/me/recommendations"),

  listJobs: (params = "") => apiRequest(`/api/jobs${params}`),
  getJob: (id) => apiRequest(`/api/jobs/${id}`),
  createJob: (payload) => apiRequest("/api/jobs", { method: "POST", body: payload }),
  updateJob: (id, payload) => apiRequest(`/api/jobs/${id}`, { method: "PUT", body: payload }),
  deleteJob: (id) => apiRequest(`/api/jobs/${id}`, { method: "DELETE" }),
  getRankedCandidates: (jobId) => apiRequest(`/api/jobs/${jobId}/candidates`),

  applyToJob: (payload) => apiRequest("/api/applications", { method: "POST", body: payload }),
  myApplications: () => apiRequest("/api/applications/me"),
  listApplicationsAdmin: (params = "") => apiRequest(`/api/applications${params}`),
  updateApplicationStatus: (id, status) => apiRequest(`/api/applications/${id}/status`, { method: "PUT", body: { status } }),

  adminDashboard: () => apiRequest("/api/admin/dashboard"),
  adminListCandidates: (params = "") => apiRequest(`/api/admin/candidates${params}`),
  adminGetCandidate: (id) => apiRequest(`/api/admin/candidates/${id}`),
  adminDeleteCandidate: (id) => apiRequest(`/api/admin/candidates/${id}`, { method: "DELETE" }),

  myNotifications: () => apiRequest("/api/notifications/me"),
  markNotificationRead: (id) => apiRequest(`/api/notifications/${id}/read`, { method: "PUT" }),
  markAllNotificationsRead: () => apiRequest("/api/notifications/read-all", { method: "PUT" }),
};
