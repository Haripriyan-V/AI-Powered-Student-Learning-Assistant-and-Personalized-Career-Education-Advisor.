import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Logo from '../../components/common/Logo';
import { ROUTES } from '../../utils/constants';
import api from '../../services/api';
import { tokenStorage } from '../../utils/tokenStorage';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '', password2: '' });
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
      const data = err?.response?.data;
      if (typeof data === 'string') {
        setError(data);
      } else if (data?.detail) {
        setError(data.detail);
      } else if (data && typeof data === 'object') {
        const messages = Object.entries(data)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(' ') : val}`)
          .join(' | ');
        setError(messages || 'Registration failed');
      } else {
        setError('Registration failed. Please check your details and try again.');
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
          <input name="password" type="password" className="input mt-1 w-full" value={form.password} onChange={handleChange} required />

          <label className="block text-sm text-ink-600 mt-4">Confirm password</label>
          <input name="password2" type="password" className="input mt-1 w-full" value={form.password2} onChange={handleChange} required />

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
