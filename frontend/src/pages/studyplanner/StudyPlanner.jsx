import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CalendarDaysIcon, CheckCircleIcon, PlusIcon } from '@heroicons/react/24/outline';
import api from '../../services/api';
import { Loader } from '../../components/common/Loader';

export default function StudyPlanner() {
  const [loading, setLoading] = useState(true);
  const [todaysGoals, setTodaysGoals] = useState([]);
  const [weeklySchedule, setWeeklySchedule] = useState([]);
  const [totalHours, setTotalHours] = useState(0);
  const [newGoal, setNewGoal] = useState('');
  const [toggleMsg, setToggleMsg] = useState(null);

  useEffect(() => {
    fetchPlannerData();
  }, []);

  const fetchPlannerData = async () => {
    try {
      const res = await api.get('/learning/planner/');
      if (res.data) {
        setTodaysGoals(res.data.goals || []);
        setWeeklySchedule(res.data.weekly_schedule || []);
        setTotalHours(res.data.total_hours || 0);
      }
    } catch (err) {
      console.error('Failed to load study planner:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddGoal = async () => {
    if (!newGoal.trim()) return;
    try {
      const res = await api.post('/learning/planner/', { task: newGoal.trim() });
      if (res.data?.task) {
        const newTask = {
          id: `db-${res.data.task.id}`,
          task_db_id: res.data.task.id,
          task: res.data.task.task,
          completed: false,
          hours: 0.5,
          day: 'Today',
          is_custom: true,
        };
        setTodaysGoals([...todaysGoals, newTask]);
        setNewGoal('');
        if (res.data.message) {
          setToggleMsg(res.data.message);
          setTimeout(() => setToggleMsg(null), 3000);
        }
      }
    } catch (err) {
      console.error('Failed to save study goal to backend:', err);
      // Fallback local update if network issue
      const fallbackTask = {
        id: `custom-${Date.now()}`,
        task: newGoal.trim(),
        completed: false,
        hours: 0.5,
      };
      setTodaysGoals([...todaysGoals, fallbackTask]);
      setNewGoal('');
    }
  };

  const handleToggleGoal = async (goal) => {
    const nextCompleted = !goal.completed;
    // Optimistic UI update
    setTodaysGoals((prev) =>
      prev.map((g) => (g.id === goal.id ? { ...g, completed: nextCompleted } : g))
    );

    try {
      const res = await api.post('/learning/planner/toggle/', {
        task_id: goal.id,
        completed: nextCompleted,
      });
      if (res.data?.message) {
        setToggleMsg(res.data.message);
        setTimeout(() => setToggleMsg(null), 3000);
      }
    } catch (err) {
      console.error('Failed to toggle study task:', err);
    }
  };

  const completedCount = todaysGoals.filter((g) => g.completed).length;
  const completedPercent = todaysGoals.length > 0 ? Math.round((completedCount / todaysGoals.length) * 100) : 0;

  if (loading) {
    return <Loader label="Loading personalized study plan…" size="lg" />;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900 dark:text-ink-50 mb-1">Study Planner</h1>
          <p className="text-sm text-ink-500 dark:text-ink-400">
            Plan your study sessions and track daily progress toward your target career.
          </p>
        </div>
        {toggleMsg && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-xs px-3 py-1.5 rounded-lg bg-growth-50 dark:bg-growth-900/30 text-growth-700 dark:text-growth-400 border border-growth-200 dark:border-growth-800 font-semibold"
          >
            {toggleMsg}
          </motion.div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Goals */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-2"
        >
          <div className="surface p-6 mb-6">
            <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50 mb-4">Today's Goals</h2>

            {/* Progress */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm font-medium text-ink-600 dark:text-ink-400">
                  {completedCount} of {todaysGoals.length} completed
                </p>
                <p className="text-sm font-bold text-iris-600 dark:text-iris-400">{completedPercent}%</p>
              </div>
              <div className="w-full bg-ink-200 dark:bg-ink-700 rounded-full h-3">
                <div
                  className="bg-iris-500 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${completedPercent}%` }}
                />
              </div>
            </div>

            {/* Goals List */}
            <div className="space-y-2 mb-4">
              {todaysGoals.length === 0 ? (
                <p className="text-sm text-ink-500 py-4 text-center">No tasks scheduled for today. Add a new goal below!</p>
              ) : (
                todaysGoals.map((goal) => (
                  <div
                    key={goal.id}
                    onClick={() => handleToggleGoal(goal)}
                    className={`p-3.5 rounded-xl cursor-pointer transition-colors border ${
                      goal.completed
                        ? 'bg-growth-50 dark:bg-growth-900/20 border-growth-200 dark:border-growth-800/60'
                        : 'bg-ink-50 dark:bg-ink-900/50 hover:bg-ink-100 dark:hover:bg-ink-900 border-ink-100 dark:border-ink-800'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div
                          className={`h-5 w-5 rounded-full border-2 flex-shrink-0 flex items-center justify-center ${
                            goal.completed
                              ? 'bg-growth-500 border-growth-500'
                              : 'border-ink-300 dark:border-ink-600'
                          }`}
                        >
                          {goal.completed && <CheckCircleIcon className="h-4 w-4 text-white" />}
                        </div>
                        <div>
                          <p
                            className={`text-sm font-medium ${
                              goal.completed
                                ? 'text-growth-700 dark:text-growth-400 line-through'
                                : 'text-ink-900 dark:text-ink-50'
                            }`}
                          >
                            {goal.task}
                          </p>
                          {goal.skill_name && (
                            <span className="text-[10px] text-iris-600 dark:text-iris-400 font-semibold uppercase tracking-wider">
                              Target Skill: {goal.skill_name}
                            </span>
                          )}
                        </div>
                      </div>
                      {goal.estimated_minutes && (
                        <span className="text-xs text-ink-400 shrink-0">
                          {goal.estimated_minutes} min
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Add New Goal */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleAddGoal();
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                placeholder="Add a custom study goal…"
                className="flex-1 input"
              />
              <button type="submit" className="btn-primary flex items-center justify-center px-4">
                <PlusIcon className="h-4 w-4" />
              </button>
            </form>
          </div>
        </motion.div>

        {/* Weekly Schedule */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="surface p-6 h-fit"
        >
          <h2 className="text-lg font-semibold text-ink-900 dark:text-ink-50 mb-4 flex items-center gap-2">
            <CalendarDaysIcon className="h-5 w-5" />
            This Week
          </h2>

          <div className="space-y-3">
            {weeklySchedule.map((item) => (
              <div key={item.day} className="p-3 rounded-lg bg-ink-50 dark:bg-ink-900/50">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs font-semibold text-iris-600 dark:text-iris-400">{item.day}</p>
                  <span className="text-[10px] text-ink-400">{item.hours} hrs</span>
                </div>
                <p className="text-xs text-ink-600 dark:text-ink-300 font-medium">{item.focus}</p>
              </div>
            ))}
          </div>

          <div className="mt-4 p-3 rounded-lg bg-growth-50 dark:bg-growth-900/20 border border-growth-200 dark:border-growth-800">
            <p className="text-xs font-medium text-growth-700 dark:text-growth-400 mb-1">Total Planned Hours</p>
            <p className="text-xl font-bold text-growth-600 dark:text-growth-400">{totalHours} hrs</p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
