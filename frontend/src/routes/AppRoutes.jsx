import { Routes, Route, Navigate } from 'react-router-dom';
import { tokenStorage } from '../utils/tokenStorage';

import PublicLayout from '../layouts/PublicLayout';
import MainLayout from '../layouts/MainLayout';

import Landing from '../pages/Landing';
import About from '../pages/About';
import Contact from '../pages/Contact';
import NotFound from '../pages/NotFound';
import Notifications from '../pages/Notifications';

import Login from '../pages/auth/Login';
import Register from '../pages/auth/Register';
import ForgotPassword from '../pages/auth/ForgotPassword';

import Dashboard from '../pages/dashboard/Dashboard';
import Profile from '../pages/profile/Profile';
import Chat from '../pages/chat/Chat';
import Career from '../pages/career/Career';
import SkillAssessment from '../pages/career/SkillAssessment';
import Roadmap from '../pages/roadmap/Roadmap';
import Courses from '../pages/courses/Courses';
import Resources from '../pages/resources/Resources';
import Scholarships from '../pages/scholarships/Scholarships';
import Colleges from '../pages/colleges/Colleges';
import Exams from '../pages/exams/Exams';
import Resume from '../pages/resume/Resume';
import SkillGapAnalyzer from '../pages/skillgap/SkillGapAnalyzer';
import StudyPlanner from '../pages/studyplanner/StudyPlanner';
import Settings from '../pages/settings/Settings';

import { ROUTES } from '../utils/constants';

function ProtectedRoute({ children }) {
  const token = tokenStorage.getAccessToken();
  if (!token) {
    return <Navigate to={ROUTES.LOGIN} replace />;
  }
  return children;
}

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public / marketing pages */}
      <Route element={<PublicLayout />}>
        <Route path={ROUTES.HOME} element={<Landing />} />
        <Route path={ROUTES.ABOUT} element={<About />} />
        <Route path={ROUTES.CONTACT} element={<Contact />} />
      </Route>

      {/* Auth pages (standalone, no shell) */}
      <Route path={ROUTES.LOGIN} element={<Login />} />
      <Route path={ROUTES.REGISTER} element={<Register />} />
      <Route path={ROUTES.FORGOT_PASSWORD} element={<ForgotPassword />} />

      {/* App shell (sidebar + navbar) */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path={ROUTES.DASHBOARD} element={<Dashboard />} />
        <Route path={ROUTES.PROFILE} element={<Profile />} />
        <Route path={ROUTES.CHAT} element={<Chat />} />
        <Route path={ROUTES.CAREER} element={<Career />} />
        <Route path={ROUTES.SKILL_GAP} element={<SkillGapAnalyzer />} />
        <Route path={ROUTES.ASSESSMENT} element={<SkillAssessment />} />
        <Route path={ROUTES.ROADMAP} element={<Roadmap />} />
        <Route path={ROUTES.COURSES} element={<Courses />} />
        <Route path={ROUTES.RESOURCES} element={<Resources />} />
        <Route path={ROUTES.SCHOLARSHIPS} element={<Scholarships />} />
        <Route path={ROUTES.COLLEGES} element={<Colleges />} />
        <Route path={ROUTES.EXAMS} element={<Exams />} />
        <Route path={ROUTES.RESUME} element={<Resume />} />
        <Route path={ROUTES.PLANNER} element={<StudyPlanner />} />
        <Route path={ROUTES.NOTIFICATIONS} element={<Notifications />} />
        <Route path={ROUTES.SETTINGS} element={<Settings />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
