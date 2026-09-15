from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsCounselorOrAdmin
from .models import (
    Subject, Course, LearningResource, Quiz, Question, Choice,
    QuizAttempt, StudentProgress, Scholarship, College,
    EntranceExam, StudyTask,
)
from .serializers import (
    SubjectSerializer, CourseSerializer, CourseListSerializer,
    LearningResourceSerializer, QuizSerializer, QuizPublicSerializer,
    QuestionSerializer, ChoiceSerializer, QuizAttemptSerializer,
    QuizSubmissionSerializer, StudentProgressSerializer,
    ScholarshipSerializer, CollegeSerializer,
    EntranceExamSerializer, StudyTaskSerializer,
)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CourseViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for courses.
    - List/Retrieve: any user (AllowAny) — matches Career recommendation pattern.
    - Create/Update/Delete: counselors/admins only.
    """
    queryset = Course.objects.select_related('subject', 'created_by').prefetch_related('resources').filter(is_published=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'level']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'duration_hours', 'title']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        """POST /api/learning/courses/{id}/enroll/ -> start tracking progress for this student."""
        course = self.get_object()
        progress, created = StudentProgress.objects.get_or_create(
            student=request.user, course=course,
            defaults={'status': StudentProgress.Status.IN_PROGRESS, 'progress_percent': 0},
        )
        serializer = StudentProgressSerializer(progress)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class LearningResourceViewSet(viewsets.ModelViewSet):
    """
    - List/Retrieve: AllowAny — students can browse resources.
    - Create/Update/Delete: counselors/admins only.
    """
    queryset = LearningResource.objects.select_related('course')
    serializer_class = LearningResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course', 'resource_type']
    search_fields = ['title']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [AllowAny()]


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related('course').prefetch_related('questions__choices')
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list') and not (
            self.request.user.is_authenticated and (
                self.request.user.is_staff or
                getattr(self.request.user, 'role', None) in ('counselor', 'admin')
            )
        ):
            return QuizPublicSerializer
        return QuizSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        """
        POST /api/learning/quizzes/{id}/submit/
        Body: {"answers": {"<question_id>": <choice_id>, ...}}
        Grades the quiz and records a QuizAttempt for the logged-in student.
        """
        quiz = self.get_object()
        serializer = QuizSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data['answers']

        questions = quiz.questions.prefetch_related('choices')
        total = questions.count()
        correct = 0

        for question in questions:
            chosen_choice_id = answers.get(str(question.id)) or answers.get(question.id)
            if chosen_choice_id is None:
                continue
            is_correct = Choice.objects.filter(
                id=chosen_choice_id, question=question, is_correct=True
            ).exists()
            if is_correct:
                correct += 1

        score = round((correct / total) * 100, 2) if total else 0
        passed = score >= quiz.passing_score

        attempt = QuizAttempt.objects.create(
            student=request.user, quiz=quiz, score=score, passed=passed,
            completed_at=timezone.now(),
        )

        from .roadmap_service import RoadmapService
        feedback_data = RoadmapService.handle_quiz_completed(request.user, quiz, score, passed)

        return Response(
            {
                'attempt': QuizAttemptSerializer(attempt).data,
                'correct_answers': correct,
                'total_questions': total,
                'feedback': feedback_data['feedback'],
                'revision_needed': feedback_data['revision_needed'],
            },
            status=status.HTTP_201_CREATED,
        )



class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('quiz').prefetch_related('choices')
    serializer_class = QuestionSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz']


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.select_related('question')
    serializer_class = ChoiceSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """Students see only their own attempts; counselors/admins see all."""
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['quiz', 'passed']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) in ('counselor', 'admin'):
            return QuizAttempt.objects.select_related('quiz', 'student').all()
        return QuizAttempt.objects.select_related('quiz').filter(student=user)


class StudentProgressViewSet(viewsets.ModelViewSet):
    """Tracks each student's progress through courses. Students manage only their own records."""
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) in ('counselor', 'admin'):
            return StudentProgress.objects.select_related('course', 'student').all()
        return StudentProgress.objects.select_related('course').filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


# ---------------------------------------------------------------------------
# Scholarship ViewSet
# ---------------------------------------------------------------------------

class ScholarshipViewSet(viewsets.ModelViewSet):
    """
    Scholarship catalog.
    - List/Retrieve: AllowAny — students can browse without login.
    - Create/Update/Delete: counselors/admins only.
    """
    queryset = Scholarship.objects.filter(is_active=True)
    serializer_class = ScholarshipSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['scholarship_type']
    search_fields = ['name', 'provider', 'eligibility']
    ordering_fields = ['name', 'amount', 'deadline', 'created_at']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [AllowAny()]


# ---------------------------------------------------------------------------
# College ViewSet
# ---------------------------------------------------------------------------

class CollegeViewSet(viewsets.ModelViewSet):
    """
    College / university catalog.
    - List/Retrieve: AllowAny — students can browse without login.
    - Create/Update/Delete: counselors/admins only.
    """
    queryset = College.objects.filter(is_active=True)
    serializer_class = CollegeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college_type']
    search_fields = ['name', 'location', 'affiliation']
    ordering_fields = ['ranking', 'name', 'established_year']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [AllowAny()]


# ---------------------------------------------------------------------------
# Dynamic Learning Roadmap Views
# ---------------------------------------------------------------------------

from rest_framework.views import APIView

class LearningRoadmapView(APIView):
    """
    GET  /api/learning/roadmap/          -> returns personalized roadmap
    POST /api/learning/roadmap/generate/ -> regenerates fresh adaptive roadmap from skill gaps
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .roadmap_service import RoadmapService
        data = RoadmapService.get_or_generate_roadmap(request.user)
        return Response(data)

    def post(self, request):
        from .roadmap_service import RoadmapService
        data = RoadmapService.get_or_generate_roadmap(request.user, force_regenerate=True)
        return Response(data)


class RoadmapItemCompleteView(APIView):
    """
    POST /api/learning/roadmap/items/{id}/complete/
    Marks roadmap item complete, improves skill proficiency, recalculates skill gaps,
    and awards XP via GamificationService.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        from .roadmap_service import RoadmapService
        result = RoadmapService.complete_item(request.user, item_id=pk)
        if 'error' in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        return Response(result, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Gamification & Daily Check-in Views
# ---------------------------------------------------------------------------

class GamificationView(APIView):
    """GET /api/learning/gamification/ -> returns XP, level, streak, badges, recent activity."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .gamification_service import GamificationService
        summary = GamificationService.get_summary(request.user)
        return Response(summary)


class DailyCheckinView(APIView):
    """POST /api/learning/gamification/daily-checkin/ -> claims daily learning XP and updates streak."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .gamification_service import GamificationService
        result = GamificationService.award_xp(
            student=request.user,
            activity_type='daily',
            title='Daily Learning Check-in',
            xp_amount=15,
        )
        return Response({
            'message': f"Daily bonus claimed! +{result['xp_awarded']} XP",
            'gamification': result,
        })


# ---------------------------------------------------------------------------
# Entrance Exams
# ---------------------------------------------------------------------------

class EntranceExamViewSet(viewsets.ModelViewSet):
    """
    List / Retrieve entrance exams.
    - Read: Authenticated
    - Write: Counselors / Admins
    """
    queryset = EntranceExam.objects.prefetch_related('related_career_paths').filter(is_active=True)
    serializer_class = EntranceExamSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['exam_category', 'is_active']
    search_fields = ['name', 'conducting_body', 'syllabus_summary', 'eligibility']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [permissions.IsAuthenticated()]


# ---------------------------------------------------------------------------
# Dynamic Study Planner Views & StudyTask ViewSet
# ---------------------------------------------------------------------------

class StudyTaskViewSet(viewsets.ModelViewSet):
    """
    CRUD for authenticated student's study tasks with strict user data isolation.
    """
    serializer_class = StudyTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['completed', 'priority', 'status', 'scheduled_date']
    search_fields = ['task', 'notes']
    ordering_fields = ['scheduled_date', 'priority', 'created_at', 'completed']

    def get_queryset(self):
        return StudyTask.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class StudyPlannerView(APIView):
    """
    GET  /api/learning/planner/ -> returns student's dynamically generated study plan based on skill gaps AND persisted custom tasks.
    POST /api/learning/planner/ -> allows adding a custom persisted study task.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .roadmap_service import RoadmapService
        plan = RoadmapService.get_study_plan(request.user)
        
        # Merge persisted StudyTask items for this student
        custom_tasks = StudyTask.objects.filter(student=request.user)
        custom_goals = []
        for ct in custom_tasks:
            custom_goals.append({
                'id': f"db-{ct.id}",
                'task_db_id': ct.id,
                'task': ct.task,
                'day': ct.scheduled_date.strftime('%A') if ct.scheduled_date else 'Today',
                'hours': round(ct.estimated_minutes / 60, 1) if ct.estimated_minutes else 0.5,
                'completed': ct.completed,
                'priority': ct.priority,
                'notes': ct.notes or '',
                'is_custom': True,
            })
        
        # Combine goals
        all_goals = plan.get('goals', []) + custom_goals
        completed_count = sum(1 for g in all_goals if g.get('completed'))
        total_count = len(all_goals)
        completed_percent = round((completed_count / total_count) * 100) if total_count > 0 else 0
        total_hours = sum(g.get('hours', 0) for g in all_goals)
        
        plan['goals'] = all_goals
        plan['completed_count'] = completed_count
        plan['total_count'] = total_count
        plan['completed_percent'] = completed_percent
        plan['total_weekly_hours'] = total_hours
        return Response(plan)

    def post(self, request):
        """Allow adding a custom study task through the planner endpoint directly."""
        task_title = request.data.get('task') or request.data.get('title')
        if not task_title or not str(task_title).strip():
            return Response({'error': 'Task title is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        task = StudyTask.objects.create(
            student=request.user,
            task=str(task_title).strip(),
            estimated_minutes=request.data.get('estimated_minutes', 30),
            priority=request.data.get('priority', 'medium'),
            notes=request.data.get('notes', ''),
        )
        return Response({
            'success': True,
            'message': f"Added study task '{task.task}'",
            'task': StudyTaskSerializer(task).data,
        }, status=status.HTTP_201_CREATED)


class StudyPlannerToggleView(APIView):
    """POST /api/learning/planner/toggle/ -> toggles completion of an adaptive or custom study plan goal."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from .roadmap_service import RoadmapService
        raw_task_id = request.data.get('task_id')
        if raw_task_id is None:
            return Response({'error': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if it's a persisted StudyTask
        str_id = str(raw_task_id)
        if str_id.startswith('db-') or (isinstance(raw_task_id, int) and StudyTask.objects.filter(id=raw_task_id, student=request.user).exists()):
            db_id = int(str_id.replace('db-', '')) if str_id.startswith('db-') else raw_task_id
            task = StudyTask.objects.filter(id=db_id, student=request.user).first()
            if not task:
                return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
            
            desired = request.data.get('completed')
            if desired is not None:
                task.completed = bool(desired)
            else:
                task.completed = not task.completed
            task.status = 'completed' if task.completed else 'pending'
            task.save()

            # Award XP if completed
            if task.completed:
                from .gamification_service import GamificationService
                GamificationService.award_xp(
                    student=request.user,
                    activity_type='planner_task',
                    title=f"Completed study goal: {task.task}",
                    xp_amount=15,
                    metadata={'task_id': task.id}
                )

            return Response({
                'success': True,
                'completed': task.completed,
                'message': f"Task marked {'complete' if task.completed else 'pending'}.",
                'task': StudyTaskSerializer(task).data
            }, status=status.HTTP_200_OK)

        # Otherwise delegate to RoadmapService for adaptive roadmap goals
        try:
            task_id_parsed = int(raw_task_id)
        except (ValueError, TypeError):
            task_id_parsed = raw_task_id
        result = RoadmapService.toggle_study_task(request.user, task_id_parsed)
        if 'error' in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        return Response(result, status=status.HTTP_200_OK)


