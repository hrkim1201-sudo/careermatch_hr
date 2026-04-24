const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(status, body) {
    super(`API ${status}: ${body}`);
    this.status = status;
    this.body = body;
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(res.status, text);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  // Programs
  listPrograms: () => request("/api/programs"),
  seedPrograms: () => request("/api/programs/seed", { method: "POST" }),
  // Match
  match: (payload) =>
    request("/api/match", { method: "POST", body: JSON.stringify(payload) }),
  generateGuide: (programId, payload) =>
    request(`/api/match/${programId}/guide`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  // Qualifications
  listQualifications: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).filter(([, v]) => v != null && v !== "")
      )
    ).toString();
    return request(`/api/qualifications${qs ? "?" + qs : ""}`);
  },
  getQualification: (qualCode) => request(`/api/qualifications/${qualCode}`),
  getQualSchedules: (qualCode) =>
    request(`/api/qualifications/${qualCode}/schedules`),
  refreshQualifications: () =>
    request("/api/qualifications/refresh", { method: "POST" }),
  // Portfolio
  createPortfolio: (payload) =>
    request("/api/portfolio", { method: "POST", body: JSON.stringify(payload) }),
};
