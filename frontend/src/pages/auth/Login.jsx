import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import Logo from '../../components/common/Logo';
import { ROUTES } from '../../utils/constants';
import api from '../../services/api';
import { tokenStorage } from '../../utils/tokenStorage';

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const { data } = await api.post('/accounts/login/', { username, password });
      tokenStorage.setTokens({ access: data.access, refresh: data.refresh });
      tokenStorage.setUser(data.user);
      navigate(ROUTES.DASHBOARD);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-25 dark:bg-ink-950 px-6">
      <div className="surface w-full max-w-sm p-8">
        <div className="text-center">
          <Logo className="justify-center" />
          <h1 className="mt-5 text-lg font-semibold text-ink-900 dark:text-ink-50">Welcome back</h1>
        </div>

        <form className="mt-6" onSubmit={handleSubmit}>
          <label className="block text-sm text-ink-600">Username or email</label>
          <input
            className="input mt-1 w-full"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label className="block text-sm text-ink-600 mt-4">Password</label>
          <input
            type="password"
            className="input mt-1 w-full"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <div className="text-sm text-red-600 mt-3">{error}</div>}

          <button className="btn-primary mt-6 w-full" type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>

        <p className="mt-4 text-sm text-ink-500 dark:text-ink-400 text-center">
          No account?{' '}
          <Link to={ROUTES.REGISTER} className="font-medium text-iris-500 hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
