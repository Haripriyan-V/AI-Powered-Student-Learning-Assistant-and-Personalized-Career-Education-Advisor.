import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  AcademicCapIcon,
  CurrencyRupeeIcon,
  CalendarDaysIcon,
  ArrowTopRightOnSquareIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

const TYPE_COLORS = {
  merit: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400',
  need: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-400',
  sports: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400',
  minority: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',
  government: 'bg-iris-100 text-iris-700 dark:bg-iris-900/40 dark:text-iris-400',
  private: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-400',
  other: 'bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ink-400',
};

function ScholarshipCard({ s }) {
  const deadlineDate = s.deadline ? new Date(s.deadline) : null;
  const isExpired = deadlineDate && deadlineDate < new Date();

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col rounded-2xl border border-ink-100 dark:border-ink-800 bg-white dark:bg-ink-900 p-5 shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Icon + type badge */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 text-white">
          <AcademicCapIcon className="h-5 w-5" />
        </div>
        <span
          className={`ml-auto shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${
            TYPE_COLORS[s.scholarship_type] || TYPE_COLORS.other
          }`}
        >
          {(s.scholarship_type || 'other').replace('_', ' ')}
        </span>
      </div>

      {/* Name & provider */}
      <h3 className="text-base font-semibold text-ink-900 dark:text-ink-50 leading-snug mb-0.5">
        {s.name}
      </h3>
      <p className="text-xs font-medium text-iris-500 mb-2">{s.provider}</p>

      {/* Description */}
      <p className="text-sm text-ink-500 dark:text-ink-400 line-clamp-3 flex-1 mb-4">
        {s.description}
      </p>

      {/* Eligibility */}
      {s.eligibility && (
        <p className="text-xs text-ink-400 dark:text-ink-500 mb-3 line-clamp-2">
          <span className="font-medium text-ink-600 dark:text-ink-300">Eligibility: </span>
          {s.eligibility}
        </p>
      )}

      {/* Footer row */}
      <div className="mt-auto pt-3 border-t border-ink-100 dark:border-ink-800 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          {s.amount && (
            <span className="flex items-center gap-1 text-xs text-ink-500 dark:text-ink-400">
              <CurrencyRupeeIcon className="h-3.5 w-3.5" />
              {Number(s.amount).toLocaleString('en-IN')} / yr
            </span>
          )}
          {deadlineDate && (
            <span
              className={`flex items-center gap-1 text-xs ${
                isExpired ? 'text-rose-500' : 'text-ink-500 dark:text-ink-400'
              }`}
            >
              <CalendarDaysIcon className="h-3.5 w-3.5" />
              {isExpired ? 'Closed' : deadlineDate.toLocaleDateString('en-IN')}
            </span>
          )}
        </div>

        {s.application_url && (
          <a
            href={s.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 rounded-lg bg-iris-50 dark:bg-iris-900/20 px-3 py-1.5 text-xs font-medium text-iris-600 dark:text-iris-400 hover:bg-iris-100 dark:hover:bg-iris-900/40 transition-colors"
          >
            Apply <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
          </a>
        )}
      </div>
    </motion.div>
  );
}

export default function Scholarships() {
  const [scholarships, setScholarships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api
      .get('/learning/scholarships/')
      .then((res) => {
        const data = res.data;
        setScholarships(Array.isArray(data) ? data : data.results || []);
      })
      .catch((err) => {
        console.error('Error fetching scholarships:', err);
        setError('Failed to load scholarships. Please try again later.');
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = scholarships.filter(
    (s) =>
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      (s.provider || '').toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 flex flex-col gap-1">
        <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50">Scholarships</h1>
        <p className="text-sm text-ink-500 dark:text-ink-400">
          Find scholarships that match your profile and apply directly.
        </p>
      </div>

      {/* Search bar */}
      <div className="relative mb-6 max-w-md">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
        <input
          type="text"
          placeholder="Search scholarships or providers…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-xl border border-ink-200 dark:border-ink-700 bg-white dark:bg-ink-900 pl-9 pr-4 py-2 text-sm text-ink-900 dark:text-ink-100 placeholder-ink-400 focus:outline-none focus:ring-2 focus:ring-iris-400"
        />
      </div>

      {/* States */}
      {loading && <Loader label="Loading scholarships…" size="lg" />}

      {!loading && error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-900/20 dark:border-rose-800 p-6 text-center text-sm text-rose-600 dark:text-rose-400">
          {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
          <AcademicCapIcon className="h-12 w-12 text-ink-300 dark:text-ink-600" />
          <p className="text-sm text-ink-500 dark:text-ink-400">
            {scholarships.length === 0
              ? 'No scholarships available yet. Check back soon!'
              : 'No scholarships match your search.'}
          </p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((s) => (
            <ScholarshipCard key={s.id} s={s} />
          ))}
        </div>
      )}
    </div>
  );
}
