import { motion } from 'framer-motion';
import { MapIcon } from '@heroicons/react/24/outline';

/**
 * Temporary placeholder used only during Phase 1 scaffolding so every route
 * renders something real instead of a blank screen. Each of these gets
 * replaced with its full page in the matching later phase (see Step 5/6/...).
 */
export default function ComingSoon({ title, phaseNote }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="surface flex min-h-[50vh] flex-col items-center justify-center gap-4 p-10 text-center"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-iris text-white shadow-glow">
        <MapIcon className="h-7 w-7" />
      </div>
      <div>
        <h2 className="text-xl font-semibold text-ink-900 dark:text-ink-50">{title}</h2>
        <p className="mt-1.5 max-w-sm text-sm text-ink-500 dark:text-ink-400">
          {phaseNote || 'This page is scaffolded for routing and will be fully built in its dedicated phase.'}
        </p>
      </div>
    </motion.div>
  );
}
