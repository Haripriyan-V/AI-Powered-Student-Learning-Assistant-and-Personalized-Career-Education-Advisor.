import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  PlayCircleIcon,
  DocumentTextIcon,
  LinkIcon,
  DocumentArrowDownIcon,
  MagnifyingGlassIcon,
  FolderOpenIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

const RESOURCE_ICONS = {
  video: PlayCircleIcon,
  article: DocumentTextIcon,
  pdf: DocumentArrowDownIcon,
  link: LinkIcon,
};

const RESOURCE_COLORS = {
  video: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-400',
  article: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400',
  pdf: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',
  link: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400',
};

const ICON_BG = {
  video: 'from-rose-500 to-pink-600',
  article: 'from-blue-500 to-cyan-600',
  pdf: 'from-amber-500 to-orange-600',
  link: 'from-emerald-500 to-teal-600',
};

function ResourceCard({ resource }) {
  const Icon = RESOURCE_ICONS[resource.resource_type] || LinkIcon;
  const colorClass = RESOURCE_COLORS[resource.resource_type] || RESOURCE_COLORS.link;
  const iconBg = ICON_BG[resource.resource_type] || ICON_BG.link;

  const target = resource.url || resource.file;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col rounded-2xl border border-ink-100 dark:border-ink-800 bg-white dark:bg-ink-900 p-5 shadow-sm hover:shadow-md transition-shadow"
    >
      {/* Icon + type badge */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${iconBg} text-white`}
        >
          <Icon className="h-5 w-5" />
        </div>
        <span className={`ml-auto shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${colorClass}`}>
          {resource.resource_type}
        </span>
      </div>

      {/* Title */}
      <h3 className="text-base font-semibold text-ink-900 dark:text-ink-50 leading-snug mb-0.5">
        {resource.title}
      </h3>

      {/* Course */}
      <p className="text-xs font-medium text-iris-500 mb-2">
        {resource.course_title || `Course #${resource.course}`}
      </p>

      {/* Content preview */}
      {resource.content && (
        <p className="text-sm text-ink-500 dark:text-ink-400 line-clamp-3 flex-1 mb-4">
          {resource.content}
        </p>
      )}

      {/* Link / open button */}
      {target && (
        <div className="mt-auto pt-3 border-t border-ink-100 dark:border-ink-800">
          <a
            href={target}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 rounded-xl bg-iris-50 dark:bg-iris-900/20 px-4 py-2 text-xs font-medium text-iris-600 dark:text-iris-400 hover:bg-iris-100 dark:hover:bg-iris-900/40 transition-colors"
          >
            <Icon className="h-4 w-4" />
            {resource.resource_type === 'pdf' ? 'Download PDF' : 'Open Resource'}
          </a>
        </div>
      )}
    </motion.div>
  );
}

export default function Resources() {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [activeType, setActiveType] = useState('all');

  useEffect(() => {
    api
      .get('/learning/resources/')
      .then((res) => {
        const data = res.data;
        setResources(Array.isArray(data) ? data : data.results || []);
      })
      .catch((err) => {
        console.error('Error fetching resources:', err);
        setError('Failed to load resources. Please try again later.');
      })
      .finally(() => setLoading(false));
  }, []);

  const types = ['all', ...new Set(resources.map((r) => r.resource_type))];

  const filtered = resources.filter((r) => {
    const matchType = activeType === 'all' || r.resource_type === activeType;
    const matchSearch =
      r.title.toLowerCase().includes(search.toLowerCase()) ||
      (r.course_title || '').toLowerCase().includes(search.toLowerCase());
    return matchType && matchSearch;
  });

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 flex flex-col gap-1">
        <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50">Learning Resources</h1>
        <p className="text-sm text-ink-500 dark:text-ink-400">
          Videos, articles, PDFs, and links curated for your learning journey.
        </p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-3">
        {/* Search bar */}
        <div className="relative flex-1 max-w-md">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-400" />
          <input
            type="text"
            placeholder="Search resources or courses…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-ink-200 dark:border-ink-700 bg-white dark:bg-ink-900 pl-9 pr-4 py-2 text-sm text-ink-900 dark:text-ink-100 placeholder-ink-400 focus:outline-none focus:ring-2 focus:ring-iris-400"
          />
        </div>

        {/* Type filter pills */}
        <div className="flex flex-wrap gap-2">
          {types.map((t) => (
            <button
              key={t}
              onClick={() => setActiveType(t)}
              className={`rounded-full px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
                activeType === t
                  ? 'bg-iris-500 text-white shadow-sm'
                  : 'bg-ink-100 dark:bg-ink-800 text-ink-600 dark:text-ink-300 hover:bg-ink-200 dark:hover:bg-ink-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* States */}
      {loading && <Loader label="Loading resources…" size="lg" />}

      {!loading && error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-900/20 dark:border-rose-800 p-6 text-center text-sm text-rose-600 dark:text-rose-400">
          {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
          <FolderOpenIcon className="h-12 w-12 text-ink-300 dark:text-ink-600" />
          <p className="text-sm text-ink-500 dark:text-ink-400">
            {resources.length === 0
              ? 'No resources available yet.'
              : 'No resources match your filters.'}
          </p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((r) => (
            <ResourceCard key={r.id} resource={r} />
          ))}
        </div>
      )}
    </div>
  );
}
