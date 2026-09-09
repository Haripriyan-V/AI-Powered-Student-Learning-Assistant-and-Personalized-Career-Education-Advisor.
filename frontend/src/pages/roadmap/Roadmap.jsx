import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  SparklesIcon,
  AcademicCapIcon,
  BookOpenIcon,
  PlayCircleIcon,
  DocumentTextIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';
import { ROUTES } from '../../utils/constants';

export default function Roadmap() {
  const navigate = useNavigate();
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [completingId, setCompletingId] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const fetchRoadmap = async (force = false) => {
    if (force) setRegenerating(true);
    else setLoading(true);
    setError(null);
    try {
      const endpoint = force ? '/learning/roadmap/generate/' : '/learning/roadmap/';
      const res = force ? await api.post(endpoint) : await api.get(endpoint);
      setRoadmap(res.data);
      // Auto expand first in-progress item
      const firstActive = res.data?.phases?.flatMap((p) => p.items)?.find((i) => i.status === 'in_progress');
      if (firstActive) setExpandedId(firstActive.id);
    } catch (err) {
      console.error('Error loading roadmap:', err);
      setError('Could not load your personalized learning roadmap.');
    } finally {
      setLoading(false);
      setRegenerating(false);
    }
  };

  const handleCompleteItem = async (itemId) => {
    setCompletingId(itemId);
    try {
      const res = await api.post(`/learning/roadmap/items/${itemId}/complete/`);
      setFeedback(res.data);
      setRoadmap(res.data.roadmap);
      setTimeout(() => setFeedback(null), 6000);
    } catch (err) {
      console.error('Error completing item:', err);
    } finally {
      setCompletingId(null);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (loading) return <Loader label="Generating your personalized, gap-targeted roadmap…" size="lg" />;

  const phases = roadmap?.phases || [];
  const totalItems = roadmap?.total_items || 0;
  const completedItems = roadmap?.completed_items || 0;
  const progressPercent = roadmap?.overall_progress || 0;

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="surface p-6 lg:p-8 relative overflow-hidden bg-gradient-to-br from-iris-500/10 via-transparent to-growth-500/5">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-iris-500/10 text-iris-600 dark:text-iris-400 text-xs font-semibold uppercase tracking-wider">
              <SparklesIcon className="h-4 w-4" />
              Dynamic Adaptive Learning
            </div>
            <h1 className="text-2xl lg:text-3xl font-bold text-ink-900 dark:text-ink-50">
              {roadmap?.title || 'Personalized Learning Roadmap'}
            </h1>
            <p className="text-sm text-ink-600 dark:text-ink-300">
              Tailored learning path specifically constructed to bridge your active skill gaps. Completing tasks automatically increases skill proficiencies, awards XP, and recalculates your career readiness.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={() => fetchRoadmap(true)}
              disabled={regenerating}
              className="btn-secondary flex items-center gap-2 py-2 px-4"
              title="Regenerate learning path using latest skill gap priorities"
            >
              <ArrowPathIcon className={`h-4 w-4 ${regenerating ? 'animate-spin text-iris-500' : ''}`} />
              <span>{regenerating ? 'Regenerating…' : 'Regenerate Path'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Live XP and Gap Recalculation Feedback Toast */}
      {feedback && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-xl border border-growth-300 bg-growth-50 dark:bg-growth-950/40 text-growth-900 dark:text-growth-200 text-sm flex items-center justify-between gap-4 shadow-sm"
        >
          <div className="flex items-center gap-3">
            <CheckCircleIcon className="h-6 w-6 text-growth-600 shrink-0" />
            <div>
              <p className="font-bold">{feedback.message}</p>
              <p className="text-xs text-growth-700 dark:text-growth-300 mt-0.5">
                +15% proficiency in <span className="font-semibold">{feedback.skill_updated}</span> • +{feedback.xp_earned} XP awarded • Career Readiness: <span className="font-semibold">{feedback.career_readiness}%</span>!
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate(ROUTES.SKILL_GAP)}
            className="text-xs font-bold text-growth-700 underline flex items-center gap-1 shrink-0"
          >
            <span>View Skill Gap</span>
            <ArrowRightIcon className="h-3.5 w-3.5" />
          </button>
        </motion.div>
      )}

      {error && (
        <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-700 text-sm">
          {error}
        </div>
      )}

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="surface p-5 border-l-4 border-l-iris-500">
          <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">
            Overall Roadmap Progress
          </p>
          <p className="text-3xl font-extrabold text-iris-600 dark:text-iris-400">{progressPercent}%</p>
          <div className="w-full bg-ink-200 dark:bg-ink-800 rounded-full h-2 mt-3">
            <div className="bg-iris-500 h-2 rounded-full transition-all duration-700" style={{ width: `${progressPercent}%` }} />
          </div>
        </div>

        <div className="surface p-5 border-l-4 border-l-growth-500">
          <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">
            Milestones Completed
          </p>
          <p className="text-3xl font-extrabold text-growth-600 dark:text-growth-400">
            {completedItems} / {totalItems}
          </p>
          <p className="text-xs text-ink-500 mt-2">Verified skill steps finished</p>
        </div>

        <div className="surface p-5 border-l-4 border-l-cyan-500">
          <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">
            Active Phase
          </p>
          <p className="text-3xl font-extrabold text-cyan-600 dark:text-cyan-400">
            Phase {roadmap?.active_phase || 1}
          </p>
          <p className="text-xs text-ink-500 mt-2">In structured progression</p>
        </div>

        <div className="surface p-5 border-l-4 border-l-marigold-500 flex flex-col justify-between">
          <div>
            <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">
              Target Career Role
            </p>
            <p className="text-base font-bold text-ink-900 dark:text-ink-50 truncate">
              {roadmap?.career_path_title || 'Software / AI'}
            </p>
          </div>
          <button
            onClick={() => navigate(ROUTES.SKILL_GAP)}
            className="text-xs text-iris-600 dark:text-iris-400 font-semibold hover:underline flex items-center gap-1 mt-2"
          >
            <span>Analyze Skill Gaps</span>
            <ArrowRightIcon className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* Phased Roadmap Timeline */}
      <div className="space-y-8">
        {phases.map((phase) => {
          const isPhaseActive = phase.phase_number === roadmap?.active_phase;

          return (
            <div key={phase.phase_number} className="space-y-4">
              {/* Phase Title Badge */}
              <div className="flex items-center gap-3">
                <span className={`flex h-8 w-8 items-center justify-center rounded-xl font-bold text-xs ${
                  isPhaseActive
                    ? 'bg-iris-500 text-white shadow-md shadow-iris-500/30'
                    : 'bg-ink-200 dark:bg-ink-800 text-ink-700 dark:text-ink-300'
                }`}>
                  P{phase.phase_number}
                </span>
                <div>
                  <h2 className="text-lg font-bold text-ink-900 dark:text-ink-50">
                    Phase {phase.phase_number}: {phase.phase_title}
                  </h2>
                  <p className="text-xs text-ink-500">
                    {phase.items?.filter((i) => i.status === 'completed').length} of {phase.items?.length} milestones completed
                  </p>
                </div>
              </div>

              {/* Items in this Phase */}
              <div className="space-y-3 pl-4 border-l-2 border-ink-200 dark:border-ink-800 ml-4">
                {phase.items?.map((item) => {
                  const isCompleted = item.status === 'completed';
                  const isInProgress = item.status === 'in_progress';
                  const isExpanded = expandedId === item.id;

                  return (
                    <div
                      key={item.id}
                      className={`surface p-5 transition-all ${
                        isInProgress
                          ? 'ring-2 ring-iris-500/80 bg-iris-50/20 dark:bg-iris-950/20 shadow-sm'
                          : isCompleted
                          ? 'opacity-85 border-growth-200 dark:border-growth-900/30'
                          : 'opacity-70 hover:opacity-100'
                      }`}
                    >
                      {/* Top Header Row */}
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-start gap-3.5 flex-1 cursor-pointer" onClick={() => toggleExpand(item.id)}>
                          <div className="mt-0.5 shrink-0">
                            {isCompleted ? (
                              <CheckCircleIcon className="h-6 w-6 text-growth-500" />
                            ) : isInProgress ? (
                              <div className="h-6 w-6 rounded-full border-2 border-iris-500 flex items-center justify-center bg-iris-500/10">
                                <span className="h-2 w-2 rounded-full bg-iris-500 animate-pulse" />
                              </div>
                            ) : (
                              <div className="h-6 w-6 rounded-full border-2 border-ink-300 dark:border-ink-700" />
                            )}
                          </div>

                          <div>
                            <div className="flex flex-wrap items-center gap-2">
                              <h3 className={`font-semibold text-sm ${isCompleted ? 'text-ink-500 line-through' : 'text-ink-900 dark:text-ink-50'}`}>
                                {item.title}
                              </h3>
                              {item.skill_name && (
                                <span className="text-[11px] px-2 py-0.5 rounded-full font-medium bg-iris-500/10 text-iris-600 dark:text-iris-400">
                                  {item.skill_name}
                                </span>
                              )}
                              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-ink-100 dark:bg-ink-800 text-ink-500">
                                {item.difficulty}
                              </span>
                            </div>

                            <p className="text-xs text-ink-500 mt-1 line-clamp-1">
                              {item.description}
                            </p>
                          </div>
                        </div>

                        {/* Action buttons on header */}
                        <div className="flex items-center gap-2 shrink-0">
                          {isInProgress && (
                            <button
                              onClick={() => handleCompleteItem(item.id)}
                              disabled={completingId === item.id}
                              className="btn-primary py-1.5 px-3 text-xs flex items-center gap-1.5 font-semibold"
                            >
                              <CheckIcon className="h-3.5 w-3.5" />
                              <span>{completingId === item.id ? 'Updating…' : 'Mark Done'}</span>
                            </button>
                          )}

                          <button
                            onClick={() => toggleExpand(item.id)}
                            className="p-1 rounded-lg text-ink-400 hover:bg-ink-100 dark:hover:bg-ink-800"
                            aria-label="Toggle details"
                          >
                            {isExpanded ? <ChevronUpIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
                          </button>
                        </div>
                      </div>

                      {/* Expandable Details */}
                      {isExpanded && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="mt-4 pt-4 border-t border-ink-100 dark:border-ink-800/80 space-y-4 text-xs"
                        >
                          <p className="text-ink-600 dark:text-ink-300 leading-relaxed">
                            {item.description}
                          </p>

                          {/* Practice Tasks */}
                          {item.practice_tasks && item.practice_tasks.length > 0 && (
                            <div className="p-3 rounded-xl bg-ink-50 dark:bg-ink-900/40 border border-ink-100 dark:border-ink-800">
                              <p className="font-bold text-ink-800 dark:text-ink-200 uppercase tracking-wider mb-2">
                                Hands-on Practice Tasks
                              </p>
                              <ul className="space-y-1.5">
                                {item.practice_tasks.map((task, i) => (
                                  <li key={i} className="flex items-start gap-2 text-ink-600 dark:text-ink-300">
                                    <span className="text-iris-500 font-bold">•</span>
                                    <span>{task}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {/* Mini Project */}
                          {item.mini_project && (
                            <div className="p-3 rounded-xl bg-growth-50/50 dark:bg-growth-950/20 border border-growth-200 dark:border-growth-900/30">
                              <p className="font-bold text-growth-700 dark:text-growth-400 uppercase tracking-wider mb-1">
                                Milestone Mini-Project
                              </p>
                              <p className="text-ink-600 dark:text-ink-300">{item.mini_project}</p>
                            </div>
                          )}

                          {/* Links / Quiz / AI Assistant CTAs */}
                          <div className="flex flex-wrap items-center gap-3 pt-2">
                            {item.quiz_id && (
                              <button
                                onClick={() => navigate(`/courses`)}
                                className="btn-secondary py-1.5 px-3 text-xs flex items-center gap-1.5"
                              >
                                <AcademicCapIcon className="h-4 w-4 text-cyan-500" />
                                <span>Take Quiz Verification</span>
                              </button>
                            )}

                            <button
                              onClick={() => navigate(ROUTES.CHAT)}
                              className="btn-secondary py-1.5 px-3 text-xs flex items-center gap-1.5"
                            >
                              <SparklesIcon className="h-4 w-4 text-iris-500" />
                              <span>Practice with AI Assistant</span>
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
