import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  BuildingLibraryIcon,
  MapPinIcon,
  TrophyIcon,
  ArrowTopRightOnSquareIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

const TYPE_COLORS = {
  iit: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-400',
  nit: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400',
  iiit: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-400',
  central: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',
  state: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400',
  deemed: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-400',
  private: 'bg-iris-100 text-iris-700 dark:bg-iris-900/40 dark:text-iris-400',
  other: 'bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ink-400',
};

function CollegeCard({ college }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col rounded-2xl border border-ink-100 dark:border-ink-800 bg-white dark:bg-ink-900 p-5 shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Icon + type badge */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 text-white">
          <BuildingLibraryIcon className="h-5 w-5" />
        </div>
        <span
          className={`ml-auto shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${
            TYPE_COLORS[college.college_type] || TYPE_COLORS.other
          }`}
        >
          {college.college_type}
        </span>
      </div>

      {/* Name */}
      <h3 className="text-base font-semibold text-ink-900 dark:text-ink-50 leading-snug mb-1">
        {college.name}
      </h3>

      {/* Location */}
      {college.location && (
        <p className="flex items-center gap-1 text-xs text-iris-500 mb-2">
          <MapPinIcon className="h-3.5 w-3.5" />
          {college.location}
        </p>
      )}

      {/* Description */}
      {college.description && (
        <p className="text-sm text-ink-500 dark:text-ink-400 line-clamp-3 flex-1 mb-4">
          {college.description}
        </p>
      )}

      {/* Affiliation */}
      {college.affiliation && (
        <p className="text-xs text-ink-400 dark:text-ink-500 mb-3">
          <span className="font-medium text-ink-600 dark:text-ink-300">Affiliation: </span>
          {college.affiliation}
        </p>
      )}

      {/* Footer */}
      <div className="mt-auto pt-3 border-t border-ink-100 dark:border-ink-800 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-3">
          {college.ranking && (
            <span className="flex items-center gap-1 text-xs text-amber-600 dark:text-amber-400">
              <TrophyIcon className="h-3.5 w-3.5" />
              NIRF #{college.ranking}
            </span>
          )}
          {college.established_year && (
            <span className="text-xs text-ink-400 dark:text-ink-500">
              Est. {college.established_year}
            </span>
          )}
        </div>

        {college.website && (
          <a
            href={college.website}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 rounded-lg bg-iris-50 dark:bg-iris-900/20 px-3 py-1.5 text-xs font-medium text-iris-600 dark:text-iris-400 hover:bg-iris-100 dark:hover:bg-iris-900/40 transition-colors"
          >
            Visit <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
          </a>
        )}
      </div>
    </motion.div>
  );
}

export default function Colleges() {
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api
      .get('/learning/colleges/')
      .then((res) => {
        const data = res.data;
        setColleges(Array.isArray(data) ? data : data.results || []);
      })
      .catch((err) => {
        console.error('Error fetching colleges:', err);
        setError('Failed to load colleges. Please try again later.');
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = colleges.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      (c.location || '').toLowerCase().includes(search.toLowerCase()) ||
      (c.affiliation || '').toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 flex flex-col gap-1">
        <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50">Colleges</h1>
        <p className="text-sm text-ink-500 dark:text-ink-400">
          Explore colleges and universities across India to find your best fit.
        </p>
      </div>

      {/* Search bar */}
      <div className="relative mb-6 max-w-md">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
        <input
          type="text"
          placeholder="Search colleges, cities, or affiliations…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-xl border border-ink-200 dark:border-ink-700 bg-white dark:bg-ink-900 pl-9 pr-4 py-2 text-sm text-ink-900 dark:text-ink-100 placeholder-ink-400 focus:outline-none focus:ring-2 focus:ring-iris-400"
        />
      </div>

      {/* States */}
      {loading && <Loader label="Loading colleges…" size="lg" />}

      {!loading && error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-900/20 dark:border-rose-800 p-6 text-center text-sm text-rose-600 dark:text-rose-400">
          {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
          <BuildingLibraryIcon className="h-12 w-12 text-ink-300 dark:text-ink-600" />
          <p className="text-sm text-ink-500 dark:text-ink-400">
            {colleges.length === 0
              ? 'No colleges listed yet. Check back soon!'
              : 'No colleges match your search.'}
          </p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((college) => (
            <CollegeCard key={college.id} college={college} />
          ))}
        </div>
      )}
    </div>
  );
}
