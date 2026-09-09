import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { CheckCircleIcon, ClipboardDocumentCheckIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';
import { ROUTES } from '../../utils/constants';

export default function SkillAssessment() {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [validationError, setValidationError] = useState(null);

  useEffect(() => {
    api
      .get('/career/tests/')
      .then((res) => {
        const testsData = res.data;
        const list = Array.isArray(testsData) ? testsData : testsData.results || [];
        setTests(list);
      })
      .catch((err) => console.error('Error fetching tests:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectTest = (test) => {
    setSelectedTest(test);
    setAnswers({});
    setResult(null);
    setValidationError(null);
  };

  const handleAnswerChange = (questionId, optionId) => {
    setAnswers({ ...answers, [questionId]: optionId });
    if (validationError) setValidationError(null);
  };

  const handleSubmit = async () => {
    if (!selectedTest) return;
    
    const totalQuestions = selectedTest.questions?.length || 0;
    const answeredCount = Object.keys(answers).length;
    if (answeredCount < totalQuestions) {
      setValidationError('Please answer all questions before submitting.');
      return;
    }

    setSubmitting(true);
    setValidationError(null);
    try {
      const res = await api.post(`/career/tests/${selectedTest.id}/submit/`, { answers });
      setResult(res.data);
    } catch (err) {
      console.error('Error submitting test:', err);
      const errMsg = err?.response?.data?.error || 'Failed to submit assessment. Please try again.';
      setValidationError(errMsg);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Loader label="Loading assessments…" size="lg" />;

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50 mb-1">Skill Assessment</h1>
      <p className="text-sm text-ink-500 dark:text-ink-400 mb-6">
        Take assessments to discover your strengths and get personalized career recommendations.
      </p>

      {result ? (
        // Results View
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
          <div className="surface p-8 text-center mb-6">
            <CheckCircleIcon className="h-12 w-12 text-growth-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-ink-900 dark:text-ink-50 mb-2">Assessment Completed!</h2>
            <p className="text-ink-500 dark:text-ink-400 mb-6">
              Your assessment has been analyzed. Here are your personalized career recommendations:
            </p>

            {result.recommendations && result.recommendations.length > 0 && (
              <div className="space-y-4 mb-6">
                {result.recommendations.map((rec, idx) => {
                  const title = rec.career || rec.career_path_title || rec.title || 'Career Path';
                  const field = rec.career_field_name || rec.career_path_career_field_name || '';
                  const matchScore = Number(rec.match_score ?? rec.score ?? 70);
                  const reasoning = rec.reasoning || rec.reason || '';

                  return (
                    <div key={rec.id || idx} className="surface p-4 text-left">
                      <h3 className="font-semibold text-ink-900 dark:text-ink-50 mb-1">{title}</h3>
                      {field && <p className="text-xs text-iris-500 mb-2">{field}</p>}
                      <p className="text-sm text-ink-500 dark:text-ink-400 mb-3">{reasoning}</p>
                      <div className="w-full bg-ink-200 dark:bg-ink-700 rounded-full h-2">
                        <div
                          className="bg-iris-500 h-2 rounded-full"
                          style={{ width: `${matchScore}%` }}
                        />
                      </div>
                      <p className="text-xs text-ink-400 text-right mt-2">{matchScore}% Match</p>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => navigate(ROUTES.CAREER)}
                className="btn-primary"
              >
                View Career Recommendations
              </button>
              <button
                onClick={() => {
                  setResult(null);
                  setSelectedTest(null);
                }}
                className="btn-secondary"
              >
                Back to Assessments
              </button>
            </div>
          </div>
        </motion.div>
      ) : selectedTest ? (
        // Test Taking View
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
          <div className="surface p-6 mb-6">
            <h2 className="text-xl font-semibold text-ink-900 dark:text-ink-50 mb-1">{selectedTest.title}</h2>
            <p className="text-ink-500 dark:text-ink-400">{selectedTest.description}</p>
          </div>

          {validationError && (
            <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-700 text-sm mb-6 flex items-center gap-2">
              <ExclamationTriangleIcon className="h-5 w-5 shrink-0" />
              <span>{validationError}</span>
            </div>
          )}

          <div className="space-y-6 mb-8">
            {selectedTest.questions?.map((question, idx) => (
              <div key={question.id} className="surface p-6">
                <p className="font-semibold text-ink-900 dark:text-ink-50 mb-4">
                  {idx + 1}. {question.text}
                </p>
                <div className="space-y-2">
                  {question.options?.map((option) => (
                    <label key={option.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-ink-50 dark:hover:bg-ink-800 cursor-pointer transition-colors">
                      <input
                        type="radio"
                        name={`question-${question.id}`}
                        value={option.id}
                        checked={answers[question.id] === option.id}
                        onChange={() => handleAnswerChange(question.id, option.id)}
                        className="w-4 h-4"
                      />
                      <span className="text-sm">{option.text}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setSelectedTest(null)}
              className="btn-secondary flex-1"
            >
              Back
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting || !Object.keys(answers).length}
              className="btn-primary flex-1"
            >
              {submitting ? 'Submitting…' : 'Submit Assessment'}
            </button>
          </div>
        </motion.div>
      ) : (
        // Test Selection View
        <div className="space-y-4">
          {tests.length === 0 ? (
            <div className="text-center py-12">
              <ClipboardDocumentCheckIcon className="h-12 w-12 text-ink-300 dark:text-ink-600 mx-auto mb-3" />
              <p className="text-ink-500 dark:text-ink-400">No assessments available yet.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tests.map((test) => (
                <motion.button
                  key={test.id}
                  onClick={() => handleSelectTest(test)}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ y: -4 }}
                  className="surface p-6 text-left hover:shadow-md transition-shadow"
                >
                  <h3 className="font-semibold text-ink-900 dark:text-ink-50 mb-2">{test.title}</h3>
                  <p className="text-sm text-ink-500 dark:text-ink-400 mb-3 line-clamp-2">
                    {test.description}
                  </p>
                  <p className="text-xs text-iris-500 font-medium">
                    {test.questions?.length || 0} questions
                  </p>
                </motion.button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
