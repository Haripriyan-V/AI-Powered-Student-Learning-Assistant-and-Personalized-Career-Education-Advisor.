import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ClipboardDocumentCheckIcon,
  SparklesIcon,
  AcademicCapIcon,
  CalendarDaysIcon,
  BuildingLibraryIcon,
  ArrowTopRightOnSquareIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

const CATEGORY_COLORS = {
  engineering: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400',
  medical: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400',
  management: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-400',
  sciences: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400',
  civil_services: 'bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-400',
  law: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-400',
  other: 'bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ink-400',
};

export default function Exams() {
  const [activeTab, setActiveTab] = useState('entrance_exams'); // 'entrance_exams' | 'quizzes'
  const [entranceExams, setEntranceExams] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [attempts, setAttempts] = useState([]);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get('/learning/entrance-exams/'),
      api.get('/learning/quizzes/'),
      api.get('/learning/attempts/'),
    ])
      .then(([examsRes, quizzesRes, attemptsRes]) => {
        const examsData = examsRes.data;
        setEntranceExams(Array.isArray(examsData) ? examsData : examsData.results || []);
        const quizzesData = quizzesRes.data;
        setQuizzes(Array.isArray(quizzesData) ? quizzesData : quizzesData.results || []);
        const attemptsData = attemptsRes.data;
        setAttempts(Array.isArray(attemptsData) ? attemptsData : attemptsData.results || []);
      })
      .catch((err) => {
        console.error('Error fetching exams:', err);
        setError('Failed to load entrance exams and quizzes.');
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredExams = entranceExams.filter((exam) => {
    const matchesSearch =
      exam.name.toLowerCase().includes(search.toLowerCase()) ||
      (exam.conducting_body || '').toLowerCase().includes(search.toLowerCase()) ||
      (exam.syllabus_summary || '').toLowerCase().includes(search.toLowerCase());
    const matchesCat = categoryFilter === 'all' || exam.exam_category === categoryFilter;
    return matchesSearch && matchesCat;
  });

  if (loading) return <Loader label="Loading entrance exams & quizzes…" size="lg" />;

  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-iris-500/10 text-iris-600 dark:text-iris-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <SparklesIcon className="h-4 w-4" />
          Examinations & Assessments
        </div>
        <h1 className="text-2xl lg:text-3xl font-bold text-ink-900 dark:text-ink-50 mb-1">
          Entrance Exams & Assessments
        </h1>
        <p className="text-sm text-ink-600 dark:text-ink-400">
          Explore key national and state entrance exams with verified official portals, eligibility, patterns, and practice test modules.
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-900/20 dark:border-rose-800 p-4 text-sm text-rose-600 dark:text-rose-400">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-ink-100 dark:border-ink-800 gap-2">
        <button
          onClick={() => setActiveTab('entrance_exams')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'entrance_exams'
              ? 'border-iris-600 text-iris-600 dark:border-iris-400 dark:text-iris-400'
              : 'border-transparent text-ink-500 hover:text-ink-900 dark:text-ink-400 dark:hover:text-ink-200'
          }`}
        >
          <BuildingLibraryIcon className="h-4 w-4" />
          <span>National Entrance Exams ({entranceExams.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('quizzes')}
          className={`pb-3 px-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'quizzes'
              ? 'border-iris-600 text-iris-600 dark:border-iris-400 dark:text-iris-400'
              : 'border-transparent text-ink-500 hover:text-ink-900 dark:text-ink-400 dark:hover:text-ink-200'
          }`}
        >
          <ClipboardDocumentCheckIcon className="h-4 w-4" />
          <span>Practice Quizzes ({quizzes.length})</span>
        </button>
      </div>

      {/* Tab 1: Entrance Exams */}
      {activeTab === 'entrance_exams' && (
        <div className="space-y-6">
          {/* Filters & Search */}
          <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
            <div className="relative w-full sm:w-72">
              <MagnifyingGlassIcon className="h-4 w-4 text-ink-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search exams, conducting body..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-field pl-9 w-full text-sm"
              />
            </div>
            <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-1">
              {['all', 'engineering', 'medical', 'management', 'sciences'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setCategoryFilter(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize whitespace-nowrap transition-colors ${
                    categoryFilter === cat
                      ? 'bg-iris-600 text-white dark:bg-iris-500'
                      : 'bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ink-300 hover:bg-ink-200 dark:hover:bg-ink-700'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {filteredExams.length === 0 ? (
            <div className="text-center py-12 surface p-8 rounded-2xl">
              <AcademicCapIcon className="h-12 w-12 text-ink-300 dark:text-ink-600 mx-auto mb-3" />
              <p className="text-ink-500 dark:text-ink-400">No entrance exams matched your filter.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {filteredExams.map((exam) => (
                <motion.div
                  key={exam.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="surface p-5 rounded-2xl flex flex-col justify-between border border-ink-100 dark:border-ink-800"
                >
                  <div>
                    {/* Header */}
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div>
                        <h3 className="text-base font-bold text-ink-900 dark:text-ink-50 leading-snug">
                          {exam.name}
                        </h3>
                        <p className="text-xs font-semibold text-iris-600 dark:text-iris-400">
                          {exam.conducting_body}
                        </p>
                      </div>
                      <span
                        className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${
                          CATEGORY_COLORS[exam.exam_category] || CATEGORY_COLORS.other
                        }`}
                      >
                        {exam.exam_category}
                      </span>
                    </div>

                    {/* Eligibility */}
                    {exam.eligibility && (
                      <p className="text-xs text-ink-600 dark:text-ink-400 mb-2.5 line-clamp-2">
                        <span className="font-semibold text-ink-800 dark:text-ink-200">Eligibility: </span>
                        {exam.eligibility}
                      </p>
                    )}

                    {/* Timeline & Reference Date */}
                    <div className="space-y-1 text-xs text-ink-500 dark:text-ink-400 mb-3 bg-ink-50 dark:bg-ink-800/40 p-2.5 rounded-xl">
                      {exam.application_period && (
                        <div className="flex items-center gap-1.5">
                          <CalendarDaysIcon className="h-3.5 w-3.5 text-iris-500 shrink-0" />
                          <span><strong>Application:</strong> {exam.application_period}</span>
                        </div>
                      )}
                      {exam.exam_date_reference && (
                        <div className="flex items-center gap-1.5">
                          <BookOpenIcon className="h-3.5 w-3.5 text-iris-500 shrink-0" />
                          <span><strong>Exam Window:</strong> {exam.exam_date_reference}</span>
                        </div>
                      )}
                    </div>

                    {/* Pattern Summary */}
                    {exam.exam_pattern && (
                      <p className="text-xs text-ink-500 dark:text-ink-400 mb-3 line-clamp-2">
                        <strong>Pattern:</strong> {exam.exam_pattern}
                      </p>
                    )}
                  </div>

                  {/* Actions / Official Links */}
                  <div className="pt-3 border-t border-ink-100 dark:border-ink-800 flex items-center justify-between gap-3">
                    {exam.official_website && (
                      <a
                        href={exam.official_website}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-xs font-semibold text-iris-600 dark:text-iris-400 hover:underline"
                      >
                        <span>Official Website</span>
                        <ArrowTopRightOnSquareIcon className="h-3.5 w-3.5" />
                      </a>
                    )}
                    {exam.registration_url && (
                      <a
                        href={exam.registration_url}
                        target="_blank"
                        rel="noreferrer"
                        className="btn-primary text-xs py-1.5 px-3"
                      >
                        <span>Portal & Registration</span>
                      </a>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Quizzes & Attempts */}
      {activeTab === 'quizzes' && (
        <div className="space-y-8">
          {/* Available Quizzes */}
          <div>
            <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50 mb-4">Available Quizzes</h2>
            {quizzes.length === 0 ? (
              <div className="text-center py-12 surface p-8 rounded-2xl">
                <ClipboardDocumentCheckIcon className="h-12 w-12 text-ink-300 dark:text-ink-600 mx-auto mb-3" />
                <p className="text-ink-500 dark:text-ink-400">No quizzes available yet.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {quizzes.map((quiz) => (
                  <motion.div
                    key={quiz.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="surface p-5 rounded-2xl"
                  >
                    <h3 className="font-semibold text-ink-900 dark:text-ink-50 mb-2">{quiz.title}</h3>
                    {quiz.description && (
                      <p className="text-sm text-ink-500 dark:text-ink-400 mb-3 line-clamp-2">
                        {quiz.description}
                      </p>
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-ink-400">
                        {quiz.questions?.length || 0} questions • Pass: {quiz.passing_score}%
                      </span>
                      <button className="btn-primary text-sm">
                        Take Quiz
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>

          {/* Attempts History */}
          {attempts.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50 mb-4">Your Attempts</h2>
              <div className="space-y-3">
                {attempts.slice(0, 10).map((attempt) => (
                  <motion.div
                    key={attempt.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="surface p-4 rounded-xl flex items-center justify-between"
                  >
                    <div>
                      <p className="font-semibold text-ink-900 dark:text-ink-50">{attempt.quiz_title}</p>
                      <p className="text-xs text-ink-400 dark:text-ink-500">
                        Attempted on {new Date(attempt.completed_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-iris-600 dark:text-iris-400">
                        {attempt.score}%
                      </p>
                      <p className={`text-xs font-medium ${attempt.passed ? 'text-growth-600' : 'text-rose-600'}`}>
                        {attempt.passed ? 'Passed' : 'Not Passed'}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
