from django.contrib import admin
from .models import (
    Subject, Course, LearningResource, Quiz, Question, Choice,
    QuizAttempt, StudentProgress, Scholarship, College,
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
