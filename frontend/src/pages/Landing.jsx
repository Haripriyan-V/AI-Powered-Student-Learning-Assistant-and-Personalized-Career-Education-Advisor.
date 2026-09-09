import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ROUTES } from '../utils/constants';

export default function Landing() {
  return (
    <section className="relative overflow-hidden">
      <div className="mx-auto max-w-7xl px-6 py-24 lg:py-32">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-2xl"
        >
          <span className="badge bg-iris-50 text-iris-600 dark:bg-iris-500/10 dark:text-iris-300">
            AI-Powered Career & Education Platform
          </span>
          <h1 className="mt-5 font-display text-4xl font-semibold leading-tight text-ink-900 dark:text-ink-50 sm:text-5xl">
            Find your <span className="text-iris-500">direction</span>, one milestone at a time.
          </h1>
          <p className="mt-5 text-lg text-ink-500 dark:text-ink-400">
            Disha AI is your personal learning assistant and career advisor —
            charting a clear path from where you are to where you want to be.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to={ROUTES.REGISTER} className="btn-primary px-6 py-3 text-base">
              Get started — it&apos;s free
            </Link>
            <Link to={ROUTES.ABOUT} className="btn-secondary px-6 py-3 text-base">
              Learn more
            </Link>
          </div>
        </motion.div>
      </div>

      <p className="border-t border-ink-100 dark:border-ink-800 py-4 text-center text-xs text-ink-400">
        Full landing experience — hero, feature trail, and testimonials — arrives in Phase 2.
      </p>
    </section>
  );
}
