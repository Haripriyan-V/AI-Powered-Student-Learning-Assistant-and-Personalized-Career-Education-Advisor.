import { Link, Outlet } from 'react-router-dom';
import Logo from '../components/common/Logo';
import Footer from '../components/common/Footer';
import { useTheme } from '../context/ThemeContext';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { ROUTES } from '../utils/constants';

export default function PublicLayout() {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className="flex min-h-screen flex-col bg-white dark:bg-ink-950">
      <header className="sticky top-0 z-30 border-b border-ink-100 dark:border-ink-800 bg-white/80 dark:bg-ink-950/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link to={ROUTES.HOME}>
            <Logo />
          </Link>
          <nav className="hidden items-center gap-8 md:flex">
            <Link to={ROUTES.ABOUT} className="text-sm font-medium text-ink-600 hover:text-iris-500 dark:text-ink-300">
              About
            </Link>
            <Link to={ROUTES.CONTACT} className="text-sm font-medium text-ink-600 hover:text-iris-500 dark:text-ink-300">
              Contact
            </Link>
          </nav>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="rounded-lg p-2 text-ink-500 hover:bg-ink-100 dark:text-ink-300 dark:hover:bg-ink-800"
              aria-label="Toggle theme"
            >
              {isDark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
            </button>
            <Link to={ROUTES.LOGIN} className="btn-ghost">
              Log in
            </Link>
            <Link to={ROUTES.REGISTER} className="btn-primary">
              Get started
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}
