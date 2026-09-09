import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  SparklesIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  FireIcon,
  AcademicCapIcon,
  ArrowTrendingUpIcon,
  ChartBarIcon,
  MapIcon,
  ChatBubbleLeftRightIcon,
} from '@heroicons/react/24/outline';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';
import { ROUTES } from '../../utils/constants';

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export default function SkillGapAnalyzer() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [careers, setCareers] = useState([]);
  const [selectedCareerId, setSelectedCareerId] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch available career paths
      const careerRes = await api.get('/career/paths/');
      const careerList = Array.isArray(careerRes.data) ? careerRes.data : careerRes.data.results || [];
      setCareers(careerList);

      // Check if URL specifies ?career_id=X
      const searchParams = new URLSearchParams(window.location.search);
      const urlCareerId = searchParams.get('career_id');

      // 2. Fetch target career or specified career skill gap
      const gapUrl = urlCareerId ? `/career/skill-gap/?career_id=${urlCareerId}` : '/career/skill-gap/';
      const gapRes = await api.get(gapUrl);
      setAnalysis(gapRes.data);
      if (urlCareerId) {
        setSelectedCareerId(Number(urlCareerId));
      } else if (gapRes.data && gapRes.data.career_path) {
        setSelectedCareerId(gapRes.data.career_path);
      } else if (careerList.length > 0) {
        setSelectedCareerId(careerList[0].id);
      }
    } catch (err) {
      console.error('Error loading skill gap:', err);
      setError('Unable to load skill gap data. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleCareerChange = async (e) => {
    const careerId = e.target.value;
    setSelectedCareerId(careerId);
    setAnalyzing(true);
    try {
      // Set as target career & trigger fresh analysis
      await api.post('/career/target-career/', { career_id: careerId });
      const res = await api.post('/career/skill-gap/analyze/', { career_id: careerId });
      setAnalysis(res.data);
    } catch (err) {
      console.error('Error analyzing skill gap:', err);
      setError('Failed to analyze selected career path.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleRefreshAnalysis = async () => {
    if (!selectedCareerId) return;
    setAnalyzing(true);
    try {
      const res = await api.post('/career/skill-gap/analyze/', { career_id: selectedCareerId });
      setAnalysis(res.data);
    } catch (err) {
      console.error('Error refreshing analysis:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <Loader label="🧠 Analyzing your skill intelligence & career readiness…" size="lg" />;
  }

  const readinessScore = analysis ? Number(analysis.readiness_score) : 0;
  const gapsData = analysis?.gaps_data || [];
  const prioritySkills = analysis?.priority_skills || [];
  const counts = {
    strong: analysis?.strong_count || 0,
    minor: analysis?.minor_count || 0,
    moderate: analysis?.moderate_count || 0,
    major: analysis?.major_count || 0,
    critical: analysis?.critical_count || 0,
  };

  // Filter skills
  const filteredSkills = gapsData.filter((item) => {
    if (filterCategory === 'gaps') return item.gap > 0;
    if (filterCategory === 'strong') return item.gap <= 10;
    if (filterCategory === 'critical') return item.gap > 50;
    return true;
  });

  // Prepare radar chart data
  const categorySummary = analysis?.category_summary || [];
  const radarLabels = categorySummary.map((c) => c.category);
  const radarCurrent = categorySummary.map((c) => c.current_avg);
  const radarRequired = categorySummary.map((c) => c.required_avg);

  const radarData = {
    labels: radarLabels.length > 0 ? radarLabels : ['Programming', 'Data Science', 'AI/ML', 'Cloud/DevOps', 'Databases', 'Soft Skills'],
    datasets: [
      {
        label: 'Your Current Proficiency',
        data: radarCurrent.length > 0 ? radarCurrent : [65, 55, 40, 30, 60, 75],
        backgroundColor: 'rgba(99, 102, 241, 0.25)',
        borderColor: 'rgba(99, 102, 241, 0.9)',
        pointBackgroundColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 2,
      },
      {
        label: 'Required for Career',
        data: radarRequired.length > 0 ? radarRequired : [85, 80, 80, 70, 75, 80],
        backgroundColor: 'rgba(239, 68, 68, 0.12)',
        borderColor: 'rgba(239, 68, 68, 0.8)',
        pointBackgroundColor: 'rgba(239, 68, 68, 1)',
        borderDash: [4, 4],
        borderWidth: 2,
      },
    ],
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        angleLines: { color: 'rgba(156, 163, 175, 0.2)' },
        grid: { color: 'rgba(156, 163, 175, 0.2)' },
        suggestedMin: 0,
        suggestedMax: 100,
        ticks: { stepSize: 20, display: false },
        pointLabels: {
          font: { size: 11, weight: '600' },
          color: '#6366f1',
        },
      },
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: { boxWidth: 12, padding: 16 },
      },
    },
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div className="surface p-6 lg:p-8 relative overflow-hidden bg-gradient-to-br from-iris-500/10 via-ink-50/50 to-growth-500/5 dark:from-iris-950/40 dark:via-ink-900/60 dark:to-ink-950">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-iris-500/10 text-iris-600 dark:text-iris-400 text-xs font-semibold uppercase tracking-wider">
              <SparklesIcon className="h-4 w-4" />
              AI Skill Intelligence Engine
            </div>
            <h1 className="text-2xl lg:text-3xl font-bold text-ink-900 dark:text-ink-50">
              AI Skill Gap Analyzer
            </h1>
            <p className="text-sm text-ink-600 dark:text-ink-300">
              Comparing your verified skills against industry role benchmarks. Discover exactly what to learn next to bridge every gap.
            </p>
          </div>

          {/* Career Selector & Refresh */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <div className="relative">
              <label className="block text-xs font-medium text-ink-500 dark:text-ink-400 mb-1">Target Role</label>
              <select
                value={selectedCareerId}
                onChange={handleCareerChange}
                disabled={analyzing}
                className="input text-sm py-2 pr-8 font-medium min-w-[240px] bg-white dark:bg-ink-900"
              >
                {careers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="sm:self-end">
              <button
                onClick={handleRefreshAnalysis}
                disabled={analyzing}
                className="btn-secondary flex items-center justify-center gap-2 py-2 px-4 w-full sm:w-auto"
                title="Recalculate with latest quiz & resume updates"
              >
                <ArrowPathIcon className={`h-4 w-4 ${analyzing ? 'animate-spin text-iris-500' : ''}`} />
                <span>{analyzing ? 'Analyzing…' : 'Re-evaluate'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-700 text-sm flex items-center gap-3">
          <ExclamationTriangleIcon className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Top Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Career Readiness Card */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="surface p-5 lg:col-span-2 flex items-center justify-between gap-4 border-l-4 border-l-iris-500"
        >
          <div>
            <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider mb-1">
              Overall Career Readiness
            </p>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-iris-600 dark:text-iris-400">
                {readinessScore}%
              </span>
              <span className="text-xs text-ink-500">
                for {analysis?.career_path_title || 'Target Role'}
              </span>
            </div>
            <p className="text-xs text-ink-500 mt-2">
              {readinessScore >= 75
                ? '🚀 Interview & Job Ready!'
                : readinessScore >= 50
                ? '⚡ Solid Foundation — Focus on key gaps'
                : '🌱 Learning Phase — Follow your roadmap'}
            </p>
          </div>

          {/* Progress Ring / Gauge */}
          <div className="relative h-20 w-20 shrink-0 flex items-center justify-center">
            <svg className="h-20 w-20 transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-ink-100 dark:text-ink-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-iris-500 transition-all duration-1000 ease-out"
                strokeDasharray={`${readinessScore}, 100`}
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span className="absolute text-sm font-bold text-ink-900 dark:text-ink-100">
              {readinessScore}%
            </span>
          </div>
        </motion.div>

        {/* Strong Skills */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="surface p-5 border-l-4 border-l-growth-500"
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider">Strong Skills</p>
            <CheckCircleIcon className="h-5 w-5 text-growth-500" />
          </div>
          <p className="text-2xl font-bold text-growth-600 dark:text-growth-400">{counts.strong}</p>
          <p className="text-xs text-ink-500 mt-1">Met or exceeded target</p>
        </motion.div>

        {/* Moderate Gaps */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="surface p-5 border-l-4 border-l-marigold-500"
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider">Moderate Gaps</p>
            <ExclamationTriangleIcon className="h-5 w-5 text-marigold-500" />
          </div>
          <p className="text-2xl font-bold text-marigold-600 dark:text-marigold-400">
            {counts.minor + counts.moderate}
          </p>
          <p className="text-xs text-ink-500 mt-1">11% - 50% gap to bridge</p>
        </motion.div>

        {/* Critical Gaps */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="surface p-5 border-l-4 border-l-rose-500"
        >
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider">Critical Gaps</p>
            <XCircleIcon className="h-5 w-5 text-rose-500" />
          </div>
          <p className="text-2xl font-bold text-rose-600 dark:text-rose-400">
            {counts.major + counts.critical}
          </p>
          <p className="text-xs text-ink-500 mt-1">High priority next steps</p>
        </motion.div>
      </div>

      {/* Main Analysis Section: Radar Chart + Priority Skills */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Radar Chart (5 cols) */}
        <div className="surface p-6 lg:col-span-5 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-semibold text-ink-900 dark:text-ink-50">Skill Profile Radar</h2>
              <p className="text-xs text-ink-500">Domain competency comparison</p>
            </div>
            <ChartBarIcon className="h-5 w-5 text-iris-500 opacity-60" />
          </div>
          <div className="h-[280px] w-full flex items-center justify-center relative">
            <Radar data={radarData} options={radarOptions} />
          </div>
        </div>

        {/* Top 5 Priority Skills to Learn Next (7 cols) */}
        <div className="surface p-6 lg:col-span-7 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="font-semibold text-ink-900 dark:text-ink-50 flex items-center gap-2">
                  <FireIcon className="h-5 w-5 text-rose-500" />
                  Top Priority Skills to Learn Next
                </h2>
                <p className="text-xs text-ink-500">Calculated by: Importance × Skill Gap × Career Relevance</p>
              </div>
            </div>

            <div className="space-y-3">
              {prioritySkills.map((skill, index) => (
                <div
                  key={skill.skill_id || index}
                  className="p-3.5 rounded-xl border border-ink-200 dark:border-ink-800 bg-ink-50/50 dark:bg-ink-900/40 flex items-center justify-between gap-4 hover:border-iris-400 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-iris-500/10 text-iris-600 dark:text-iris-400 font-bold text-xs">
                      #{index + 1}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-ink-900 dark:text-ink-50 text-sm">{skill.name}</p>
                        <span className="text-[11px] px-2 py-0.5 rounded-full font-medium bg-rose-500/10 text-rose-600 dark:text-rose-400">
                          {skill.gap}% gap
                        </span>
                      </div>
                      <p className="text-xs text-ink-500 mt-0.5">
                        Current: <span className="font-semibold">{skill.current_proficiency}%</span> • Target: <span className="font-semibold">{skill.required_proficiency}%</span>
                      </p>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-md uppercase tracking-wider ${
                      skill.priority_score > 250
                        ? 'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                        : 'bg-marigold-500/15 text-marigold-600 dark:text-marigold-400'
                    }`}>
                      {skill.priority_score > 250 ? 'HIGH PRIORITY' : 'MEDIUM'}
                    </span>
                  </div>
                </div>
              ))}

              {prioritySkills.length === 0 && (
                <div className="py-8 text-center text-ink-500 text-sm">
                  🎉 No skill gaps detected! Your current skills fully align with this career.
                </div>
              )}
            </div>
          </div>

          {/* Roadmap & Chat quick action buttons */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-5 mt-4 border-t border-ink-100 dark:border-ink-800">
            <button
              onClick={() => navigate(ROUTES.ROADMAP)}
              className="btn-primary w-full sm:w-auto flex items-center justify-center gap-2"
            >
              <MapIcon className="h-4 w-4" />
              <span>Generate Dynamic Roadmap</span>
            </button>
            <button
              onClick={() => navigate(ROUTES.CHAT)}
              className="btn-secondary w-full sm:w-auto flex items-center justify-center gap-2"
            >
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
              <span>Ask AI How to Bridge Gaps</span>
            </button>
          </div>
        </div>
      </div>

      {/* AI Explainability Banner */}
      {analysis?.ai_explanation && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="surface p-6 lg:p-7 border border-iris-500/30 bg-gradient-to-r from-iris-500/5 via-transparent to-growth-500/5"
        >
          <div className="flex items-start gap-4">
            <div className="h-10 w-10 rounded-xl bg-iris-500/10 text-iris-600 dark:text-iris-400 flex items-center justify-center shrink-0 mt-0.5">
              <SparklesIcon className="h-6 w-6" />
            </div>
            <div className="space-y-2 flex-1">
              <h3 className="font-semibold text-ink-900 dark:text-ink-50">
                AI Career Strategist Analysis & Next Steps
              </h3>
              <div className="prose dark:prose-invert max-w-none text-sm text-ink-700 dark:text-ink-300 whitespace-pre-line leading-relaxed">
                {analysis.ai_explanation}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Detailed Current vs Required Skills Comparison Table */}
      <div className="surface p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h2 className="font-semibold text-ink-900 dark:text-ink-50 text-base">
              Current vs Required Skill Proficiency
            </h2>
            <p className="text-xs text-ink-500">Comprehensive breakdown across all domain competencies</p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-ink-100 dark:bg-ink-800 self-start sm:self-auto">
            <button
              onClick={() => setFilterCategory('all')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                filterCategory === 'all' ? 'bg-white dark:bg-ink-900 text-ink-900 dark:text-ink-50 shadow-sm' : 'text-ink-500'
              }`}
            >
              All ({gapsData.length})
            </button>
            <button
              onClick={() => setFilterCategory('gaps')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                filterCategory === 'gaps' ? 'bg-white dark:bg-ink-900 text-ink-900 dark:text-ink-50 shadow-sm' : 'text-ink-500'
              }`}
            >
              Gaps Only ({gapsData.filter((i) => i.gap > 0).length})
            </button>
            <button
              onClick={() => setFilterCategory('strong')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                filterCategory === 'strong' ? 'bg-white dark:bg-ink-900 text-ink-900 dark:text-ink-50 shadow-sm' : 'text-ink-500'
              }`}
            >
              Strong ({counts.strong})
            </button>
          </div>
        </div>

        {/* Comparison Bars */}
        <div className="space-y-4">
          {filteredSkills.map((item) => {
            const currentProf = item.current_proficiency;
            const reqProf = item.required_proficiency;
            const gap = item.gap;

            return (
              <div
                key={item.skill_id || item.name}
                className="p-4 rounded-xl border border-ink-100 dark:border-ink-800 hover:border-ink-300 dark:hover:border-ink-700 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-ink-900 dark:text-ink-50 text-sm">{item.name}</h3>
                      <span className="text-[11px] text-ink-400 font-medium">({item.category})</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                      gap <= 10
                        ? 'bg-growth-500/10 text-growth-600 dark:text-growth-400'
                        : gap <= 25
                        ? 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400'
                        : gap <= 50
                        ? 'bg-marigold-500/10 text-marigold-600 dark:text-marigold-400'
                        : 'bg-rose-500/10 text-rose-600 dark:text-rose-400'
                    }`}>
                      {item.status} ({gap}% gap)
                    </span>
                    <span className="text-xs text-ink-400">
                      Imp: {'★'.repeat(item.importance)}
                    </span>
                  </div>
                </div>

                {/* Double Progress Bar */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs text-ink-500">
                    <span>You: <strong className="text-ink-800 dark:text-ink-200">{currentProf}%</strong></span>
                    <span>Target: <strong className="text-ink-800 dark:text-ink-200">{reqProf}%</strong></span>
                  </div>

                  <div className="h-3 w-full bg-ink-100 dark:bg-ink-800 rounded-full overflow-hidden relative">
                    {/* Target marker line */}
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-ink-900 dark:bg-ink-100 z-10"
                      style={{ left: `${reqProf}%` }}
                      title={`Target requirement: ${reqProf}%`}
                    />
                    {/* Current fill bar */}
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        gap <= 10
                          ? 'bg-growth-500'
                          : gap <= 25
                          ? 'bg-cyan-500'
                          : gap <= 50
                          ? 'bg-marigold-500'
                          : 'bg-rose-500'
                      }`}
                      style={{ width: `${currentProf}%` }}
                    />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
