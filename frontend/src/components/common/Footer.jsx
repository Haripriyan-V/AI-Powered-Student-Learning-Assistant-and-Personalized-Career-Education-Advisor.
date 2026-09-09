import { Link } from 'react-router-dom';
import Logo from './Logo';
import { ROUTES } from '../../utils/constants';

const LINK_GROUPS = [
  {
    title: 'Product',
    links: [
      { label: 'Dashboard', to: ROUTES.DASHBOARD },
      { label: 'AI Chat Assistant', to: ROUTES.CHAT },
      { label: 'Career Recommendation', to: ROUTES.CAREER },
      { label: 'Learning Roadmap', to: ROUTES.ROADMAP },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Courses', to: ROUTES.COURSES },
      { label: 'Scholarships', to: ROUTES.SCHOLARSHIPS },
      { label: 'Colleges', to: ROUTES.COLLEGES },
      { label: 'Entrance Exams', to: ROUTES.EXAMS },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About', to: ROUTES.ABOUT },
      { label: 'Contact', to: ROUTES.CONTACT },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-ink-100 dark:border-ink-800 bg-white dark:bg-ink-900">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div className="col-span-2">
            <Logo />
            <p className="mt-3 max-w-xs text-sm text-ink-500 dark:text-ink-400">
              An AI-powered learning assistant and personalized
              career &amp; education advisor for every student.
            </p>
          </div>

          {LINK_GROUPS.map((group) => (
            <div key={group.title}>
              <p className="text-sm font-semibold text-ink-800 dark:text-ink-100">{group.title}</p>
              <ul className="mt-3 space-y-2">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      to={link.to}
                      className="text-sm text-ink-500 hover:text-iris-500 dark:text-ink-400 dark:hover:text-iris-400 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-ink-100 dark:border-ink-800 pt-6 sm:flex-row">
          <p className="text-xs text-ink-400">© {new Date().getFullYear()} Disha AI</p>
          <p className="text-xs text-ink-400">Made with care for students charting their path.</p>
        </div>
      </div>
    </footer>
  );
}
