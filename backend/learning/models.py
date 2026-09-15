from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Subject(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses')
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    duration_hours = models.PositiveIntegerField(default=1)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_created'
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LearningResource(models.Model):
    class ResourceType(models.TextChoices):
        VIDEO = 'video', 'Video'
        ARTICLE = 'article', 'Article'
        PDF = 'pdf', 'PDF'
        LINK = 'link', 'External Link'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices, default=ResourceType.ARTICLE)
    url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='learning_resources/', blank=True, null=True)
    content = models.TextField(blank=True, null=True, help_text="Inline text content for article-type resources.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    passing_score = models.PositiveIntegerField(default=50, help_text="Passing percentage")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'correct' if self.is_correct else 'incorrect'})"


class QuizAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    score = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score}%)"


class StudentProgress(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='student_progress')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.progress_percent}%)"


# ---------------------------------------------------------------------------
# Scholarship
# ---------------------------------------------------------------------------

class Scholarship(models.Model):
    """A scholarship opportunity students can apply for."""

    class ScholarshipType(models.TextChoices):
        MERIT = 'merit', 'Merit Based'
        NEED = 'need', 'Need Based'
        SPORTS = 'sports', 'Sports'
        MINORITY = 'minority', 'Minority'
        GOVERNMENT = 'government', 'Government'
        PRIVATE = 'private', 'Private'
        OTHER = 'other', 'Other'

    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=255, help_text="Organisation or government body offering the scholarship")
    description = models.TextField()
    scholarship_type = models.CharField(
        max_length=20, choices=ScholarshipType.choices, default=ScholarshipType.MERIT
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        help_text="Annual scholarship amount in INR"
    )
    eligibility = models.TextField(blank=True, null=True, help_text="Eligibility criteria")
    deadline = models.DateField(blank=True, null=True, help_text="Application deadline")
    application_url = models.URLField(blank=True, null=True, help_text="Link to apply")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# College
# ---------------------------------------------------------------------------

class College(models.Model):
    """A college / university that students can explore."""

    class CollegeType(models.TextChoices):
        IIT = 'iit', 'IIT'
        NIT = 'nit', 'NIT'
        IIIT = 'iiit', 'IIIT'
        CENTRAL = 'central', 'Central University'
        STATE = 'state', 'State University'
        DEEMED = 'deemed', 'Deemed University'
        PRIVATE = 'private', 'Private'
        OTHER = 'other', 'Other'

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True, help_text="City, State")
    college_type = models.CharField(
        max_length=20, choices=CollegeType.choices, default=CollegeType.OTHER
    )
    affiliation = models.CharField(
        max_length=255, blank=True, null=True, help_text="Affiliated board / university"
    )
    ranking = models.PositiveIntegerField(
        blank=True, null=True, help_text="NIRF or equivalent national rank"
    )
    website = models.URLField(blank=True, null=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ranking', 'name']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Personalized Dynamic Learning Roadmap
# ---------------------------------------------------------------------------

class LearningRoadmap(models.Model):
    """A personalized learning journey generated for a student targeting a career path."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roadmaps')
    career_path = models.ForeignKey('career.CareerPath', on_delete=models.CASCADE, related_name='student_roadmaps')
    title = models.CharField(max_length=255)
    overall_progress = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    active_phase = models.PositiveIntegerField(default=1)
    phases_data = models.JSONField(default=list, help_text="Phase metadata and titles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Roadmap: {self.student.username} -> {self.career_path.title} ({self.overall_progress}%)"


class RoadmapItem(models.Model):
    """An individual topic, exercise, or milestone in a student's learning roadmap."""
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', 'Not Started'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    roadmap = models.ForeignKey(LearningRoadmap, on_delete=models.CASCADE, related_name='items')
    phase_number = models.PositiveIntegerField(default=1)
    phase_title = models.CharField(max_length=150)
    title = models.CharField(max_length=255)
    skill = models.ForeignKey('students.Skill', on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_items')
    difficulty = models.CharField(max_length=20, default='intermediate', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    estimated_hours = models.PositiveIntegerField(default=5)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_items')
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True, related_name='roadmap_items')
    description = models.TextField(blank=True, null=True)
    learning_resources = models.JSONField(default=list, help_text="Curated articles, docs, or video links")
    practice_tasks = models.JSONField(default=list, help_text="Hands-on practice exercises")
    mini_project = models.TextField(blank=True, null=True, help_text="Milestone mini-project description")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    completion_percent = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    prerequisites = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['phase_number', 'order', 'id']

    def __str__(self):
        return f"P{self.phase_number}: {self.title} [{self.status}]"


# ---------------------------------------------------------------------------
# Student Gamification & Activity Tracking
# ---------------------------------------------------------------------------

class StudentGamification(models.Model):
    """Central gamification profile tracking XP, level, daily streaks, and unlocked badges."""
    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gamification')
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    level_title = models.CharField(max_length=50, default='Beginner')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    unlocked_badges = models.JSONField(default=list)

    def __str__(self):
        return f"{self.student.username} - Level {self.level} ({self.xp} XP) 🔥 {self.current_streak}d"


from django.utils import timezone


class LearningActivity(models.Model):
    """Audit log of student achievements, lessons completed, quizzes passed for analytics and XP."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='learning_activities')
    activity_type = models.CharField(
        max_length=50,
        help_text="lesson, quiz, assessment, project, skill_gap, daily, streak"
    )
    title = models.CharField(max_length=255)
    xp_awarded = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} - {self.title} (+{self.xp_awarded} XP)"


# ---------------------------------------------------------------------------
# Entrance Exams
# ---------------------------------------------------------------------------

class EntranceExam(models.Model):
    """National and state entrance exams with verified information and official portals."""

    class ExamCategory(models.TextChoices):
        ENGINEERING = 'engineering', 'Engineering'
        MEDICAL = 'medical', 'Medical'
        MANAGEMENT = 'management', 'Management'
        CIVIL_SERVICES = 'civil_services', 'Civil Services'
        LAW = 'law', 'Law'
        SCIENCES = 'sciences', 'Sciences & Research'
        OTHER = 'other', 'Other'

    name = models.CharField(max_length=255)
    conducting_body = models.CharField(max_length=255, help_text="e.g. NTA, IITs, NBE, UPSC")
    exam_category = models.CharField(
        max_length=50, choices=ExamCategory.choices, default=ExamCategory.ENGINEERING
    )
    eligibility = models.TextField(blank=True, null=True, help_text="Eligibility criteria & educational qualifications")
    application_period = models.CharField(max_length=255, blank=True, null=True, help_text="Application window or dates e.g. Dec - Jan (Annual)")
    exam_date_reference = models.CharField(max_length=255, blank=True, null=True, help_text="Expected exam window / reference date")
    official_website = models.URLField(blank=True, null=True, help_text="Official exam portal")
    registration_url = models.URLField(blank=True, null=True, help_text="Direct registration link if active")
    exam_pattern = models.TextField(blank=True, null=True, help_text="Format: Mode (CBT/Offline), Duration, Sections, Marking scheme")
    syllabus_summary = models.TextField(blank=True, null=True, help_text="Key subjects and high-weightage topics covered")
    related_career_paths = models.ManyToManyField('career.CareerPath', blank=True, related_name='entrance_exams')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.conducting_body})"


# ---------------------------------------------------------------------------
# Study Planner Tasks
# ---------------------------------------------------------------------------

class StudyTask(models.Model):
    """Individual study planner task created by or tailored for an authenticated student with user isolation."""

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='study_tasks')
    task = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_tasks')
    skill = models.ForeignKey('students.Skill', on_delete=models.SET_NULL, null=True, blank=True, related_name='study_tasks')
    scheduled_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    estimated_minutes = models.PositiveIntegerField(default=30)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', 'scheduled_date', '-priority', '-created_at']

    def __str__(self):
        return f"{self.student.username}: {self.task} ({'Done' if self.completed else 'Pending'})"


