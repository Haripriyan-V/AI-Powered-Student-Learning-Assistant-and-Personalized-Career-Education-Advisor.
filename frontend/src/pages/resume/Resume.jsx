import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  DocumentTextIcon,
  ArrowUpTrayIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  SparklesIcon,
  BriefcaseIcon,
  ArrowPathIcon,
  ArrowRightIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { ROUTES } from '../../utils/constants';

export default function Resume() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [importSuccess, setImportSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [loadingInitial, setLoadingInitial] = useState(true);

  useEffect(() => {
    // Fetch latest resume analysis if available
    api
      .get('/students/resume/latest/')
      .then((res) => {
        if (res.data && res.data.id) {
          setAnalysis(res.data);
        }
      })
      .catch((err) => console.error('Error loading latest resume:', err))
      .finally(() => setLoadingInitial(false));
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setImportSuccess(null);

    const formData = new FormData();
    formData.append('resume', selectedFile);

    try {
      const res = await api.post('/students/resume/analyze/', formData);
      setAnalysis(res.data);
      setSelectedFile(null);
    } catch (err) {
      console.error('Error analyzing resume:', err);
      const serverErr = err.response?.data?.error || err.response?.data?.detail;
      setError(serverErr || 'Unable to analyze your resume. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleImportSkills = async () => {
    setImporting(true);
    try {
      const res = await api.post('/students/resume/import-skills/');
      setImportSuccess(res.data.message);
    } catch (err) {
      console.error('Error importing skills:', err);
      setError('Could not import skills to profile.');
    } finally {
      setImporting(false);
    }
  };

  const breakdown = analysis?.breakdown_scores || {};
  const careerAlign = analysis?.career_alignment || {};

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-iris-500/10 text-iris-600 dark:text-iris-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <SparklesIcon className="h-4 w-4" />
          AI Document Intelligence
        </div>
        <h1 className="text-2xl lg:text-3xl font-bold text-ink-900 dark:text-ink-50 mb-1">
          AI Resume & ATS Analyzer
        </h1>
        <p className="text-sm text-ink-600 dark:text-ink-400">
          Extract skills, evaluate ATS compatibility, detect missing keywords, and automatically synchronize verified skills with your Skill Gap profile.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-rose-700 text-sm flex items-center gap-3">
          <ExclamationCircleIcon className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {importSuccess && (
        <div className="p-4 rounded-xl border border-growth-300 bg-growth-50 text-growth-800 text-sm flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <CheckCircleIcon className="h-5 w-5 text-growth-600 shrink-0" />
            <span>{importSuccess}</span>
          </div>
          <button
            onClick={() => navigate(ROUTES.SKILL_GAP)}
            className="text-xs font-bold text-growth-700 underline flex items-center gap-1 shrink-0"
          >
            <span>View Skill Gap</span>
            <ArrowRightIcon className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Upload Box & Instructions */}
        <div className="lg:col-span-5 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="surface p-6 sm:p-8"
          >
            <form onSubmit={handleUpload}>
              <div className="border-2 border-dashed border-ink-300 dark:border-ink-700 rounded-2xl p-8 text-center hover:bg-ink-50 dark:hover:bg-ink-900/50 transition-colors cursor-pointer relative">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.txt"
                  className="hidden"
                  id="resume-upload"
                  disabled={uploading}
                />
                <label htmlFor="resume-upload" className="cursor-pointer block">
                  <ArrowUpTrayIcon className="h-12 w-12 text-iris-500 mx-auto mb-3" />
                  <p className="font-semibold text-ink-900 dark:text-ink-50 mb-1">
                    {selectedFile ? selectedFile.name : 'Upload your resume'}
                  </p>
                  <p className="text-xs text-ink-500 dark:text-ink-400">
                    PDF, DOCX, or TXT • Max 10MB
                  </p>
                </label>
              </div>

              {selectedFile && (
                <button
                  type="submit"
                  disabled={uploading}
                  className="btn-primary w-full mt-4 flex items-center justify-center gap-2"
                >
                  {uploading ? (
                    <>
                      <ArrowPathIcon className="h-4 w-4 animate-spin" />
                      <span>Analyzing Document…</span>
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-4 w-4" />
                      <span>Analyze with AI</span>
                    </>
                  )}
                </button>
              )}
            </form>

            {/* Pro Tip Card */}
            <div className="mt-6 pt-6 border-t border-ink-100 dark:border-ink-800 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-ink-800 dark:text-ink-200">
                <ShieldCheckIcon className="h-4 w-4 text-iris-500" />
                <span>How Our AI Evaluates Resumes:</span>
              </div>
              <ul className="text-xs text-ink-500 dark:text-ink-400 space-y-1.5 list-disc list-inside">
                <li>Extracts technical languages, tools, frameworks & soft skills</li>
                <li>Standardizes skill variations (e.g. React.js → React)</li>
                <li>Evaluates ATS formatting, structure, and action verbs</li>
                <li>Compares keywords directly with your target career path</li>
              </ul>
            </div>
          </motion.div>
        </div>

        {/* Right Column: Analysis Results */}
        <div className="lg:col-span-7 space-y-6">
          {analysis ? (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Top Score Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Overall Score */}
                <div className="surface p-5 border-l-4 border-l-iris-500 flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider">
                      Overall Resume Score
                    </p>
                    <p className="text-3xl font-extrabold text-iris-600 dark:text-iris-400 mt-1">
                      {analysis.overall_score}/100
                    </p>
                    <p className="text-xs text-ink-500 mt-1">
                      {analysis.overall_score >= 80 ? '⭐ Excellent Quality' : '⚡ Good — Room for refinement'}
                    </p>
                  </div>
                  <div className="h-12 w-12 rounded-xl bg-iris-500/10 flex items-center justify-center text-iris-600 font-bold">
                    {analysis.overall_score}%
                  </div>
                </div>

                {/* ATS Score */}
                <div className="surface p-5 border-l-4 border-l-growth-500 flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-ink-400 dark:text-ink-500 uppercase tracking-wider">
                      ATS Score
                    </p>
                    <p className="text-3xl font-extrabold text-growth-600 dark:text-growth-400 mt-1">
                      {analysis.ats_score || analysis.overall_score} / 100
                    </p>
                    <p className="text-xs text-ink-500 mt-1">Parser pass probability</p>
                  </div>
                  <div className="h-12 w-12 rounded-xl bg-growth-500/10 flex items-center justify-center text-growth-600 font-bold">
                    ATS
                  </div>
                </div>
              </div>

              {/* Career Alignment & Import CTA Banner */}
              <div className="surface p-6 border border-iris-500/20 bg-gradient-to-r from-iris-500/5 to-transparent space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <BriefcaseIcon className="h-5 w-5 text-iris-500" />
                      <h3 className="font-semibold text-ink-900 dark:text-ink-50">
                        Career Alignment: {careerAlign.target_role || 'Target Career'}
                      </h3>
                    </div>
                    <p className="text-xs text-ink-500 mt-0.5">
                      {careerAlign.match_percentage || 65}% match with current target role requirements
                    </p>
                  </div>

                  <button
                    onClick={handleImportSkills}
                    disabled={importing}
                    className="btn-primary py-2 px-4 text-xs flex items-center justify-center gap-1.5 shrink-0"
                  >
                    <SparklesIcon className="h-3.5 w-3.5" />
                    <span>{importing ? 'Importing…' : 'Import Skills to Skill Gap'}</span>
                  </button>
                </div>

                {/* Strong vs Missing Role Skills */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <div className="p-3 rounded-xl bg-growth-500/10 border border-growth-200 dark:border-growth-900/40">
                    <p className="text-xs font-bold text-growth-700 dark:text-growth-400 uppercase tracking-wider mb-2">
                      ✓ Strong Matched Skills ({careerAlign.strong_skills?.length || 0})
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {careerAlign.strong_skills?.map((s) => (
                        <span key={s} className="text-xs px-2 py-0.5 rounded-md bg-white dark:bg-ink-900 text-growth-700 dark:text-growth-300 font-medium shadow-2xs">
                          {s}
                        </span>
                      ))}
                      {(!careerAlign.strong_skills || careerAlign.strong_skills.length === 0) && (
                        <span className="text-xs text-ink-500">None detected</span>
                      )}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-200 dark:border-rose-900/40">
                    <p className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider mb-2">
                      ○ Role Skills to Add ({careerAlign.missing_skills?.length || 0})
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {careerAlign.missing_skills?.map((s) => (
                        <span key={s} className="text-xs px-2 py-0.5 rounded-md bg-white dark:bg-ink-900 text-rose-700 dark:text-rose-300 font-medium shadow-2xs">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Breakdown Bars */}
              <div className="surface p-6 space-y-3">
                <h3 className="font-semibold text-ink-900 dark:text-ink-50 text-sm">Evaluation Breakdown</h3>
                <div className="space-y-3">
                  {Object.entries(breakdown).map(([cat, score]) => (
                    <div key={cat}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="capitalize text-ink-600 dark:text-ink-400">{cat.replace('_', ' ')}</span>
                        <span className="font-bold text-ink-800 dark:text-ink-200">{score}%</span>
                      </div>
                      <div className="w-full bg-ink-200 dark:bg-ink-800 rounded-full h-2">
                        <div
                          className="bg-iris-500 h-2 rounded-full transition-all duration-700"
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Extracted Normalized Skills */}
              <div className="surface p-6 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-ink-900 dark:text-ink-50 text-sm">
                    Extracted & Normalized Skills ({analysis.normalized_skills?.length || 0})
                  </h3>
                  <span className="text-xs text-ink-400">Canonical Standardized</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {analysis.normalized_skills?.map((s) => (
                    <span
                      key={s}
                      className="px-2.5 py-1 rounded-lg text-xs font-medium bg-iris-50 dark:bg-iris-950/40 text-iris-600 dark:text-iris-300 border border-iris-200 dark:border-iris-800/40"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              {/* Strengths & Improvements */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="surface p-5 space-y-3">
                  <h4 className="text-xs font-bold text-growth-600 dark:text-growth-400 uppercase tracking-wider">
                    Key Strengths
                  </h4>
                  <ul className="space-y-2">
                    {analysis.strengths?.map((st, i) => (
                      <li key={i} className="text-xs text-ink-600 dark:text-ink-300 flex items-start gap-2">
                        <span className="text-growth-500 shrink-0 mt-0.5">✓</span>
                        <span>{st}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="surface p-5 space-y-3">
                  <h4 className="text-xs font-bold text-marigold-600 dark:text-marigold-400 uppercase tracking-wider">
                    Recommended Improvements
                  </h4>
                  <ul className="space-y-2">
                    {analysis.improvements?.map((imp, i) => (
                      <li key={i} className="text-xs text-ink-600 dark:text-ink-300 flex items-start gap-2">
                        <span className="text-marigold-500 shrink-0 mt-0.5">→</span>
                        <span>{imp}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="surface p-12 text-center text-ink-400 dark:text-ink-600 space-y-3">
              <DocumentTextIcon className="h-16 w-16 mx-auto opacity-40 text-iris-500" />
              <p className="font-semibold text-ink-700 dark:text-ink-300">No Resume Uploaded Yet</p>
              <p className="text-xs max-w-sm mx-auto">
                Upload your resume on the left to receive immediate ATS feedback and sync extracted skills to your Skill Gap profile.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
