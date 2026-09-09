import axios from 'axios';
import { API_BASE_URL, ROUTES } from '../utils/constants';
import { tokenStorage } from '../utils/tokenStorage';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Request interceptor: attach the current access token -------------
api.interceptors.request.use((config) => {
  const isAuthEndpoint =
    config?.url?.includes('/accounts/login') || config?.url?.includes('/accounts/register');
  const token = tokenStorage.getAccessToken();
  if (token && !isAuthEndpoint) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

// --- Response interceptor: transparently refresh on 401 ----------------
// Uses a single shared in-flight refresh promise so that several requests
// failing at once only trigger one network call to /auth/token/refresh/.
let refreshPromise = null;

async function refreshAccessToken() {
  const refresh = tokenStorage.getRefreshToken();
  if (!refresh) throw new Error('No refresh token available');

  // Plain axios call (not the `api` instance) to avoid interceptor recursion.
  const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, { refresh });
  tokenStorage.setTokens({ access: data.access, refresh: data.refresh });
  return data.access;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;

    const isAuthEndpoint =
      config?.url?.includes('/accounts/login') || config?.url?.includes('/accounts/register');

    if (response?.status === 401 && !config._retry && !isAuthEndpoint) {
      config._retry = true;
      try {
        refreshPromise = refreshPromise || refreshAccessToken();
        const newAccessToken = await refreshPromise;
        refreshPromise = null;
        config.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(config);
      } catch (refreshError) {
        refreshPromise = null;
        tokenStorage.clear();
        if (window.location.pathname !== ROUTES.LOGIN) {
          window.location.href = ROUTES.LOGIN;
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default api;
