import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BellIcon, ShieldCheckIcon, SwatchIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

export default function Settings() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    notifications: true,
    newsletter: false,
  });

  useEffect(() => {
    api
      .get('/students/profile/me/')
      .then((res) => {
        const userData = res.data;
        setUser(userData);
        setFormData({
          firstName: userData.first_name || userData.user_first_name || '',
          lastName: userData.last_name || userData.user_last_name || '',
          email: userData.email || userData.user_email || '',
          phone: userData.phone || userData.phone_number || '',
          notifications: true,
          newsletter: false,
        });
      })
      .catch((err) => {
        console.error('Error loading profile:', err);
        setError('Failed to load settings.');
      })
      .finally(() => setLoading(false));
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setSuccess(null);
    setError(null);

    try {
      await api.patch('/students/profile/me/', {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
      });

      // Update cached user object for Navbar
      const stored = localStorage.getItem('disha_user');
      if (stored) {
        try {
          const userObj = JSON.parse(stored);
          userObj.first_name = formData.firstName;
          userObj.last_name = formData.lastName;
          userObj.email = formData.email;
          localStorage.setItem('disha_user', JSON.stringify(userObj));
        } catch (e) {}
      }

      setSuccess('Settings saved successfully!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loader label="Loading settings…" size="lg" />;

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50 mb-1">Settings</h1>
      <p className="text-sm text-ink-500 dark:text-ink-400 mb-6">
        Manage your account preferences and settings.
      </p>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-900/20 dark:border-rose-800 p-4 text-sm text-rose-600 dark:text-rose-400 mb-6"
        >
          {error}
        </motion.div>
      )}

      {success && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl border border-growth-200 bg-growth-50 dark:bg-growth-900/20 dark:border-growth-800 p-4 text-sm text-growth-600 dark:text-growth-400 mb-6"
        >
          {success}
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Account Settings */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2 space-y-6"
        >
          {/* Profile Information */}
          <div className="surface p-6">
            <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50 mb-4 flex items-center gap-2">
              <UserGroupIcon className="h-5 w-5" />
              Profile Information
            </h2>

            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-ink-700 dark:text-ink-300 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    className="input w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-ink-700 dark:text-ink-300 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    className="input w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-ink-700 dark:text-ink-300 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="input w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-ink-700 dark:text-ink-300 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="input w-full"
                />
              </div>

              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-primary w-full"
              >
                {saving ? 'Saving…' : 'Save Changes'}
              </button>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="surface p-6">
            <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50 mb-4 flex items-center gap-2">
              <BellIcon className="h-5 w-5" />
              Notifications
            </h2>

            <div className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-ink-50 dark:hover:bg-ink-900/50 transition-colors">
                <input
                  type="checkbox"
                  name="notifications"
                  checked={formData.notifications}
                  onChange={handleInputChange}
                  className="w-4 h-4"
                />
                <div className="flex-1">
                  <p className="font-medium text-ink-900 dark:text-ink-50">Email Notifications</p>
                  <p className="text-sm text-ink-500 dark:text-ink-400">
                    Get updates about courses, assessments, and recommendations
                  </p>
                </div>
              </label>

              <label className="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-ink-50 dark:hover:bg-ink-900/50 transition-colors">
                <input
                  type="checkbox"
                  name="newsletter"
                  checked={formData.newsletter}
                  onChange={handleInputChange}
                  className="w-4 h-4"
                />
                <div className="flex-1">
                  <p className="font-medium text-ink-900 dark:text-ink-50">Newsletter</p>
                  <p className="text-sm text-ink-500 dark:text-ink-400">
                    Receive curated tips, insights, and learning resources
                  </p>
                </div>
              </label>
            </div>
          </div>
        </motion.div>

        {/* Quick Settings Sidebar */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-4"
        >
          {/* Appearance */}
          <div className="surface p-6">
            <h3 className="font-semibold text-ink-900 dark:text-ink-50 mb-4 flex items-center gap-2">
              <SwatchIcon className="h-5 w-5" />
              Appearance
            </h3>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="theme" value="system" defaultChecked className="w-4 h-4" />
                <span className="text-sm text-ink-600 dark:text-ink-400">System</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="theme" value="light" className="w-4 h-4" />
                <span className="text-sm text-ink-600 dark:text-ink-400">Light</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="radio" name="theme" value="dark" className="w-4 h-4" />
                <span className="text-sm text-ink-600 dark:text-ink-400">Dark</span>
              </label>
            </div>
          </div>

          {/* Security */}
          <div className="surface p-6">
            <h3 className="font-semibold text-ink-900 dark:text-ink-50 mb-4 flex items-center gap-2">
              <ShieldCheckIcon className="h-5 w-5" />
              Security
            </h3>
            <button className="btn-secondary w-full text-sm">
              Change Password
            </button>
            <button className="btn-secondary w-full text-sm mt-2">
              Manage Sessions
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
