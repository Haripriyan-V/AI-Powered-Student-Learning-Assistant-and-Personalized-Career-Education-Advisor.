from rest_framework import serializers
from students.serializers import SkillSerializer, InterestSerializer
from .models import (
    CareerField, CareerPath, AssessmentTest, AssessmentQuestion,
    AssessmentOption, AssessmentResult, CareerRecommendation,
)


class CareerFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerField
        fields = ('id', 'name', 'description')


class CareerPathSerializer(serializers.ModelSerializer):
    career_field_name = serializers.CharField(source='career_field.name', read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    related_interests = InterestSerializer(many=True, read_only=True)

    class Meta:
        model = CareerPath
        fields = (
            'id', 'title', 'description', 'career_field', 'career_field_name',
            'required_skills', 'related_interests', 'average_salary_lpa',
            'growth_outlook', 'created_at',
        )


class CareerPathListSerializer(serializers.ModelSerializer):
    career_field_name = serializers.CharField(source='career_field.name', read_only=True)

    class Meta:
        model = CareerPath
        fields = ('id', 'title', 'career_field', 'career_field_name', 'average_salary_lpa', 'growth_outlook')


class AssessmentOptionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentOption
        fields = ('id', 'text')  # score_weight hidden from students


class AssessmentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentOption
        fields = ('id', 'question', 'text', 'score_weight')


class AssessmentQuestionPublicSerializer(serializers.ModelSerializer):
    options = AssessmentOptionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentQuestion
        fields = ('id', 'text', 'order', 'options')


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    options = AssessmentOptionSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentQuestion
        fields = ('id', 'test', 'text', 'related_career_field', 'order', 'options')


class AssessmentTestPublicSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentTest
        fields = ('id', 'title', 'description', 'is_active', 'questions')


class AssessmentTestSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = AssessmentTest
        fields = ('id', 'title', 'description', 'is_active', 'questions', 'created_at')


class AssessmentSubmissionSerializer(serializers.Serializer):
    """Payload: {"answers": {"<question_id>": <option_id>, ...}}"""
    answers = serializers.DictField(required=True)


class AssessmentResultSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)

    class Meta:
        model = AssessmentResult
        fields = ('id', 'student', 'test', 'test_title', 'field_scores', 'completed_at')
        read_only_fields = ('student', 'field_scores', 'completed_at')


class CareerRecommendationSerializer(serializers.ModelSerializer):
    career_path_id = serializers.IntegerField(source='career_path.id', read_only=True)
    career_path_detail = CareerPathListSerializer(source='career_path', read_only=True)
    career_path_title = serializers.CharField(source='career_path.title', read_only=True)
    career = serializers.CharField(source='career_path.title', read_only=True)
    career_name = serializers.CharField(source='career_path.title', read_only=True)
    title = serializers.CharField(source='career_path.title', read_only=True)
    career_field_name = serializers.CharField(source='career_path.career_field.name', read_only=True)
    career_path_career_field_name = serializers.CharField(source='career_path.career_field.name', read_only=True)
    average_salary_lpa = serializers.DecimalField(source='career_path.average_salary_lpa', max_digits=8, decimal_places=2, read_only=True)
    career_path_average_salary_lpa = serializers.DecimalField(source='career_path.average_salary_lpa', max_digits=8, decimal_places=2, read_only=True)
    growth_outlook = serializers.CharField(source='career_path.growth_outlook', read_only=True)
    career_path_growth_outlook = serializers.CharField(source='career_path.growth_outlook', read_only=True)
    description = serializers.CharField(source='career_path.description', read_only=True)
    matched_skills = serializers.SerializerMethodField()
    missing_skills = serializers.SerializerMethodField()
    score_breakdown = serializers.SerializerMethodField()

    class Meta:
        model = CareerRecommendation
        fields = (
            'id', 'student', 'career_path', 'career_path_id', 'career_path_detail',
            'career_path_title', 'career', 'career_name', 'title', 'career_field_name',
            'career_path_career_field_name', 'average_salary_lpa',
            'career_path_average_salary_lpa', 'growth_outlook',
            'career_path_growth_outlook', 'description', 'match_score', 'reasoning',
            'matched_skills', 'missing_skills', 'score_breakdown',
            'source_assessment', 'generated_at',
        )
        read_only_fields = ('student', 'generated_at')

    def get_matched_skills(self, obj):
        student = obj.student
        profile = getattr(student, 'student_profile', None)
        if not profile:
            return []
        student_skills = {ss.skill.name.lower() for ss in profile.skills.all()}
        cp_skills = [s.name for s in obj.career_path.required_skills.all()]
        return [name for name in cp_skills if name.lower() in student_skills]

    def get_missing_skills(self, obj):
        student = obj.student
        profile = getattr(student, 'student_profile', None)
        student_skills = {ss.skill.name.lower() for ss in profile.skills.all()} if profile else set()
        cp_skills = [s.name for s in obj.career_path.required_skills.all()]
        return [name for name in cp_skills if name.lower() not in student_skills]

    def get_score_breakdown(self, obj):
        score = float(obj.match_score) if obj.match_score else 70.0
        return {
            'skills_alignment': round(score * 0.4, 1),
            'assessment_affinity': round(score * 0.35, 1),
            'resume_match': round(score * 0.15, 1),
            'interests_alignment': round(score * 0.1, 1),
        }


class SkillRequirementSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)

    class Meta:
        from .models import SkillRequirement
        model = SkillRequirement
        fields = (
            'id', 'career_path', 'skill', 'skill_name', 'skill_category',
            'required_proficiency', 'importance', 'is_core'
        )


class SkillGapAnalysisSerializer(serializers.ModelSerializer):
    career_path_title = serializers.CharField(source='career_path.title', read_only=True)
    career_field_name = serializers.CharField(source='career_path.career_field.name', read_only=True)

    class Meta:
        from .models import SkillGapAnalysis
        model = SkillGapAnalysis
        fields = (
            'id', 'career_path', 'career_path_title', 'career_field_name',
            'readiness_score', 'total_skills_count', 'strong_count',
            'minor_count', 'moderate_count', 'major_count', 'critical_count',
            'gaps_data', 'priority_skills', 'category_summary', 'ai_explanation',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')

