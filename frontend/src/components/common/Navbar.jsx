import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Bars3Icon,
  MagnifyingGlassIcon,
  BellIcon,
  SunIcon,
  MoonIcon,
  ChevronDownIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import { useTheme } from '../../context/ThemeContext';
import { ROUTES } from '../../utils/constants';
import { tokenStorage } from '../../utils/tokenStorage';

export default function Navbar({ onOpenMobileSidebar }) {
  const { isDark, toggleTheme } = useTheme();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  const storedUser = tokenStorage.getUser();
  const currentUser = {
    first_name: storedUser?.first_name || storedUser?.username || 'Student',
    role: storedUser?.role || 'student',
  };

  const handleLogout = () => {
    tokenStorage.clear();
    setMenuOpen(false);
    window.location.href = ROUTES.LOGIN;
  };

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-ink-100 dark:border-ink-800 bg-white/80 dark:bg-ink-900/80 backdrop-blur-xl px-4 lg:px-6">
      <button
        onClick={onOpenMobileSidebar}
        className="rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:hover:bg-ink-800 lg:hidden"
        aria-label="Open menu"
      >
        <Bars3Icon className="h-5 w-5" />
      </button>

      <div className="relative hidden flex-1 max-w-md md:flex">
        <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
        <input
          type="text"
          placeholder="Search courses, careers, colleges..."
          className="w-full rounded-xl border border-ink-200 dark:border-ink-700 bg-ink-50 dark:bg-ink-800 py-2 pl-9 pr-3 text-sm text-ink-800 dark:text-ink-100 placeholder:text-ink-400 focus:border-iris-400 focus:bg-white dark:focus:bg-ink-900 transition-colors"
        />
      </div>

      <div className="ml-auto flex items-center gap-1.5">
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800 transition-colors"
          aria-label="Toggle theme"
        >
          {isDark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
        </button>

        <Link
          to={ROUTES.NOTIFICATIONS}
          className="relative rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800 transition-colors"
          aria-label="Notifications"
        >
          <BellIcon className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-marigold-400 ring-2 ring-white dark:ring-ink-900" />
        </Link>

        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen((o) => !o)}
            className="flex items-center gap-2 rounded-xl py-1.5 pl-2 pr-2.5 hover:bg-ink-100 dark:hover:bg-ink-800 transition-colors"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-iris text-sm font-semibold text-white">
              {currentUser.first_name?.[0]?.toUpperCase() || 'S'}
            </div>
            <span className="hidden text-sm font-medium text-ink-700 dark:text-ink-200 sm:block">
              {currentUser.first_name}
            </span>
            <ChevronDownIcon className="hidden h-4 w-4 text-ink-400 sm:block" />
          </button>

          <AnimatePresence>
            {menuOpen && (
              <motion.div
                initial={{ opacity: 0, y: -6, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -6, scale: 0.97 }}
                transition={{ duration: 0.14 }}
                className="surface absolute right-0 mt-2 w-52 overflow-hidden p-1.5"
              >
                <Link
                  to={ROUTES.PROFILE}
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-ink-600 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800"
                >
                  <UserCircleIcon className="h-4 w-4" /> Profile
                </Link>
                <Link
                  to={ROUTES.SETTINGS}
                  onClick={() => setMenuOpen(false)}
                  className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-ink-600 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800"
                >
                  <Cog6ToothIcon className="h-4 w-4" /> Settings
                </Link>
                <div className="my-1 border-t border-ink-100 dark:border-ink-800" />
                <button
                  className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-danger-500 hover:bg-danger-50 dark:hover:bg-danger-500/10"
                  onClick={handleLogout}
                >
                  <ArrowRightOnRectangleIcon className="h-4 w-4" /> Log out
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
