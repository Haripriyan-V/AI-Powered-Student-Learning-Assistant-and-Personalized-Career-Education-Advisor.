import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  BriefcaseIcon,
  ArrowTrendingUpIcon,
  SparklesIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  ChartBarIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';
import { ROUTES } from '../../utils/constants';

export default function Career() {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [targetCareerId, setTargetCareerId] = useState(null);
  const [settingTarget, setSettingTarget] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [targetMsg, setTargetMsg] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get('/career/my-recommendations/'),
      api.get('/career/target-career/'),
    ])
      .then(([recRes, targetRes]) => {
        const recList = Array.isArray(recRes.data)
          ? recRes.data
          : (recRes.data?.recommendations || recRes.data?.results || []);
        setRecommendations(recList);
        if (targetRes.data && targetRes.data.id) {
          setTargetCareerId(targetRes.data.id);
        }
      })
      .catch((err) => {
        console.error('Error fetching recommendations:', err);
        setError('Failed to load career recommendations.');
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSetTarget = async (careerId, title) => {
    setSettingTarget(careerId);
    try {
      await api.post('/career/target-career/', { career_id: careerId });
      setTargetCareerId(careerId);
      setTargetMsg(`Target role set to "${title}". Skill Gap Analyzer updated.`);
      setTimeout(() => setTargetMsg(null), 4000);
    } catch (err) {
      console.error('Error setting target career:', err);
    } finally {
      setSettingTarget(null);
    }
  };

  if (loading) return <Loader label="Evaluating transparent career match scores…" size="lg" />;

  return (
    <div className="space-y-8 pb-12">
      {/* Header Banner */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-iris-500/10 text-iris-600 dark:text-iris-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <SparklesIcon className="h-4 w-4" />
          AI Career Intelligence Engine
        </div>
        <h1 className="text-2xl lg:text-3xl font-bold text-ink-900 dark:text-ink-50 mb-1">
          Intelligent Career Recommendations
        </h1>
        <p className="text-sm text-ink-600 dark:text-ink-400">
          Ranked by multi-factor algorithmic alignment across your verified skills, psychometric assessment, resume experience, and interests.
        </p>
      </div>

      {targetMsg && (
        <div className="p-4 rounded-xl border border-growth-300 bg-growth-50 text-growth-800 text-sm flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <CheckCircleIcon className="h-5 w-5 text-growth-600 shrink-0" />
            <span>{targetMsg}</span>
          </div>
          <button
            onClick={() => navigate(ROUTES.SKILL_GAP)}
            className="text-xs font-bold text-growth-700 underline flex items-center gap-1"
          >
            <span>Open Skill Gap</span>
            <ArrowRightIcon className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-700 text-sm">
          {error}
        </div>
      )}

      {recommendations.length === 0 ? (
        <div className="surface p-12 text-center text-ink-500">
          <SparklesIcon className="h-12 w-12 mx-auto mb-3 text-iris-500 opacity-60" />
          <p className="font-semibold text-ink-800 dark:text-ink-200">No Career Recommendations Yet</p>
          <p className="text-xs max-w-md mx-auto mt-1 mb-4 text-ink-600 dark:text-ink-400">
            We need some information about your skills to recommend careers.
            Please complete the Skill Assessment or add your skills to your profile.
          </p>
          <div className="flex items-center justify-center gap-3">
            <button onClick={() => navigate(ROUTES.ASSESSMENT)} className="btn-primary">
              Take Skill Assessment
            </button>
            <button onClick={() => navigate(ROUTES.PROFILE)} className="btn-secondary">
              Add Skills to Profile
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {recommendations.map((rec, idx) => {
            const actualCareerId = rec.career_path_id || rec.career_path || rec.id;
            const isTarget = targetCareerId === actualCareerId;
            const salary = rec.average_salary_lpa || rec.career_path_average_salary_lpa;
            const title = rec.career || rec.career_path_title || rec.title || 'Career Path';
            const field = rec.career_field_name || rec.career_path_career_field_name || 'Technology';
            const outlook = rec.growth_outlook || rec.career_path_growth_outlook || 'high';
            const matchScore = Number(rec.match_score ?? rec.score ?? rec.matchPercentage ?? 70);

            return (
              <motion.div
                key={rec.id || idx}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                className={`surface p-6 flex flex-col justify-between relative transition-all ${
                  isTarget ? 'ring-2 ring-iris-500 shadow-md' : 'hover:border-iris-300'
                }`}
              >
                <div>
                  {/* Top Badges */}
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h2 className="text-lg font-bold text-ink-900 dark:text-ink-50">{title}</h2>
                        {isTarget && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-iris-500 text-white uppercase tracking-wider">
                            Active Target
                          </span>
                        )}
                      </div>
                      <p className="text-xs font-semibold text-iris-600 dark:text-iris-400 mt-0.5">{field}</p>
                    </div>

                    <div className="text-right shrink-0">
                      <span className="text-2xl font-black text-iris-600 dark:text-iris-400">
                        {matchScore}%
                      </span>
                      <p className="text-[10px] text-ink-400 font-semibold uppercase tracking-wider">Match</p>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full bg-ink-100 dark:bg-ink-800 rounded-full h-2.5 mb-4 overflow-hidden">
                    <div
                      className="bg-iris-500 h-full rounded-full transition-all duration-800"
                      style={{ width: `${matchScore}%` }}
                    />
                  </div>

                  {/* Metadata Row */}
                  <div className="flex flex-wrap items-center gap-4 text-xs text-ink-600 dark:text-ink-400 mb-4 pb-3 border-b border-ink-100 dark:border-ink-800">
                    {salary && (
                      <div className="flex items-center gap-1.5 font-medium">
                        <ArrowTrendingUpIcon className="h-4 w-4 text-growth-500" />
                        <span>₹{Number(salary).toLocaleString('en-IN')} LPA Avg.</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1.5 font-medium capitalize">
                      <SparklesIcon className="h-4 w-4 text-marigold-500" />
                      <span>{outlook.replace('_', ' ')} Growth</span>
                    </div>
                  </div>

                  {/* Why this career reasoning */}
                  <div className="p-3.5 rounded-xl bg-ink-50/70 dark:bg-ink-900/40 border border-ink-100 dark:border-ink-800/80 mb-4 space-y-2">
                    <p className="text-xs font-bold text-ink-700 dark:text-ink-300 uppercase tracking-wider">
                      Why this career?
                    </p>
                    <p className="text-xs text-ink-600 dark:text-ink-400 leading-relaxed">
                      {rec.reason || rec.reasoning}
                    </p>

                    {/* Matched vs Missing Skills */}
                    {rec.matched_skills && rec.matched_skills.length > 0 && (
                      <div className="pt-1 flex flex-wrap gap-1 items-center">
                        <span className="text-[11px] font-bold text-growth-600 mr-1">✓ Matched:</span>
                        {rec.matched_skills.map((s) => (
                          <span key={s} className="text-[11px] px-2 py-0.5 rounded bg-growth-500/10 text-growth-700 dark:text-growth-300 font-medium">
                            {s}
                          </span>
                        ))}
                      </div>
                    )}

                    {rec.missing_skills && rec.missing_skills.length > 0 && (
                      <div className="pt-1 flex flex-wrap gap-1 items-center">
                        <span className="text-[11px] font-bold text-rose-600 mr-1">○ Gaps:</span>
                        {rec.missing_skills.map((s) => (
                          <span key={s} className="text-[11px] px-2 py-0.5 rounded bg-rose-500/10 text-rose-700 dark:text-rose-300 font-medium">
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 pt-2">
                  {!isTarget && (
                    <button
                      onClick={() => handleSetTarget(actualCareerId, title)}
                      disabled={settingTarget === actualCareerId}
                      className="btn-secondary text-xs flex-1 py-2 font-medium"
                    >
                      {settingTarget === actualCareerId ? 'Setting…' : 'Set as Target Role'}
                    </button>
                  )}

                  <button
                    onClick={() => navigate(`${ROUTES.SKILL_GAP}?career_id=${actualCareerId}`)}
                    className="btn-primary text-xs flex-1 py-2 flex items-center justify-center gap-1 font-medium"
                  >
                    <ChartBarIcon className="h-3.5 w-3.5" />
                    <span>Analyze Skill Gap</span>
                  </button>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}