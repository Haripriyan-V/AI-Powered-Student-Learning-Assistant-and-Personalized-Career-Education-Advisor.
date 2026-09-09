import clsx from 'clsx';

/**
 * Disha AI brand mark - a compass-needle pointing along a "path",
 * echoing the trail/direction motif used throughout the roadmap & sidebar.
 */
export default function Logo({ size = 'md', withWordmark = true, className }) {
  const sizes = {
    sm: { box: 28, text: 'text-base' },
    md: { box: 34, text: 'text-lg' },
    lg: { box: 44, text: 'text-2xl' },
  };
  const { box, text } = sizes[size] || sizes.md;

  return (
    <div className={clsx('flex items-center gap-2.5 select-none', className)}>
      <svg width={box} height={box} viewBox="0 0 32 32" fill="none" className="shrink-0">
        <rect width="32" height="32" rx="9" className="fill-iris-500" />
        <circle cx="16" cy="16" r="9.5" stroke="white" strokeWidth="1.4" opacity="0.5" />
        <path d="M16 7.5 L20 16 L16 24.5 L12 16 Z" className="fill-marigold-400" />
        <path d="M16 7.5 L20 16 L16 16 Z" fill="white" />
      </svg>
      {withWordmark && (
        <span className={clsx('font-display font-semibold tracking-tight text-ink-900 dark:text-ink-50', text)}>
          Disha<span className="text-iris-500">AI</span>
        </span>
      )}
    </div>
  );
}
