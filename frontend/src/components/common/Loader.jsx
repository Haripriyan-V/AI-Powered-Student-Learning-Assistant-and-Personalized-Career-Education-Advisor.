import clsx from 'clsx';

export function Loader({ label = 'Loading...', size = 'md' }) {
  const dims = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-9 w-9' };
  return (
    <div className="flex items-center justify-center gap-2.5 py-10 text-ink-400">
      <span
        className={clsx('animate-spin rounded-full border-2 border-ink-200 border-t-iris-500 dark:border-ink-700', dims[size])}
      />
      {label && <span className="text-sm font-medium">{label}</span>}
    </div>
  );
}

export function Skeleton({ className }) {
  return <div className={clsx('animate-pulse rounded-lg bg-ink-100 dark:bg-ink-800', className)} />;
}

export function PageLoader() {
  return (
    <div className="flex h-[60vh] w-full items-center justify-center">
      <Loader label="Charting your path..." size="lg" />
    </div>
  );
}
