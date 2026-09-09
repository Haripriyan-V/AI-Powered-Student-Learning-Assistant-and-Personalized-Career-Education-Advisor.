import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BellIcon, XMarkIcon } from '@heroicons/react/24/outline';

export default function Notifications() {
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'achievement',
      title: 'Course Completed!',
      message: 'You have successfully completed "Python Basics"',
      timestamp: new Date(Date.now() - 3600000),
      read: false,
    },
    {
      id: 2,
      type: 'recommendation',
      title: 'New Recommendation',
      message: 'Based on your skills, check out "Data Science Path"',
      timestamp: new Date(Date.now() - 7200000),
      read: false,
    },
    {
      id: 3,
      type: 'message',
      title: 'New Message',
      message: 'You have a new message from your career counselor',
      timestamp: new Date(Date.now() - 86400000),
      read: true,
    },
    {
      id: 4,
      type: 'scholarship',
      title: 'Scholarship Alert',
      message: 'New scholarship opportunity: "STEM Excellence Award"',
      timestamp: new Date(Date.now() - 172800000),
      read: true,
    },
  ]);

  const handleDismiss = (id) => {
    setNotifications(notifications.filter((n) => n.id !== id));
  };

  const handleMarkAsRead = (id) => {
    setNotifications(
      notifications.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  const getIcon = (type) => {
    const icons = {
      achievement: '🏆',
      recommendation: '💡',
      message: '💬',
      scholarship: '🎓',
    };
    return icons[type] || '🔔';
  };

  const getColor = (type) => {
    const colors = {
      achievement: 'bg-growth-50 dark:bg-growth-900/20 border-growth-200 dark:border-growth-800',
      recommendation: 'bg-iris-50 dark:bg-iris-900/20 border-iris-200 dark:border-iris-800',
      message: 'bg-marigold-50 dark:bg-marigold-900/20 border-marigold-200 dark:border-marigold-800',
      scholarship: 'bg-violet-50 dark:bg-violet-900/20 border-violet-200 dark:border-violet-800',
    };
    return colors[type] || 'bg-ink-50 dark:bg-ink-900/20 border-ink-200 dark:border-ink-800';
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50 mb-1">Notifications</h1>
      <p className="text-sm text-ink-500 dark:text-ink-400 mb-6">
        {unreadCount > 0
          ? `You have ${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`
          : 'All caught up!'}
      </p>

      <div className="max-w-2xl">
        {notifications.length === 0 ? (
          <div className="text-center py-12">
            <BellIcon className="h-12 w-12 text-ink-300 dark:text-ink-600 mx-auto mb-3" />
            <p className="text-ink-500 dark:text-ink-400">No notifications yet.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {notifications.map((notif, idx) => (
              <motion.div
                key={notif.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className={`border rounded-xl p-4 flex items-start gap-4 ${getColor(notif.type)} ${
                  !notif.read ? 'ring-1 ring-iris-300 dark:ring-iris-700' : ''
                }`}
              >
                {/* Icon */}
                <div className="text-2xl flex-shrink-0 mt-1">{getIcon(notif.type)}</div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <h3
                    className={`font-semibold text-ink-900 dark:text-ink-50 ${
                      !notif.read ? 'font-bold' : ''
                    }`}
                  >
                    {notif.title}
                    {!notif.read && <span className="ml-2 text-xs font-bold text-iris-600 dark:text-iris-400">NEW</span>}
                  </h3>
                  <p className="text-sm text-ink-600 dark:text-ink-400 mt-1 line-clamp-2">
                    {notif.message}
                  </p>
                  <p className="text-xs text-ink-400 dark:text-ink-500 mt-2">
                    {formatTime(notif.timestamp)}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {!notif.read && (
                    <button
                      onClick={() => handleMarkAsRead(notif.id)}
                      className="p-1 hover:bg-white/50 dark:hover:bg-white/10 rounded transition-colors"
                      title="Mark as read"
                    >
                      <div className="h-3 w-3 rounded-full bg-iris-500" />
                    </button>
                  )}
                  <button
                    onClick={() => handleDismiss(notif.id)}
                    className="p-1 hover:bg-white/50 dark:hover:bg-white/10 rounded transition-colors"
                    title="Dismiss"
                  >
                    <XMarkIcon className="h-4 w-4 text-ink-400" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function formatTime(date) {
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}
