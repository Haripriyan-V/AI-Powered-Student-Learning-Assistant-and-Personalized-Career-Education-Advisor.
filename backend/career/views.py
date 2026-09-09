from collections import defaultdict
from rest_framework.permissions import AllowAny
from django.utils import timezone
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsCounselorOrAdmin
from students.models import StudentProfile
from .models import (
    CareerField, CareerPath, AssessmentTest, AssessmentQuestion,
    AssessmentOption, AssessmentResult, CareerRecommendation,
    SkillRequirement, SkillGapAnalysis,
)
from .serializers import (
    CareerFieldSerializer, CareerPathSerializer, CareerPathListSerializer,
    AssessmentTestSerializer, AssessmentTestPublicSerializer,
    AssessmentQuestionSerializer, AssessmentOptionSerializer,
    AssessmentSubmissionSerializer, AssessmentResultSerializer,
    CareerRecommendationSerializer, SkillRequirementSerializer,
    SkillGapAnalysisSerializer,
)



class CareerFieldViewSet(viewsets.ModelViewSet):
    queryset = CareerField.objects.all()
    serializer_class = CareerFieldSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [permissions.IsAuthenticated()]


class CareerPathViewSet(viewsets.ModelViewSet):
    queryset = CareerPath.objects.select_related('career_field').prefetch_related('required_skills', 'related_interests')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['career_field', 'growth_outlook']
    search_fields = ['title', 'description']
    ordering_fields = ['average_salary_lpa', 'title']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return CareerPathListSerializer
        return CareerPathSerializer


class AssessmentTestViewSet(viewsets.ModelViewSet):
    queryset = AssessmentTest.objects.filter(is_active=True).prefetch_related('questions__options')
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsCounselorOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) in ('counselor', 'admin'):
            return AssessmentTestSerializer
        return AssessmentTestPublicSerializer

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        """
        POST /api/career/tests/{id}/submit/
        Body: {"answers": {"<question_id>": <option_id>, ...}}
        Validates answers, computes field affinity scores, saves AssessmentResult,
        and generates fresh transparent multi-factor recommendations via CareerRecommendationEngine.
        """
        test = self.get_object()
        serializer = AssessmentSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        raw_answers = serializer.validated_data['answers']

        if not isinstance(raw_answers, dict):
            return Response(
                {'error': 'Answers must be a dictionary mapping question IDs to option IDs.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        field_scores = defaultdict(int)
        questions = test.questions.select_related('related_career_field').prefetch_related('options')
        question_map = {q.id: q for q in questions}

        # Safe fallback field if a question does not have related_career_field assigned
        default_field = CareerField.objects.first()

        for q_key, opt_val in raw_answers.items():
            try:
                qid = int(q_key)
                oid = int(opt_val)
            except (ValueError, TypeError):
                continue  # ignore malformed answer inputs safely

            question = question_map.get(qid)
            if not question:
                continue  # ignore questions outside this test

            # Verify that option strictly belongs to this question
            option = question.options.filter(id=oid).first()
            if not option:
                continue

            target_field_id = question.related_career_field_id or (default_field.id if default_field else None)
            if target_field_id:
                field_scores[str(target_field_id)] += option.score_weight

        result = AssessmentResult.objects.create(
            student=request.user,
            test=test,
            field_scores=dict(field_scores),
        )

        # Generate fresh, unified multi-factor recommendations
        from ai.career_recommender import CareerRecommendationEngine
        recommendations = CareerRecommendationEngine.recommend(request.user, top_n=6)

        return Response(
            {
                'result': AssessmentResultSerializer(result).data,
                'recommendations': recommendations,
            },
            status=status.HTTP_201_CREATED,
        )


class AssessmentQuestionViewSet(viewsets.ModelViewSet):
    queryset = AssessmentQuestion.objects.select_related('test', 'related_career_field').prefetch_related('options')
    serializer_class = AssessmentQuestionSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['test']


class AssessmentOptionViewSet(viewsets.ModelViewSet):
    queryset = AssessmentOption.objects.select_related('question')
    serializer_class = AssessmentOptionSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question']


class AssessmentResultViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssessmentResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['test']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, 'role', None) in ('counselor', 'admin'):
            return AssessmentResult.objects.select_related('test', 'student').all()
        return AssessmentResult.objects.select_related('test').filter(student=user)

class CareerRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = CareerRecommendationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['career_path']
    ordering_fields = ['match_score', 'generated_at']

    def get_queryset(self):
        return CareerRecommendation.objects.select_related(
            'career_path__career_field',
            'student'
        ).all()


class MyRecommendationsView(APIView):
    """GET /api/career/my-recommendations/ -> computes or fetches transparent multi-factor recommendations."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from ai.career_recommender import CareerRecommendationEngine
        recommendations = CareerRecommendationEngine.recommend(request.user, top_n=6)
        if not recommendations:
            # Fallback to existing saved
            recs = CareerRecommendation.objects.select_related('career_path__career_field').filter(
                student=request.user
            ).order_by('-match_score')[:6]
            return Response(CareerRecommendationSerializer(recs, many=True).data)
        return Response(recommendations)


class SkillGapAnalysisView(APIView):
    """
    GET  /api/career/skill-gap/          -> get current gap analysis (or specify ?career_id=X)
    POST /api/career/skill-gap/analyze/  -> run fresh analysis and update profile records
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from ai.skill_engine import SkillGapEngine
        from .models import SkillGapAnalysis

        career_id = request.query_params.get('career_id')
        career_path = None
        if career_id:
            career_path = CareerPath.objects.filter(id=career_id).first()

        if not career_path:
            profile = getattr(request.user, 'student_profile', None)
            career_path = getattr(profile, 'target_career', None)

        if not career_path:
            career_path = CareerPath.objects.first()

        if not career_path:
            return Response({'error': 'No career paths configured.'}, status=status.HTTP_404_NOT_FOUND)

        # Look for recent analysis or run fresh
        analysis_obj = SkillGapAnalysis.objects.filter(student=request.user, career_path=career_path).first()
        if not analysis_obj:
            analysis_data = SkillGapEngine.analyze(request.user, career_path)
            analysis_obj = SkillGapAnalysis.objects.create(
                student=request.user,
                career_path=career_path,
                readiness_score=analysis_data['readiness_score'],
                total_skills_count=analysis_data['total_skills_count'],
                strong_count=analysis_data['counts']['strong'],
                minor_count=analysis_data['counts']['minor'],
                moderate_count=analysis_data['counts']['moderate'],
                major_count=analysis_data['counts']['major'],
                critical_count=analysis_data['counts']['critical'],
                gaps_data=analysis_data['gaps_data'],
                priority_skills=analysis_data['priority_skills'],
                category_summary=analysis_data['category_summary'],
                ai_explanation=analysis_data['ai_explanation'],
            )

        serializer = SkillGapAnalysisSerializer(analysis_obj)
        return Response(serializer.data)

    def post(self, request):
        from ai.skill_engine import SkillGapEngine
        from .models import SkillGapAnalysis
        from students.models import StudentProfile

        career_id = request.data.get('career_id')
        career_path = None
        if career_id:
            career_path = CareerPath.objects.filter(id=career_id).first()

        if not career_path:
            profile, _ = StudentProfile.objects.get_or_create(user=request.user)
            career_path = getattr(profile, 'target_career', None) or CareerPath.objects.first()

        if not career_path:
            return Response({'error': 'Career path not found.'}, status=status.HTTP_404_NOT_FOUND)

        analysis_data = SkillGapEngine.analyze(request.user, career_path)

        analysis_obj, _ = SkillGapAnalysis.objects.update_or_create(
            student=request.user,
            career_path=career_path,
            defaults={
                'readiness_score': analysis_data['readiness_score'],
                'total_skills_count': analysis_data['total_skills_count'],
                'strong_count': analysis_data['counts']['strong'],
                'minor_count': analysis_data['counts']['minor'],
                'moderate_count': analysis_data['counts']['moderate'],
                'major_count': analysis_data['counts']['major'],
                'critical_count': analysis_data['counts']['critical'],
                'gaps_data': analysis_data['gaps_data'],
                'priority_skills': analysis_data['priority_skills'],
                'category_summary': analysis_data['category_summary'],
                'ai_explanation': analysis_data['ai_explanation'],
            }
        )

        return Response(SkillGapAnalysisSerializer(analysis_obj).data, status=status.HTTP_200_OK)


class TargetCareerView(APIView):
    """
    GET  /api/career/target-career/  -> get student's selected target career
    POST /api/career/target-career/  -> set student's target career {career_id: X}
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        target = profile.target_career
        if not target:
            # Default to first career path
            target = CareerPath.objects.first()
            if target:
                profile.target_career = target
                profile.save()

        if not target:
            return Response({'target_career': None})
        return Response({
            'id': target.id,
            'title': target.title,
            'field': target.career_field.name,
            'salary': target.average_salary_lpa,
            'growth': target.growth_outlook,
        })

    def post(self, request):
        career_id = request.data.get('career_id')
        career_path = CareerPath.objects.filter(id=career_id).first()
        if not career_path:
            return Response({'error': 'Invalid career_id'}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        profile.target_career = career_path
        profile.save()

        # Trigger initial gap analysis for target career
        from ai.skill_engine import SkillGapEngine
        analysis_data = SkillGapEngine.analyze(request.user, career_path)

        return Response({
            'message': f"Target career updated to {career_path.title}",
            'target_career': {
                'id': career_path.id,
                'title': career_path.title,
                'field': career_path.career_field.name,
            },
            'readiness_score': analysis_data['readiness_score'],
        })


class SkillRequirementViewSet(viewsets.ModelViewSet):
    queryset = SkillRequirement.objects.select_related('career_path', 'skill')
    serializer_class = SkillRequirementSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['career_path', 'skill', 'is_core']


class WhatIfView(APIView):
    """
    POST /api/career/what-if/
    Body: {"career_id": 1, "additional_skills": ["Docker", "Kubernetes", "AWS"]}
    Simulates real projected match score if student learns these skills.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from ai.career_recommender import CareerRecommendationEngine
        career_id = request.data.get('career_id') or request.data.get('career_path_id')
        additional_skills = request.data.get('additional_skills') or []

        if not career_id:
            profile = getattr(request.user, 'student_profile', None)
            target = getattr(profile, 'target_career', None) or CareerPath.objects.first()
            career_id = target.id if target else None

        if not career_id:
            return Response({'error': 'No career specified and none configured.'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(additional_skills, list):
            additional_skills = [str(additional_skills)]

        try:
            result = CareerRecommendationEngine.simulate_what_if(request.user, int(career_id), additional_skills)
            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            result['success'] = True
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

