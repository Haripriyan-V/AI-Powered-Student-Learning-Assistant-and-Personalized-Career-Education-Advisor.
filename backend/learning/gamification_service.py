"""
Gamification Service: Central engine managing XP awards, leveling,
daily streaks, activity logging, and badge unlocks.
"""
from datetime import date, timedelta
from django.utils import timezone
import logging

from learning.models import StudentGamification, LearningActivity

logger = logging.getLogger(__name__)

# Configurable XP Rewards Table
XP_REWARDS = {
    'lesson': 20,
    'quiz': 30,
    'assessment': 50,
    'project': 100,
    'daily': 10,
    'streak': 25,
    'skill_gap': 75,
}

# Level Thresholds and Titles
LEVEL_TIERS = [
    (3000, 30, 'Career Ready Master'),
    (2000, 20, 'Career Ready'),
    (1200, 15, 'Advanced Practitioner'),
    (700, 10, 'Skill Builder'),
    (400, 7, 'Active Explorer'),
    (200, 5, 'Dedicated Learner'),
    (100, 2, 'Motivated Student'),
    (0, 1, 'Beginner'),
]

# Badge Definitions
BADGE_DEFINITIONS = [
    {
        'id': 'first_course',
        'title': 'First Step',
        'description': 'Enrolled in your first learning course',
        'icon': '🏆',
    },
    {
        'id': 'quiz_champion',
        'title': 'Quiz Champion',
        'description': 'Passed 3 quizzes with high accuracy',
        'icon': '🧠',
    },
    {
        'id': 'streak_7',
        'title': '7-Day Streak',
        'description': 'Maintained a 7-day continuous learning streak',
        'icon': '🔥',
    },
    {
        'id': 'skill_gap_crusher',
        'title': 'Skill Gap Crusher',
        'description': 'Closed a critical or major skill gap',
        'icon': '🎯',
    },
    {
        'id': 'resume_pro',
        'title': 'Resume Ready',
        'description': 'Analyzed and aligned your resume with your target career',
        'icon': '📄',
    },
    {
        'id': 'career_ready',
        'title': 'Career Ready',
        'description': 'Attained 75%+ overall career readiness',
        'icon': '🚀',
    },
]


class GamificationService:
    """Central manager for student gamification state and rewards."""

    @classmethod
    def get_or_create_profile(cls, student) -> StudentGamification:
        profile, _ = StudentGamification.objects.get_or_create(
            student=student,
            defaults={
                'xp': 50,  # Welcome bonus
                'level': 1,
                'level_title': 'Beginner',
                'current_streak': 1,
                'longest_streak': 1,
                'last_active_date': timezone.now().date(),
                'unlocked_badges': [{'id': 'first_course', 'unlocked_at': str(timezone.now().date())}],
            }
        )
        return profile

    @classmethod
    def award_xp(cls, student, activity_type: str, title: str, xp_amount: int = None, metadata: dict = None) -> dict:
        """
        Awards XP for a verified activity, updates streaks, checks level,
        and logs the learning event.
        """
        profile = cls.get_or_create_profile(student)
        today = timezone.now().date()

        # Determine XP amount
        if xp_amount is None:
            xp_amount = XP_REWARDS.get(activity_type, 15)

        # Update streak
        last_date = profile.last_active_date
        if last_date:
            diff = (today - last_date).days
            if diff == 1:
                profile.current_streak += 1
                if profile.current_streak > profile.longest_streak:
                    profile.longest_streak = profile.current_streak
            elif diff > 1:
                profile.current_streak = 1
        else:
            profile.current_streak = 1
            profile.longest_streak = 1

        profile.last_active_date = today

        # Add XP
        old_level = profile.level
        profile.xp += xp_amount

        # Check new level
        new_level = 1
        new_title = 'Beginner'
        for threshold, lvl, tier_title in LEVEL_TIERS:
            if profile.xp >= threshold:
                new_level = lvl
                new_title = tier_title
                break

        profile.level = new_level
        profile.level_title = new_title
        profile.save()

        # Log activity
        LearningActivity.objects.create(
            student=student,
            activity_type=activity_type,
            title=title,
            xp_awarded=xp_amount,
            metadata=metadata or {},
        )

        # Check badges
        cls.check_badges(student, profile)

        return {
            'xp_awarded': xp_amount,
            'total_xp': profile.xp,
            'level': profile.level,
            'level_title': profile.level_title,
            'current_streak': profile.current_streak,
            'leveled_up': new_level > old_level,
        }

    @classmethod
    def check_badges(cls, student, profile=None):
        if not profile:
            profile = cls.get_or_create_profile(student)

        unlocked_ids = {b.get('id') for b in profile.unlocked_badges}
        today_str = str(timezone.now().date())
        new_unlocked = False

        # Check 7-day streak
        if profile.current_streak >= 7 and 'streak_7' not in unlocked_ids:
            profile.unlocked_badges.append({'id': 'streak_7', 'unlocked_at': today_str})
            new_unlocked = True

        # Check quiz champion (passed 3+ quizzes)
        passed_quizzes = student.quiz_attempts.filter(passed=True).count()
        if passed_quizzes >= 3 and 'quiz_champion' not in unlocked_ids:
            profile.unlocked_badges.append({'id': 'quiz_champion', 'unlocked_at': today_str})
            new_unlocked = True

        # Check resume badge
        if student.resume_analyses.exists() and 'resume_pro' not in unlocked_ids:
            profile.unlocked_badges.append({'id': 'resume_pro', 'unlocked_at': today_str})
            new_unlocked = True

        # Check career ready badge (from skill gap analysis)
        latest_gap = student.skill_gap_analyses.first()
        if latest_gap and latest_gap.readiness_score >= 75 and 'career_ready' not in unlocked_ids:
            profile.unlocked_badges.append({'id': 'career_ready', 'unlocked_at': today_str})
            new_unlocked = True

        if new_unlocked:
            profile.save(update_fields=['unlocked_badges'])

    @classmethod
    def get_summary(cls, student) -> dict:
        profile = cls.get_or_create_profile(student)
        today = timezone.now().date()

        # Calculate XP progress to next level
        next_threshold = 3000
        for threshold, lvl, _ in reversed(LEVEL_TIERS):
            if threshold > profile.xp:
                next_threshold = threshold
                break

        # Badges list enriched with metadata
        unlocked_lookup = {b.get('id'): b.get('unlocked_at') for b in profile.unlocked_badges}
        enriched_badges = []
        for badge_def in BADGE_DEFINITIONS:
            is_unlocked = badge_def['id'] in unlocked_lookup
            enriched_badges.append({
                **badge_def,
                'unlocked': is_unlocked,
                'unlocked_at': unlocked_lookup.get(badge_def['id']),
            })

        # Recent activities
        recent_acts = list(
            LearningActivity.objects.filter(student=student)
            .order_by('-created_at')[:8]
            .values('id', 'activity_type', 'title', 'xp_awarded', 'created_at')
        )

        return {
            'xp': profile.xp,
            'level': profile.level,
            'level_title': profile.level_title,
            'next_level_xp': next_threshold,
            'current_streak': profile.current_streak,
            'longest_streak': profile.longest_streak,
            'last_active_date': profile.last_active_date,
            'badges': enriched_badges,
            'recent_activities': recent_acts,
        }
