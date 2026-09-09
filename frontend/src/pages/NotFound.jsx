import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ROUTES } from '../utils/constants';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-white dark:bg-ink-950 px-6 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
      >
        <p className="font-display text-7xl font-semibold text-iris-500">404</p>
        <h1 className="mt-3 text-xl font-semibold text-ink-900 dark:text-ink-50">
          This path doesn&apos;t exist yet.
        </h1>
        <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">
          The page you&apos;re looking for may have moved, or the route was mistyped.
        </p>
        <Link to={ROUTES.HOME} className="btn-primary mt-6 inline-flex">
          Back to home
        </Link>
      </motion.div>
    </div>
  );
}
