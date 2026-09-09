import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  BookOpenIcon,
  SparklesIcon,
  AcademicCapIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

function EditableField({ label, value, onChange, type = 'text' }) {
  const [isEditing, setIsEditing] = useState(false);
  const [fieldValue, setFieldValue] = useState(value);

  const handleSave = () => {
    onChange(fieldValue);
    setIsEditing(false);
  };

  return (
    <div className="mb-4">
      <label className="text-xs font-medium text-ink-500 dark:text-ink-400 uppercase tracking-wide">
        {label}
      </label>
      {isEditing ? (
        <div className="mt-1 flex gap-2">
          <input
            type={type}
            value={fieldValue}
            onChange={(e) => setFieldValue(e.target.value)}
            className="flex-1 rounded-xl border border-ink-200 dark:border-ink-700 bg-white dark:bg-ink-900 px-3 py-2 text-sm"
          />
          <button
            onClick={handleSave}
            className="btn-primary"
          >
            Save
          </button>
          <button
            onClick={() => {
              setFieldValue(value);
              setIsEditing(false);
            }}
            className="btn-ghost"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div
          onClick={() => setIsEditing(true)}
          className="mt-1 rounded-xl bg-ink-50 dark:bg-ink-900 px-3 py-2 text-sm cursor-pointer hover:bg-ink-100 dark:hover:bg-ink-800 transition-colors"
        >
          {value || '–'}
        </div>
      )}
    </div>
  );
}

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [education, setEducation] = useState([]);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');

  // Education form state
  const [showEduForm, setShowEduForm] = useState(false);
  const [eduForm, setEduForm] = useState({
    institution_name: '',
    degree_or_level: '',
    field_of_study: '',
    start_year: new Date().getFullYear() - 2,
    end_year: new Date().getFullYear(),
    percentage_or_gpa: '',
  });

  // Skill form state
  const [showSkillForm, setShowSkillForm] = useState(false);
  const [skillForm, setSkillForm] = useState({
    skill_name: '',
    proficiency: 'intermediate',
  });

  useEffect(() => {
    Promise.all([
      api.get('/students/profile/me/'),
      api.get('/students/education/'),
      api.get('/students/my-skills/'),
    ])
      .then(([profileRes, educationRes, skillsRes]) => {
        setProfile(profileRes.data);
        const eduData = educationRes.data;
        setEducation(Array.isArray(eduData) ? eduData : eduData.results || []);
        const skillsData = skillsRes.data;
        setSkills(Array.isArray(skillsData) ? skillsData : skillsData.results || []);
      })
      .catch((err) => {
        console.error('Error fetching profile:', err);
        setError('Failed to load profile. Please try again.');
      })
      .finally(() => setLoading(false));
  }, []);

  const handleFieldSave = async (field, val) => {
    try {
      const updated = { ...profile, [field]: val };
      setProfile(updated);
      await api.patch('/students/profile/me/', { [field]: val });

      // Update cached user object for Navbar
      const stored = localStorage.getItem('disha_user');
      if (stored) {
        try {
          const userObj = JSON.parse(stored);
          if (field === 'user_first_name' || field === 'first_name') userObj.first_name = val;
          if (field === 'user_last_name' || field === 'last_name') userObj.last_name = val;
          localStorage.setItem('disha_user', JSON.stringify(userObj));
        } catch (e) {}
      }

      setSaveStatus('Saved!');
      setTimeout(() => setSaveStatus(null), 2500);
    } catch (err) {
      console.error('Failed to update profile field:', err);
    }
  };

  const handleAddEducation = async (e) => {
    e.preventDefault();
    if (!eduForm.institution_name || !eduForm.degree_or_level) return;
    try {
      const { data } = await api.post('/students/education/', eduForm);
      setEducation([data, ...education]);
      setShowEduForm(false);
      setEduForm({
        institution_name: '',
        degree_or_level: '',
        field_of_study: '',
        start_year: new Date().getFullYear() - 2,
        end_year: new Date().getFullYear(),
        percentage_or_gpa: '',
      });
    } catch (err) {
      console.error('Failed to add education record:', err);
    }
  };

  const handleAddSkill = async (e) => {
    e.preventDefault();
    if (!skillForm.skill_name.trim()) return;
    try {
      const { data } = await api.post('/students/my-skills/', skillForm);
      setSkills([data, ...skills]);
      setShowSkillForm(false);
      setSkillForm({ skill_name: '', proficiency: 'intermediate' });
    } catch (err) {
      console.error('Failed to add skill:', err);
    }
  };

  if (loading) return <Loader label="Loading profile…" size="lg" />;

  if (error) return <div className="text-sm text-rose-600 dark:text-rose-400">{error}</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50 mb-1">Student Profile</h1>
          <p className="text-sm text-ink-500 dark:text-ink-400">
            Manage your personal info, educational background, and verified technical skills.
          </p>
        </div>
        {saveStatus && (
          <span className="text-xs px-3 py-1 rounded-lg bg-growth-50 text-growth-700 dark:bg-growth-900/30 dark:text-growth-400 font-semibold border border-growth-200 dark:border-growth-800">
            ✓ {saveStatus}
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-2 border-b border-ink-200 dark:border-ink-800">
        {['profile', 'education', 'skills'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium text-sm transition-colors ${
              activeTab === tab
                ? 'text-iris-600 dark:text-iris-400 border-b-2 border-iris-500'
                : 'text-ink-500 dark:text-ink-400 hover:text-ink-700 dark:hover:text-ink-300'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && profile && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="surface max-w-2xl p-6"
        >
          <div className="flex items-center gap-4 mb-6">
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-iris-500 to-violet-600 flex items-center justify-center text-white text-xl font-bold">
              {(profile.user_username || 'S')?.[0]?.toUpperCase()}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50">
                {profile.user_first_name} {profile.user_last_name}
              </h2>
              <p className="text-sm text-iris-500">@{profile.user_username}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <EnvelopeIcon className="h-4 w-4 text-ink-400" />
              <span className="text-sm text-ink-500">{profile.user_email}</span>
            </div>

            <EditableField
              label="First Name"
              value={profile.user_first_name || ''}
              onChange={(val) => handleFieldSave('user_first_name', val)}
            />
            <EditableField
              label="Last Name"
              value={profile.user_last_name || ''}
              onChange={(val) => handleFieldSave('user_last_name', val)}
            />
            <EditableField
              label="Phone"
              value={profile.phone_number || ''}
              onChange={(val) => handleFieldSave('phone_number', val)}
              type="tel"
            />
            <EditableField
              label="Bio"
              value={profile.bio || ''}
              onChange={(val) => handleFieldSave('bio', val)}
            />
            <EditableField
              label="School/College"
              value={profile.school_or_college || ''}
              onChange={(val) => handleFieldSave('school_or_college', val)}
            />
            <EditableField
              label="Grade/Class"
              value={profile.grade_or_class || ''}
              onChange={(val) => handleFieldSave('grade_or_class', val)}
            />
          </div>
        </motion.div>
      )}

      {/* Education Tab */}
      {activeTab === 'education' && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="flex justify-end">
            <button
              onClick={() => setShowEduForm(!showEduForm)}
              className="btn-primary text-xs py-2 px-3"
            >
              {showEduForm ? 'Cancel' : '+ Add Education'}
            </button>
          </div>

          {showEduForm && (
            <form onSubmit={handleAddEducation} className="surface p-4 max-w-2xl space-y-3">
              <h3 className="font-semibold text-sm text-ink-900 dark:text-ink-100">New Education Entry</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-ink-500">Institution Name *</label>
                  <input
                    required
                    className="input w-full mt-1"
                    placeholder="e.g. Stanford University"
                    value={eduForm.institution_name}
                    onChange={(e) => setEduForm({ ...eduForm, institution_name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs text-ink-500">Degree / Level *</label>
                  <input
                    required
                    className="input w-full mt-1"
                    placeholder="e.g. B.Tech Computer Science"
                    value={eduForm.degree_or_level}
                    onChange={(e) => setEduForm({ ...eduForm, degree_or_level: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs text-ink-500">Field of Study</label>
                  <input
                    className="input w-full mt-1"
                    placeholder="e.g. Artificial Intelligence"
                    value={eduForm.field_of_study}
                    onChange={(e) => setEduForm({ ...eduForm, field_of_study: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs text-ink-500">GPA / Percentage</label>
                  <input
                    className="input w-full mt-1"
                    placeholder="e.g. 3.8 / 4.0 or 85%"
                    value={eduForm.percentage_or_gpa}
                    onChange={(e) => setEduForm({ ...eduForm, percentage_or_gpa: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-xs text-ink-500">Start Year</label>
                  <input
                    type="number"
                    className="input w-full mt-1"
                    value={eduForm.start_year}
                    onChange={(e) => setEduForm({ ...eduForm, start_year: parseInt(e.target.value) || 2020 })}
                  />
                </div>
                <div>
                  <label className="text-xs text-ink-500">End Year</label>
                  <input
                    type="number"
                    className="input w-full mt-1"
                    value={eduForm.end_year}
                    onChange={(e) => setEduForm({ ...eduForm, end_year: parseInt(e.target.value) || 2024 })}
                  />
                </div>
              </div>
              <button type="submit" className="btn-primary text-xs py-2 px-4 mt-2">
                Save Education
              </button>
            </form>
          )}

          {education.length === 0 ? (
            <div className="text-center py-12">
              <BookOpenIcon className="h-12 w-12 text-ink-300 dark:text-ink-600 mx-auto mb-3" />
              <p className="text-ink-500 dark:text-ink-400">No education records yet. Click "+ Add Education" above!</p>
            </div>
          ) : (
            <div className="space-y-4 max-w-2xl">
              {education.map((edu) => (
                <div key={edu.id} className="surface p-4">
                  <h3 className="font-semibold text-ink-900 dark:text-ink-50">{edu.institution_name}</h3>
                  <p className="text-sm text-iris-500">{edu.degree_or_level}</p>
                  {edu.field_of_study && <p className="text-xs text-ink-500">{edu.field_of_study}</p>}
                  <p className="text-xs text-ink-400 mt-2">
                    {edu.start_year} – {edu.end_year || 'Present'}
                  </p>
                  {edu.percentage_or_gpa && <p className="text-xs text-ink-400">GPA: {edu.percentage_or_gpa}</p>}
                </div>
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* Skills Tab */}
      {activeTab === 'skills' && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <div className="flex justify-end">
            <button
              onClick={() => setShowSkillForm(!showSkillForm)}
              className="btn-primary text-xs py-2 px-3"
            >
              {showSkillForm ? 'Cancel' : '+ Add Skill'}
            </button>
          </div>

          {showSkillForm && (
            <form onSubmit={handleAddSkill} className="surface p-4 max-w-2xl flex flex-wrap gap-3 items-end">
              <div className="flex-1 min-w-[200px]">
                <label className="text-xs text-ink-500">Skill Name *</label>
                <input
                  required
                  className="input w-full mt-1"
                  placeholder="e.g. Docker, React, PyTorch"
                  value={skillForm.skill_name}
                  onChange={(e) => setSkillForm({ ...skillForm, skill_name: e.target.value })}
                />
              </div>
              <div className="w-40">
                <label className="text-xs text-ink-500">Proficiency Level</label>
                <select
                  className="input w-full mt-1"
                  value={skillForm.proficiency}
                  onChange={(e) => setSkillForm({ ...skillForm, proficiency: e.target.value })}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>
              <button type="submit" className="btn-primary text-xs py-2.5 px-4">
                Add Skill
              </button>
            </form>
          )}

          {skills.length === 0 ? (
            <div className="text-center py-12">
              <SparklesIcon className="h-12 w-12 text-ink-300 dark:text-ink-600 mx-auto mb-3" />
              <p className="text-ink-500 dark:text-ink-400">No skills added yet. Add your skills or import them from your resume!</p>
            </div>
          ) : (
            <div className="space-y-3 max-w-2xl">
              {skills.map((skill) => (
                <div key={skill.id} className="surface p-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-ink-900 dark:text-ink-50">{skill.skill_name}</p>
                    <p className="text-xs text-ink-500 capitalize">{skill.proficiency}</p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${
                      skill.proficiency === 'advanced'
                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400'
                        : skill.proficiency === 'intermediate'
                        ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400'
                        : 'bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-400'
                    }`}
                  >
                    {skill.proficiency}
                  </span>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
