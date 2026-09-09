from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.permissions import IsOwnerOrAdmin, IsCounselorOrAdmin
from .models import StudentProfile, StudentSkill, Education, Interest, Skill
from .serializers import (
    StudentProfileSerializer, StudentSkillSerializer,
    EducationSerializer, InterestSerializer, SkillSerializer,
)


class InterestViewSet(viewsets.ModelViewSet):
    """Catalog of interests. Read access for all authenticated users; write for counselors/admins."""
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class SkillViewSet(viewsets.ModelViewSet):
    """Catalog of skills. Read access for all authenticated users; write for counselors/admins."""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'category']
    filterset_fields = ['category']


class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT/PATCH /api/students/profile/me/
    Fetch or update the logged-in student's profile. Auto-creates the
    profile on first access so the frontend never has to special-case 404.
    """
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return profile


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only listing of student profiles, intended for counselors/admins
    browsing students (e.g. for career guidance).
    """
    queryset = StudentProfile.objects.select_related('user').prefetch_related('interests', 'skills')
    serializer_class = StudentProfileSerializer
    permission_classes = [IsCounselorOrAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'user__email', 'school_or_college']


class EducationViewSet(viewsets.ModelViewSet):
    """CRUD for the logged-in student's own education history."""
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return Education.objects.filter(student_profile=profile)

    def perform_create(self, serializer):
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        serializer.save(student_profile=profile)


class StudentSkillViewSet(viewsets.ModelViewSet):
    """CRUD for the logged-in student's own skills."""
    serializer_class = StudentSkillSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return StudentSkill.objects.filter(student_profile=profile).select_related('skill')

    def perform_create(self, serializer):
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        instance = serializer.save(student_profile=profile)
        self._trigger_gap_update(profile)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._trigger_gap_update(instance.student_profile)

    def _trigger_gap_update(self, profile):
        if profile.target_career:
            try:
                from ai.skill_engine import SkillGapEngine
                from career.models import SkillGapAnalysis
                data = SkillGapEngine.analyze(profile.user, profile.target_career)
                SkillGapAnalysis.objects.update_or_create(
                    student=profile.user,
                    career_path=profile.target_career,
                    defaults={
                        'readiness_score': data['readiness_score'],
                        'total_skills_count': data['total_skills_count'],
                        'strong_count': data['counts']['strong'],
                        'minor_count': data['counts']['minor'],
                        'moderate_count': data['counts']['moderate'],
                        'major_count': data['counts']['major'],
                        'critical_count': data['counts']['critical'],
                        'gaps_data': data['gaps_data'],
                        'priority_skills': data['priority_skills'],
                        'category_summary': data['category_summary'],
                        'ai_explanation': data['ai_explanation'],
                    }
                )
            except Exception:
                pass


class ResumeAnalyzeView(generics.GenericAPIView):
    """
    POST /api/students/resume/analyze/
    Accepts multipart/form-data with `resume` file.
    Runs ATS evaluation, extracts skills, computes career alignment,
    awards XP, and saves ResumeAnalysis record.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        from ai.resume_analyzer import ResumeAnalyzer
        from learning.gamification_service import GamificationService
        from .models import ResumeAnalysis

        uploaded_file = request.FILES.get('resume') or request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'success': False, 'error': 'Please upload your resume.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enforce 10MB upload limit and check for empty files
        max_size_bytes = 10 * 1024 * 1024  # 10 MB
        if uploaded_file.size > max_size_bytes:
            return Response(
                {'success': False, 'error': 'File size exceeds the 10MB limit. Please upload a smaller resume file.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if uploaded_file.size == 0:
            return Response(
                {'success': False, 'error': 'The uploaded file is empty. Please upload a valid resume.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fname = (uploaded_file.name or '').lower()
        if not (fname.endswith('.pdf') or fname.endswith('.docx') or fname.endswith('.doc') or fname.endswith('.txt') or fname.endswith('.md')):
            return Response(
                {'success': False, 'error': 'Please upload a supported PDF, DOCX, or TXT resume.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        target_career = profile.target_career

        # Execute analysis
        try:
            analysis_data = ResumeAnalyzer.analyze_resume(
                file_obj=uploaded_file,
                filename=uploaded_file.name,
                target_career=target_career,
            )
        except Exception as e:
            return Response(
                {'success': False, 'error': 'Resume analysis is temporarily unavailable. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not analysis_data or 'error' in analysis_data:
            err_msg = analysis_data.get('error', 'Unable to extract readable text from this resume. Please upload a valid PDF/DOCX/TXT resume.') if analysis_data else 'Unable to extract readable text from this resume. Please upload a valid PDF/DOCX/TXT resume.'
            return Response(
                {'success': False, 'error': err_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save to database
        record = ResumeAnalysis.objects.create(
            student=request.user,
            resume_file=uploaded_file,
            file_name=uploaded_file.name,
            extracted_name=analysis_data.get('extracted_name', 'Candidate'),
            overall_score=analysis_data.get('overall_score', 75),
            ats_score=analysis_data.get('ats_score', 75),
            breakdown_scores=analysis_data.get('breakdown_scores', {}),
            extracted_skills=analysis_data.get('extracted_skills', []),
            normalized_skills=analysis_data.get('normalized_skills', []),
            extracted_education=analysis_data.get('extracted_education', []),
            extracted_experience=analysis_data.get('extracted_experience', []),
            extracted_projects=analysis_data.get('extracted_projects', []),
            strengths=analysis_data.get('strengths', []),
            improvements=analysis_data.get('improvements', []),
            missing_keywords=analysis_data.get('missing_keywords', []),
            career_alignment=analysis_data.get('career_alignment', {}),
        )

        # Award Gamification XP for analyzing resume
        try:
            GamificationService.award_xp(
                student=request.user,
                activity_type='project',
                title=f"Analyzed Resume ({record.overall_score}/100)",
                xp_amount=30,
                metadata={'resume_id': record.id, 'score': record.overall_score}
            )
        except Exception:
            pass

        from .serializers import ResumeAnalysisSerializer
        return Response(ResumeAnalysisSerializer(record).data, status=status.HTTP_201_CREATED)


class LatestResumeView(generics.GenericAPIView):
    """GET /api/students/resume/latest/ -> returns the latest resume analysis."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from .models import ResumeAnalysis
        from .serializers import ResumeAnalysisSerializer

        latest = ResumeAnalysis.objects.filter(student=request.user).first()
        if not latest:
            return Response({'resume': None})
        return Response(ResumeAnalysisSerializer(latest).data)


class ImportResumeSkillsView(generics.GenericAPIView):
    """
    POST /api/students/resume/import-skills/
    Takes normalized skills from latest resume and imports them into canonical StudentSkill profile,
    then automatically recalculates the student's Skill Gap Analysis!
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        from .models import ResumeAnalysis, Skill, StudentSkill
        from ai.skill_engine import SkillGapEngine
        from career.models import SkillGapAnalysis

        latest_resume = ResumeAnalysis.objects.filter(student=request.user).first()
        if not latest_resume or not latest_resume.normalized_skills:
            return Response(
                {'error': 'No analyzed resume skills found. Upload a resume first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile, _ = StudentProfile.objects.get_or_create(user=request.user)
        imported_count = 0

        for skill_name in latest_resume.normalized_skills:
            skill_obj, _ = Skill.objects.get_or_create(
                name=skill_name,
                defaults={'category': 'Technical'}
            )
            # Create or update student skill (if new, give 65% baseline proficiency from resume)
            student_skill, created = StudentSkill.objects.get_or_create(
                student_profile=profile,
                skill=skill_obj,
                defaults={'proficiency_score': 65, 'source': 'resume'}
            )
            if not created and student_skill.source == 'self':
                student_skill.source = 'resume'
                student_skill.save()
            imported_count += 1

        # Automatically recalculate Skill Gap if student has target career
        readiness_score = None
        target = profile.target_career
        if target:
            gap_data = SkillGapEngine.analyze(request.user, target)
            readiness_score = gap_data['readiness_score']
            SkillGapAnalysis.objects.update_or_create(
                student=request.user,
                career_path=target,
                defaults={
                    'readiness_score': gap_data['readiness_score'],
                    'total_skills_count': gap_data['total_skills_count'],
                    'strong_count': gap_data['counts']['strong'],
                    'minor_count': gap_data['counts']['minor'],
                    'moderate_count': gap_data['counts']['moderate'],
                    'major_count': gap_data['counts']['major'],
                    'critical_count': gap_data['counts']['critical'],
                    'gaps_data': gap_data['gaps_data'],
                    'priority_skills': gap_data['priority_skills'],
                    'category_summary': gap_data['category_summary'],
                    'ai_explanation': gap_data['ai_explanation'],
                }
            )

        # Automatically recalculate Career Recommendations based on new skills
        try:
            from ai.career_recommender import CareerRecommendationEngine
            CareerRecommendationEngine.recommend(request.user)
        except Exception:
            pass

        return Response({
            'success': True,
            'message': f"Successfully imported {imported_count} skills into your verified skill profile.",
            'imported_count': imported_count,
            'new_career_readiness': readiness_score,
        }, status=status.HTTP_200_OK)

