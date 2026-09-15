from django.contrib import admin
from .models import (
    Subject, Course, LearningResource, Quiz, Question, Choice,
    QuizAttempt, StudentProgress, Scholarship, College,
    EntranceExam, StudyTask, LearningRoadmap, RoadmapItem,
    StudentGamification, LearningActivity,
)


class LearningResourceInline(admin.TabularInline):
    model = LearningResource
    extra = 1


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'level', 'duration_hours', 'is_published', 'created_at')
    list_filter = ('level', 'is_published', 'subject')
    search_fields = ('title', 'description')
    inlines = [LearningResourceInline]


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'resource_type', 'order')
    list_filter = ('resource_type',)
    search_fields = ('title',)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    inlines = [ChoiceInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'passing_score', 'created_at')
    inlines = [QuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'passed', 'started_at')
    list_filter = ('passed',)
    search_fields = ('student__username', 'quiz__title')


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress_percent', 'last_accessed')
    list_filter = ('status',)
    search_fields = ('student__username', 'course__title')


# ---------------------------------------------------------------------------
# Scholarship admin
# ---------------------------------------------------------------------------

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'scholarship_type', 'amount', 'deadline', 'is_active')
    list_filter = ('scholarship_type', 'is_active')
    search_fields = ('name', 'provider', 'eligibility')
    list_editable = ('is_active',)
    date_hierarchy = 'deadline'


# ---------------------------------------------------------------------------
# College admin
# ---------------------------------------------------------------------------

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'college_type', 'ranking', 'established_year', 'is_active')
    list_filter = ('college_type', 'is_active')
    search_fields = ('name', 'location', 'affiliation')
    list_editable = ('is_active',)
    ordering = ('ranking', 'name')


# ---------------------------------------------------------------------------
# Entrance Exams admin
# ---------------------------------------------------------------------------

@admin.register(EntranceExam)
class EntranceExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'conducting_body', 'exam_category', 'application_period', 'is_active')
    list_filter = ('exam_category', 'is_active')
    search_fields = ('name', 'conducting_body', 'eligibility', 'syllabus_summary')
    list_editable = ('is_active',)
    filter_horizontal = ('related_career_paths',)


# ---------------------------------------------------------------------------
# Study Planner Tasks admin
# ---------------------------------------------------------------------------

@admin.register(StudyTask)
class StudyTaskAdmin(admin.ModelAdmin):
    list_display = ('student', 'task', 'priority', 'status', 'completed', 'scheduled_date', 'created_at')
    list_filter = ('completed', 'priority', 'status', 'scheduled_date')
    search_fields = ('student__username', 'task', 'notes')
    list_editable = ('completed',)


# ---------------------------------------------------------------------------
# Learning Roadmap admin
# ---------------------------------------------------------------------------

class RoadmapItemInline(admin.TabularInline):
    model = RoadmapItem
    extra = 0
    fields = ('phase_number', 'title', 'difficulty', 'estimated_hours', 'status', 'completion_percent')


@admin.register(LearningRoadmap)
class LearningRoadmapAdmin(admin.ModelAdmin):
    list_display = ('student', 'career_path', 'title', 'overall_progress', 'active_phase', 'updated_at')
    list_filter = ('career_path', 'active_phase')
    search_fields = ('student__username', 'title', 'career_path__title')
    inlines = [RoadmapItemInline]


@admin.register(RoadmapItem)
class RoadmapItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'phase_number', 'difficulty', 'status', 'completion_percent')
    list_filter = ('difficulty', 'status', 'phase_number')
    search_fields = ('title', 'description', 'roadmap__student__username')


# ---------------------------------------------------------------------------
# Student Gamification & Learning Activity admin
# ---------------------------------------------------------------------------

@admin.register(StudentGamification)
class StudentGamificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'level', 'level_title', 'xp', 'current_streak', 'longest_streak', 'last_active_date')
    search_fields = ('student__username', 'level_title')


@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity_type', 'title', 'xp_awarded', 'created_at')
    list_filter = ('activity_type',)
    search_fields = ('student__username', 'title')

