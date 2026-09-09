import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  BookOpenIcon,
  BriefcaseIcon,
  ArrowTrendingUpIcon,
  AcademicCapIcon,
  FireIcon,
  SparklesIcon,
  ChartBarIcon,
  MapIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  ChatBubbleLeftRightIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';
import { ROUTES } from '../../utils/constants';

export default function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [gamification, setGamification] = useState(null);
  const [skillGap, setSkillGap] = useState(null);
  const [roadmap, setRoadmap] = useState(null);
  const [courses, setCourses] = useState([]);
  const [claiming, setClaiming] = useState(false);
  const [claimMsg, setClaimMsg] = useState(null);

  useEffect(() => {
    // Load stored user profile
    const storedUser = localStorage.getItem('disha_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {}
    }

    Promise.all([
      api.get('/learning/gamification/').catch(() => ({ data: null })),
      api.get('/career/skill-gap/').catch(() => ({ data: null })),
      api.get('/learning/roadmap/').catch(() => ({ data: null })),
      api.get('/learning/courses/?limit=3').catch(() => ({ data: { results: [] } })),
    ])
      .then(([gamRes, gapRes, roadRes, coursesRes]) => {
        setGamification(gamRes.data);
        setSkillGap(gapRes.data);
        setRoadmap(roadRes.data);
        const cData = coursesRes.data;
        setCourses(Array.isArray(cData) ? cData : cData.results || []);
      })
      .catch((err) => console.error('Error loading dashboard data:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleDailyCheckin = async () => {
    setClaiming(true);
    try {
      const res = await api.post('/learning/gamification/daily-checkin/');
      setClaimMsg(res.data.message);
      // Refresh gamification summary
      const gRes = await api.get('/learning/gamification/');
      setGamification(gRes.data);
      setTimeout(() => setClaimMsg(null), 4000);
    } catch (err) {
      console.error('Checkin error:', err);
    } finally {
      setClaiming(false);
    }
  };

  if (loading) return <Loader label="Loading your personalized learning dashboard…" size="lg" />;

  const readinessScore = skillGap ? Math.round(Number(skillGap.readiness_score)) : 0;
  const targetCareerTitle = skillGap?.career_path_title || 'Select a Target Career';
  const prioritySkills = skillGap?.priority_skills || [];
  const currentTask = roadmap?.phases?.flatMap((p) => p.items)?.find((i) => i.status === 'in_progress');

  return (
    <div className="space-y-8 pb-12">
      {/* Welcome Hero Banner */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="surface p-6 lg:p-8 relative overflow-hidden bg-gradient-to-r from-iris-500/10 via-ink-50/50 to-growth-500/10 dark:from-iris-950/40 dark:via-ink-900/40 dark:to-growth-950/20"
      >
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex items-center gap-3">
              <span className="text-xl">👋</span>
              <h1 className="text-2xl lg:text-3xl font-extrabold text-ink-900 dark:text-ink-50">
                Welcome back, {user?.first_name || user?.username || 'Student'}!
              </h1>
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-semibold text-ink-600 dark:text-ink-300">
              <span className="flex items-center gap-1.5 text-iris-600 dark:text-iris-400">
                <BriefcaseIcon className="h-4 w-4" />
                Target Goal: <strong className="text-ink-900 dark:text-ink-50">{targetCareerTitle}</strong>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5 text-growth-600 dark:text-growth-400">
                <ArrowTrendingUpIcon className="h-4 w-4" />
                Readiness: {readinessScore}%
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5 text-marigold-600 dark:text-marigold-400">
                <FireIcon className="h-4 w-4 text-orange-500" />
                {gamification?.current_streak ?? 0} Day Streak
              </span>
            </div>
          </div>

          {/* Gamification Badge & Daily Check-in */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 shrink-0">
            <div className="px-4 py-2 rounded-2xl bg-white dark:bg-ink-900 border border-ink-200 dark:border-ink-800 shadow-2xs">
              <p className="text-[10px] font-bold uppercase tracking-wider text-ink-400">Level {gamification?.level ?? 1}</p>
              <p className="text-sm font-extrabold text-iris-600 dark:text-iris-400">{gamification?.level_title || 'Beginner'}</p>
              <p className="text-[11px] text-ink-500">{gamification?.xp ?? 0} XP</p>
            </div>

            <button
              onClick={handleDailyCheckin}
              disabled={claiming}
              className="btn-primary py-2 px-4 text-xs flex items-center gap-2"
            >
              <FireIcon className="h-4 w-4 text-yellow-300" />
              <span>{claiming ? 'Claiming…' : 'Claim Daily XP'}</span>
            </button>
          </div>
        </div>
      </motion.div>

      {claimMsg && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3.5 rounded-xl border border-growth-300 bg-growth-50 text-growth-800 text-xs font-semibold flex items-center gap-2"
        >
          <SparklesIcon className="h-4 w-4 text-growth-600" />
          <span>{claimMsg}</span>
        </motion.div>
      )}

      {/* Top 4 Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Career Readiness */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="surface p-5 border-l-4 border-l-iris-500 cursor-pointer hover:border-iris-400 transition-all"
          onClick={() => navigate(ROUTES.SKILL_GAP)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">Career Readiness</p>
              <p className="text-2xl font-bold text-iris-600 dark:text-iris-400">{readinessScore}%</p>
              <p className="text-[11px] text-ink-500 mt-1">Based on {skillGap?.total_skills_count ?? 0} skills</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-iris-500 opacity-20" />
          </div>
          <div className="w-full bg-ink-200 dark:bg-ink-800 rounded-full h-1.5 mt-3">
            <div className="bg-iris-500 h-1.5 rounded-full" style={{ width: `${readinessScore}%` }} />
          </div>
        </motion.div>

        {/* Experience Points */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.08 }}
          className="surface p-5 border-l-4 border-l-growth-500"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">Earned XP</p>
              <p className="text-2xl font-bold text-growth-600 dark:text-growth-400">{gamification?.xp ?? 0} XP</p>
              <p className="text-[11px] text-ink-500 mt-1">Next rank at {gamification?.next_level_xp ?? 100} XP</p>
            </div>
            <SparklesIcon className="h-8 w-8 text-growth-500 opacity-20" />
          </div>
        </motion.div>

        {/* Active Streak */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.16 }}
          className="surface p-5 border-l-4 border-l-orange-500"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">Learning Streak</p>
              <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">🔥 {gamification?.current_streak ?? 0} Days</p>
              <p className="text-[11px] text-ink-500 mt-1">Best: {gamification?.longest_streak ?? 0} days</p>
            </div>
            <FireIcon className="h-8 w-8 text-orange-500 opacity-20" />
          </div>
        </motion.div>

        {/* Roadmap Progress */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.24 }}
          className="surface p-5 border-l-4 border-l-cyan-500 cursor-pointer hover:border-cyan-400 transition-all"
          onClick={() => navigate(ROUTES.ROADMAP)}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">Roadmap Progress</p>
              <p className="text-2xl font-bold text-cyan-600 dark:text-cyan-400">{roadmap?.overall_progress || 0}%</p>
              <p className="text-[11px] text-ink-500 mt-1">Phase {roadmap?.active_phase || 1} Active</p>
            </div>
            <MapIcon className="h-8 w-8 text-cyan-500 opacity-20" />
          </div>
        </motion.div>
      </div>

      {/* Center 2-Column Section: Top Priority Gaps + Next Roadmap Task */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top Priority Skill Gaps (6 cols) */}
        <div className="surface p-6 lg:col-span-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-bold text-ink-900 dark:text-ink-50 flex items-center gap-2">
                  <ChartBarIcon className="h-5 w-5 text-iris-500" />
                  Top Priority Skill Gaps
                </h2>
                <p className="text-xs text-ink-500">Skills with greatest impact on your career readiness</p>
              </div>
              <button
                onClick={() => navigate(ROUTES.SKILL_GAP)}
                className="text-xs font-semibold text-iris-600 dark:text-iris-400 hover:underline flex items-center gap-1"
              >
                <span>Full Analyzer</span>
                <ArrowRightIcon className="h-3 w-3" />
              </button>
            </div>

            <div className="space-y-3">
              {prioritySkills.slice(0, 3).map((skill, i) => (
                <div
                  key={skill.name || i}
                  className="p-3.5 rounded-xl border border-ink-100 dark:border-ink-800/80 bg-ink-50/40 dark:bg-ink-900/30 flex items-center justify-between gap-3"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-ink-900 dark:text-ink-50 text-sm">{skill.name}</p>
                      <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-rose-500/10 text-rose-600">
                        {skill.gap}% gap
                      </span>
                    </div>
                    <p className="text-xs text-ink-500 mt-0.5">
                      Current: {skill.current_proficiency}% • Target: {skill.required_proficiency}%
                    </p>
                  </div>

                  <span className="text-[11px] font-semibold text-ink-400 uppercase tracking-wider">
                    #{i + 1} Priority
                  </span>
                </div>
              ))}

              {(!prioritySkills || prioritySkills.length === 0) && (
                <div className="py-6 text-center text-ink-500 text-xs">
                  All target career skills are fully met!
                </div>
              )}
            </div>
          </div>

          <div className="pt-4 mt-4 border-t border-ink-100 dark:border-ink-800 flex items-center gap-3">
            <button
              onClick={() => navigate(ROUTES.SKILL_GAP)}
              className="btn-primary text-xs w-full py-2"
            >
              Analyze & Bridge Gaps
            </button>
          </div>
        </div>

        {/* Current Roadmap Task (6 cols) */}
        <div className="surface p-6 lg:col-span-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-bold text-ink-900 dark:text-ink-50 flex items-center gap-2">
                  <MapIcon className="h-5 w-5 text-cyan-500" />
                  Active Learning Milestone
                </h2>
                <p className="text-xs text-ink-500">Your current roadmap assignment</p>
              </div>
              <button
                onClick={() => navigate(ROUTES.ROADMAP)}
                className="text-xs font-semibold text-iris-600 dark:text-iris-400 hover:underline flex items-center gap-1"
              >
                <span>View Roadmap</span>
                <ArrowRightIcon className="h-3 w-3" />
              </button>
            </div>

            {currentTask ? (
              <div className="p-4 rounded-xl border border-iris-200 dark:border-iris-900/40 bg-iris-50/20 dark:bg-iris-950/20 space-y-3">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-iris-500 animate-ping" />
                  <span className="text-xs font-bold text-iris-600 dark:text-iris-400 uppercase tracking-wider">
                    Phase {currentTask.phase_number || 1} • In Progress
                  </span>
                </div>
                <h3 className="font-bold text-ink-900 dark:text-ink-50 text-base">
                  {currentTask.title}
                </h3>
                <p className="text-xs text-ink-600 dark:text-ink-300 line-clamp-2">
                  {currentTask.description}
                </p>
                {currentTask.skill_name && (
                  <span className="inline-block text-[11px] px-2.5 py-0.5 rounded-full font-medium bg-iris-500/10 text-iris-600 dark:text-iris-400">
                    Skill: {currentTask.skill_name}
                  </span>
                )}
              </div>
            ) : (
              <div className="p-6 text-center text-ink-500 text-xs">
                Ready to begin your journey? Open your roadmap to start your first task!
              </div>
            )}
          </div>

          <div className="pt-4 mt-4 border-t border-ink-100 dark:border-ink-800 flex items-center gap-3">
            <button
              onClick={() => navigate(ROUTES.ROADMAP)}
              className="btn-primary text-xs w-full py-2 flex items-center justify-center gap-2"
            >
              <span>Continue Learning</span>
              <ArrowRightIcon className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => navigate(ROUTES.CHAT)}
              className="btn-secondary text-xs py-2 px-4 flex items-center justify-center gap-1.5 shrink-0"
              title="Ask AI Assistant about this milestone"
            >
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
              <span>Ask AI</span>
            </button>
          </div>
        </div>
      </div>

      {/* Badges & Achievements Showcase */}
      <div className="surface p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="font-bold text-ink-900 dark:text-ink-50 flex items-center gap-2">
              <ShieldCheckIcon className="h-5 w-5 text-marigold-500" />
              Achievements & Unlocked Badges
            </h2>
            <p className="text-xs text-ink-500">Milestones unlocked throughout your learning journey</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {gamification?.badges?.map((badge) => (
            <div
              key={badge.id}
              className={`p-3 rounded-xl border text-center transition-all ${
                badge.unlocked
                  ? 'border-marigold-300 dark:border-marigold-900/60 bg-marigold-50/20 dark:bg-marigold-950/10 shadow-2xs'
                  : 'border-ink-200 dark:border-ink-800 opacity-40 grayscale'
              }`}
            >
              <span className="text-2xl block mb-1">{badge.icon}</span>
              <p className="font-bold text-xs text-ink-900 dark:text-ink-100 truncate">{badge.title}</p>
              <p className="text-[10px] text-ink-500 line-clamp-2 mt-0.5">{badge.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity Timeline */}
      {gamification?.recent_activities && gamification.recent_activities.length > 0 && (
        <div className="surface p-6">
          <h2 className="font-bold text-ink-900 dark:text-ink-50 mb-4 text-sm">
            Recent Activity & XP Log
          </h2>
          <div className="space-y-2.5">
            {gamification.recent_activities.map((act) => (
              <div
                key={act.id}
                className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-ink-50/50 dark:bg-ink-900/30 border border-ink-100 dark:border-ink-800/60"
              >
                <div className="flex items-center gap-2.5">
                  <CheckCircleIcon className="h-4 w-4 text-growth-500 shrink-0" />
                  <span className="font-medium text-ink-800 dark:text-ink-200">{act.title}</span>
                </div>
                <span className="font-bold text-growth-600 dark:text-growth-400 shrink-0">
                  +{act.xp_awarded} XP
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
