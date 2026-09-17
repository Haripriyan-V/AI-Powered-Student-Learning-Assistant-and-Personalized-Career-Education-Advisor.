import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import Logo from '../../components/common/Logo';
import { ROUTES } from '../../utils/constants';
import api from '../../services/api';
import { tokenStorage } from '../../utils/tokenStorage';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const { data } = await api.post('/accounts/register/', form);
      // Auto-login after register
      const loginResp = await api.post('/accounts/login/', { username: form.username, password: form.password });
      tokenStorage.setTokens({ access: loginResp.data.access, refresh: loginResp.data.refresh });
      tokenStorage.setUser(loginResp.data.user);
      navigate(ROUTES.DASHBOARD);
    } catch (err) {
      if (!err?.response) {
        setError('Unable to connect to the server. Please check your internet connection and try again.');
      } else if (err.response.status >= 500) {
        setError('Server error. Please try again later.');
      } else {
        const data = err.response.data;
        if (typeof data === 'string') {
          setError(data);
        } else if (data?.detail) {
          setError(data.detail);
        } else if (data && typeof data === 'object') {
          const messages = Object.entries(data)
            .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(' ') : val}`)
            .join(' | ');
          setError(messages || 'Registration failed.');
        } else {
          setError('Registration failed. Please check your details and try again.');
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-25 dark:bg-ink-950 px-6">
      <div className="surface w-full max-w-sm p-8">
        <div className="text-center">
          <Logo className="justify-center" />
          <h1 className="mt-5 text-lg font-semibold text-ink-900 dark:text-ink-50">Create your account</h1>
        </div>

        <form className="mt-6" onSubmit={handleSubmit}>
          <label className="block text-sm text-ink-600">Username</label>
          <input name="username" className="input mt-1 w-full" value={form.username} onChange={handleChange} required />

          <label className="block text-sm text-ink-600 mt-4">Email</label>
          <input name="email" type="email" className="input mt-1 w-full" value={form.email} onChange={handleChange} required />

          <label className="block text-sm text-ink-600 mt-4">Password</label>
          <div className="relative mt-1">
            <input
              name="password"
              type={showPassword ? 'text' : 'password'}
              className="input w-full pr-10"
              value={form.password}
              onChange={handleChange}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-ink-400 dark:text-ink-200 hover:text-iris-600 dark:hover:text-iris-400 active:text-iris-700 dark:active:text-iris-300 focus:outline-none focus-visible:text-iris-600 dark:focus-visible:text-iris-400 transition-colors"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5" aria-hidden="true" />
              ) : (
                <EyeIcon className="h-5 w-5" aria-hidden="true" />
              )}
            </button>
          </div>

          <label className="block text-sm text-ink-600 mt-4">Confirm password</label>
          <div className="relative mt-1">
            <input
              name="password2"
              type={showConfirmPassword ? 'text' : 'password'}
              className="input w-full pr-10"
              value={form.password2}
              onChange={handleChange}
              required
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword((prev) => !prev)}
              className="absolute inset-y-0 right-0 flex items-center pr-3 text-ink-400 dark:text-ink-200 hover:text-iris-600 dark:hover:text-iris-400 active:text-iris-700 dark:active:text-iris-300 focus:outline-none focus-visible:text-iris-600 dark:focus-visible:text-iris-400 transition-colors"
              aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
            >
              {showConfirmPassword ? (
                <EyeSlashIcon className="h-5 w-5" aria-hidden="true" />
              ) : (
                <EyeIcon className="h-5 w-5" aria-hidden="true" />
              )}
            </button>
          </div>

          {error && <div className="text-sm text-red-600 mt-3">{error}</div>}

          <button className="btn-primary mt-6 w-full" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>

        <p className="mt-4 text-sm text-ink-500 dark:text-ink-400 text-center">
          Already have an account?{' '}
          <Link to={ROUTES.LOGIN} className="font-medium text-iris-500 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
