/**
 * Centralized localStorage access for JWT tokens & the cached user object.
 * Keeping this in one place means the Auth phase (Step 7) and the axios
 * interceptors (services/api.js) never drift out of sync on key names.
 */

const ACCESS_TOKEN_KEY = 'disha_access_token';
const REFRESH_TOKEN_KEY = 'disha_refresh_token';
const USER_KEY = 'disha_user';

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),

  setTokens: ({ access, refresh } = {}) => {
    if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },

  getUser: () => {
    const raw = localStorage.getItem(USER_KEY);
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setUser: (user) => {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};
