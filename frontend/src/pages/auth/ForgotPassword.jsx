import { Link } from 'react-router-dom';
import Logo from '../../components/common/Logo';
import { ROUTES } from '../../utils/constants';

export default function ForgotPassword() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-25 dark:bg-ink-950 px-6">
      <div className="surface w-full max-w-sm p-8 text-center">
        <Logo className="justify-center" />
        <h1 className="mt-5 text-lg font-semibold text-ink-900 dark:text-ink-50">Reset your password</h1>
        <p className="mt-1.5 text-sm text-ink-500 dark:text-ink-400">
          Password reset flow arrives in the Authentication phase.
        </p>
        <Link to={ROUTES.LOGIN} className="btn-secondary mt-6 w-full">
          Back to login
        </Link>
      </div>
    </div>
  );
}
