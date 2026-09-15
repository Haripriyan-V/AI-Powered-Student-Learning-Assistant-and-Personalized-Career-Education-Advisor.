from rest_framework import serializers
from .models import (
    Subject, Course, LearningResource, Quiz, Question, Choice,
    QuizAttempt, StudentProgress, Scholarship, College,
    EntranceExam, StudyTask,
)


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'description')


class LearningResourceSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = LearningResource
        fields = ('id', 'course', 'course_title', 'title', 'resource_type', 'url', 'file', 'content', 'order')
        read_only_fields = ('id',)


class CourseSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    resources = LearningResourceSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'description', 'subject', 'subject_name', 'level',
            'duration_hours', 'thumbnail', 'created_by', 'created_by_username',
            'is_published', 'resources', 'created_at', 'updated_at',
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for course list views (no nested resources)."""
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'description', 'subject', 'subject_name',
            'level', 'duration_hours', 'thumbnail', 'is_published', 'created_at',
        )


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ('id', 'text', 'is_correct')


class ChoicePublicSerializer(serializers.ModelSerializer):
    """Hides `is_correct` so students can't see answers before submitting."""
    class Meta:
        model = Choice
        fields = ('id', 'text')


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'quiz', 'text', 'order', 'choices')


class QuestionPublicSerializer(serializers.ModelSerializer):
    choices = ChoicePublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'order', 'choices')


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'course', 'title', 'description', 'passing_score', 'questions', 'created_at')


class QuizPublicSerializer(serializers.ModelSerializer):
    """Used when a student is about to attempt the quiz (answers hidden)."""
    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'course', 'title', 'description', 'passing_score', 'questions')


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = ('id', 'student', 'quiz', 'quiz_title', 'score', 'passed', 'started_at', 'completed_at')
        read_only_fields = ('student', 'score', 'passed', 'started_at', 'completed_at')


class QuizSubmissionSerializer(serializers.Serializer):
    """Payload for submitting answers: {"answers": {"<question_id>": <choice_id>, ...}}"""
    answers = serializers.DictField(child=serializers.IntegerField())


class StudentProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = StudentProgress
        fields = ('id', 'student', 'course', 'course_title', 'status', 'progress_percent', 'last_accessed')
        read_only_fields = ('student', 'last_accessed')


# ---------------------------------------------------------------------------
# Scholarship serializers
# ---------------------------------------------------------------------------

class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = (
            'id', 'name', 'provider', 'description', 'scholarship_type',
            'amount', 'eligibility', 'deadline', 'application_url',
            'is_active', 'created_at',
        )


# ---------------------------------------------------------------------------
# College serializers
# ---------------------------------------------------------------------------

class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = (
            'id', 'name', 'location', 'college_type', 'affiliation',
            'ranking', 'website', 'established_year', 'description',
            'is_active', 'created_at',
        )


# ---------------------------------------------------------------------------
# Roadmap & Gamification serializers
# ---------------------------------------------------------------------------

class RoadmapItemSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        from .models import RoadmapItem
        model = RoadmapItem
        fields = (
            'id', 'roadmap', 'phase_number', 'phase_title', 'title',
            'skill', 'skill_name', 'difficulty', 'estimated_hours',
            'course', 'course_title', 'quiz', 'quiz_title', 'description',
            'learning_resources', 'practice_tasks', 'mini_project',
            'status', 'completion_percent', 'prerequisites', 'order', 'completed_at'
        )
        read_only_fields = ('completed_at',)


class LearningRoadmapSerializer(serializers.ModelSerializer):
    career_path_title = serializers.CharField(source='career_path.title', read_only=True)
    items = RoadmapItemSerializer(many=True, read_only=True)

    class Meta:
        from .models import LearningRoadmap
        model = LearningRoadmap
        fields = (
            'id', 'student', 'career_path', 'career_path_title', 'title',
            'overall_progress', 'active_phase', 'phases_data', 'items',
            'created_at', 'updated_at'
        )
        read_only_fields = ('student', 'created_at', 'updated_at')


class StudentGamificationSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import StudentGamification
        model = StudentGamification
        fields = (
            'xp', 'level', 'level_title', 'current_streak',
            'longest_streak', 'last_active_date', 'unlocked_badges'
        )


class LearningActivitySerializer(serializers.ModelSerializer):
    class Meta:
        from .models import LearningActivity
        model = LearningActivity
        fields = ('id', 'activity_type', 'title', 'xp_awarded', 'metadata', 'created_at')
        read_only_fields = ('created_at',)


class EntranceExamSerializer(serializers.ModelSerializer):
    related_career_names = serializers.SerializerMethodField()

    class Meta:
        model = EntranceExam
        fields = (
            'id', 'name', 'conducting_body', 'exam_category', 'eligibility',
            'application_period', 'exam_date_reference', 'official_website',
            'registration_url', 'exam_pattern', 'syllabus_summary',
            'related_career_paths', 'related_career_names', 'is_active', 'created_at',
        )

    def get_related_career_names(self, obj):
        return [c.title for c in obj.related_career_paths.all()]


class StudyTaskSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = StudyTask
        fields = (
            'id', 'student', 'task', 'subject', 'subject_name', 'skill',
            'skill_name', 'scheduled_date', 'start_time', 'end_time',
            'estimated_minutes', 'priority', 'status', 'completed', 'notes',
            'created_at', 'updated_at',
        )
        read_only_fields = ('student', 'created_at', 'updated_at')


