const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Erro ${res.status} em ${path}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getRooms: () => request('/api/rooms'),
  updateRoom: (id, payload) => request(`/api/rooms/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  getSectors: () => request('/api/sectors'),

  getTeams: () => request('/api/teams'),
  updateTeam: (id, payload) => request(`/api/teams/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  getConstraints: () => request('/api/constraints'),
  updateConstraint: (id, payload) => request(`/api/constraints/${id}`, { method: 'PATCH', body: JSON.stringify(payload) }),

  runAllocation: () => request('/api/allocate', { method: 'POST' }),
  getBaseline: () => request('/api/allocate/baseline'),

  getGovernance: () => request('/api/governance'),
  getRun: (id) => request(`/api/governance/${id}`),
  intervene: (runId, payload) => request(`/api/governance/${runId}/intervene`, { method: 'POST', body: JSON.stringify(payload) }),

  getTrustTests: () => request('/api/trust-tests'),
  getMonitoring: () => request('/api/monitoring'),
};

export default api;
