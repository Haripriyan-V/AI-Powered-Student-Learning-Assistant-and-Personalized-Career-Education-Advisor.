import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ClipboardDocumentCheckIcon, SparklesIcon } from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

export default function Exams() {
  const [quizzes, setQuizzes] = useState([]);
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get('/learning/quizzes/'),
      api.get('/learning/attempts/'),
    ])
      .then(([quizzesRes, attemptsRes]) => {
        const quizzesData = quizzesRes.data;
        setQuizzes(Array.isArray(quizzesData) ? quizzesData : quizzesData.results || []);
        const attemptsData = attemptsRes.data;
        setAttempts(Array.isArray(attemptsData) ? attemptsData : attemptsData.results || []);
      })
      .catch((err) => {
        console.error('Error fetching exams:', err);
        setError('Failed to load exams.');
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader label="Loading exams…" size="lg" />;

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50 mb-1">Entrance Exams</h1>
      <p className="text-sm text-ink-500 dark:text-ink-400 mb-6">
        Practice quizzes and entrance exams to test your knowledge.
      </p>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-900/20 dark:border-rose-800 p-4 text-sm text-rose-600 dark:text-rose-400 mb-6">
          {error}
        </div>
      )}

      {/* Available Quizzes */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50 mb-4">Available Quizzes</h2>
        {quizzes.length === 0 ? (
          <div className="text-center py-12">
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
                className="surface p-5"
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
                className="surface p-4 flex items-center justify-between"
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
  );
}
