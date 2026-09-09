import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  BookOpenIcon,
  ClockIcon,
  AcademicCapIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

const LEVEL_COLORS = {
  beginner: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400',
  intermediate: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',
  advanced: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-400',
};

function CourseCard({ course }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col rounded-2xl border border-ink-100 dark:border-ink-800 bg-white dark:bg-ink-900 p-5 shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-iris-500 to-violet-600 text-white">
          <BookOpenIcon className="h-5 w-5" />
        </div>
        <span
          className={`ml-auto shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${
            LEVEL_COLORS[course.level] || 'bg-ink-100 text-ink-600'
          }`}
        >
          {course.level}
        </span>
      </div>

      {/* Title & subject */}
      <h3 className="text-base font-semibold text-ink-900 dark:text-ink-50 leading-snug mb-1">
        {course.title}
      </h3>
      <p className="text-xs font-medium text-iris-500 mb-2">{course.subject_name}</p>

      {/* Description */}
      <p className="text-sm text-ink-500 dark:text-ink-400 line-clamp-3 flex-1 mb-4">
        {course.description}
      </p>

      {/* Footer */}
      <div className="flex items-center gap-3 mt-auto pt-3 border-t border-ink-100 dark:border-ink-800">
        <ClockIcon className="h-4 w-4 text-ink-400" />
        <span className="text-xs text-ink-500 dark:text-ink-400">
          {course.duration_hours} {course.duration_hours === 1 ? 'hour' : 'hours'}
        </span>
      </div>
    </motion.div>
  );
}

export default function Courses() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    api
      .get('/learning/courses/')
      .then((res) => {
        // Handle both paginated ({results: []}) and plain array responses
        const data = res.data;
        setCourses(Array.isArray(data) ? data : data.results || []);
      })
      .catch((err) => {
        console.error('Error fetching courses:', err);
        setError('Failed to load courses. Please try again later.');
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = courses.filter(
    (c) =>
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      (c.subject_name || '').toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 flex flex-col gap-1">
        <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50">Courses</h1>
        <p className="text-sm text-ink-500 dark:text-ink-400">
          Browse the full course catalog and start learning today.
        </p>
      </div>

      {/* Search bar */}
      <div className="relative mb-6 max-w-md">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
        <input
          type="text"
          placeholder="Search courses or subjects…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-xl border border-ink-200 dark:border-ink-700 bg-white dark:bg-ink-900 pl-9 pr-4 py-2 text-sm text-ink-900 dark:text-ink-100 placeholder-ink-400 focus:outline-none focus:ring-2 focus:ring-iris-400"
        />
      </div>

      {/* States */}
      {loading && <Loader label="Loading courses…" size="lg" />}

      {!loading && error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-900/20 dark:border-rose-800 p-6 text-center text-sm text-rose-600 dark:text-rose-400">
          {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
          <AcademicCapIcon className="h-12 w-12 text-ink-300 dark:text-ink-600" />
          <p className="text-sm text-ink-500 dark:text-ink-400">
            {courses.length === 0 ? 'No courses available yet.' : 'No courses match your search.'}
          </p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </div>
  );
}
