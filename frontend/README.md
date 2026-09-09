# Disha AI — Frontend

Frontend for **DishaAI – AI-Powered Student Learning Assistant and
Personalized Career & Education Advisor**, built with React + Vite +
Tailwind CSS, designed to plug straight into the existing Django REST
Framework backend.

> **Status: Phase 1 — App shell scaffold.** This README will be replaced
> with the full setup/feature guide once all phases are complete.

## What's in Phase 1

- Vite + React 18 project scaffold, full folder structure (components,
  pages, layouts, context, services, hooks, utils, routes)
- Tailwind CSS configured with a custom design-token system (see
  `tailwind.config.js`: `iris` primary, `marigold` accent, `growth`
  secondary, `ink` neutral scale, plus shadows/gradients/animations)
- React Router routing skeleton — every sidebar destination resolves to a
  real (placeholder) page so the app shell can be reviewed end-to-end
- Axios instance (`src/services/api.js`) with a request interceptor that
  attaches the JWT access token, and a response interceptor that
  transparently refreshes on `401` via `/api/auth/token/refresh/`
- `ThemeContext` for light/dark mode, persisted to `localStorage`,
  respecting the OS preference on first load
- Reusable shell components: `Navbar`, `Sidebar` (collapsible + mobile
  drawer), `Footer`, `Logo`, `Loader`/`Skeleton`, `ComingSoon`
- Two base layouts: `MainLayout` (sidebar + navbar, for the authenticated
  app) and `PublicLayout` (top nav + footer, for marketing pages)
- `react-toastify` wired up globally for future success/error toasts

Pages other than the shell itself (Dashboard widgets, AI Chat, Career
Recommendation, Roadmap, etc.) are intentionally **placeholders** right
now — they exist only so routing/navigation can be reviewed. Each is
built out fully in its dedicated phase.

## Setup

```bash
cd frontend
npm install
cp .env.example .env   # point VITE_API_BASE_URL at your running backend
npm run dev
```

The app runs at `http://localhost:5173`. Make sure the Django backend is
running (see the backend's own README) and that its `CORS_ALLOWED_ORIGINS`
includes `http://localhost:5173`.

## Tech stack

React 18 · Vite 5 · Tailwind CSS 3 · React Router DOM 6 · Axios ·
React Hook Form · Context API · React Icons · Heroicons · Framer Motion ·
Chart.js (react-chartjs-2) · React Toastify · React Markdown

## Project structure

```
src/
  assets/        static images/illustrations
  components/    common, dashboard, chat, career, roadmap
  layouts/       MainLayout, PublicLayout
  pages/         one folder per feature area
  hooks/         shared custom hooks
  context/       ThemeContext (AuthContext, NotificationContext to follow)
  services/      api.js (axios) + per-feature service files
  utils/         constants, tokenStorage
  routes/        AppRoutes.jsx
```
