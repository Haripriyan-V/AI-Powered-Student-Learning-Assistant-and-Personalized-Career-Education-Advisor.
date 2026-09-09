import { NavLink } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import clsx from 'clsx';
import {
  HomeIcon,
  ChatBubbleLeftRightIcon,
  BriefcaseIcon,
  MapIcon,
  ClipboardDocumentCheckIcon,
  ChartBarIcon,
  BookOpenIcon,
  AcademicCapIcon,
  BuildingLibraryIcon,
  CalendarDaysIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  BellIcon,
  Cog6ToothIcon,
  ChevronLeftIcon,
  FolderOpenIcon,
} from '@heroicons/react/24/outline';
import Logo from './Logo';
import { ROUTES } from '../../utils/constants';

const NAV_GROUPS = [
  {
    label: 'Overview',
    items: [{ to: ROUTES.DASHBOARD, label: 'Dashboard', icon: HomeIcon }],
  },
  {
    label: 'Guidance',
    items: [
      { to: ROUTES.CHAT, label: 'AI Chat Assistant', icon: ChatBubbleLeftRightIcon },
      { to: ROUTES.CAREER, label: 'Career Recommendation', icon: BriefcaseIcon },
      { to: ROUTES.SKILL_GAP, label: 'Skill Gap Analyzer', icon: ChartBarIcon },
      { to: ROUTES.ROADMAP, label: 'Learning Roadmap', icon: MapIcon },
      { to: ROUTES.ASSESSMENT, label: 'Skill Assessment', icon: ClipboardDocumentCheckIcon },
    ],
  },
  {
    label: 'Learn',
    items: [
      { to: ROUTES.COURSES, label: 'Courses', icon: BookOpenIcon },
      { to: ROUTES.RESOURCES, label: 'Resources', icon: FolderOpenIcon },
      { to: ROUTES.SCHOLARSHIPS, label: 'Scholarships', icon: AcademicCapIcon },
      { to: ROUTES.COLLEGES, label: 'Colleges', icon: BuildingLibraryIcon },
      { to: ROUTES.EXAMS, label: 'Entrance Exams', icon: CalendarDaysIcon },
    ],
  },
  {
    label: 'Tools',
    items: [
      { to: ROUTES.RESUME, label: 'Resume Analyzer', icon: DocumentTextIcon },
      { to: ROUTES.PLANNER, label: 'Study Planner', icon: ClipboardDocumentListIcon },
    ],
  },
  {
    label: 'Account',
    items: [
      { to: ROUTES.NOTIFICATIONS, label: 'Notifications', icon: BellIcon },
      { to: ROUTES.SETTINGS, label: 'Settings', icon: Cog6ToothIcon },
    ],
  },
];

function SidebarContent({ collapsed, onToggleCollapse }) {
  return (
    <div className="flex h-full flex-col">
      <div className={clsx('flex items-center px-4 py-5', collapsed ? 'justify-center' : 'justify-between')}>
        {!collapsed && <Logo size="sm" />}
        {collapsed && <Logo size="sm" withWordmark={false} />}
        {!collapsed && (
          <button
            onClick={onToggleCollapse}
            className="rounded-lg p-1.5 text-ink-400 hover:bg-ink-100 hover:text-ink-700 dark:hover:bg-ink-800 dark:hover:text-ink-200 hidden lg:flex"
            aria-label="Collapse sidebar"
          >
            <ChevronLeftIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto px-3 pb-4">
        {NAV_GROUPS.map((group) => (
          <div key={group.label} className="mb-5">
            {!collapsed && (
              <p className="px-3 pb-1.5 text-[11px] font-semibold uppercase tracking-wider text-ink-400 dark:text-ink-500">
                {group.label}
              </p>
            )}
            <ul className="space-y-1">
              {group.items.map(({ to, label, icon: Icon }) => (
                <li key={to}>
                  <NavLink
                    to={to}
                    className={({ isActive }) =>
                      clsx('sidebar-link', isActive && 'active trail-marker', collapsed && 'justify-center px-2')
                    }
                    title={collapsed ? label : undefined}
                  >
                    <Icon className="h-5 w-5 shrink-0" />
                    {!collapsed && <span className="truncate">{label}</span>}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      {collapsed && (
        <button
          onClick={onToggleCollapse}
          className="mx-3 mb-4 flex items-center justify-center rounded-lg p-2 text-ink-400 hover:bg-ink-100 hover:text-ink-700 dark:hover:bg-ink-800 dark:hover:text-ink-200"
          aria-label="Expand sidebar"
        >
          <ChevronLeftIcon className="h-4 w-4 rotate-180" />
        </button>
      )}
    </div>
  );
}

export default function Sidebar({ mobileOpen, onCloseMobile, collapsed, onToggleCollapse }) {
  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={clsx(
          'hidden lg:flex lg:flex-col border-r border-ink-100 dark:border-ink-800 bg-white dark:bg-ink-900 transition-[width] duration-200 shrink-0',
          collapsed ? 'w-[76px]' : 'w-64',
        )}
      >
        <SidebarContent collapsed={collapsed} onToggleCollapse={onToggleCollapse} />
      </aside>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onCloseMobile}
              className="fixed inset-0 z-40 bg-ink-950/40 lg:hidden"
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'tween', duration: 0.22 }}
              className="fixed inset-y-0 left-0 z-50 w-72 bg-white dark:bg-ink-900 shadow-lift lg:hidden"
            >
              <SidebarContent collapsed={false} onToggleCollapse={onCloseMobile} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
