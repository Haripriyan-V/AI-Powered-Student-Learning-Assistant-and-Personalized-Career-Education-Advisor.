from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import StudentProfile, StudentSkill, Education, Interest, Skill


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('id', 'name')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name', 'category')


class StudentSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(required=False)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        source='skill', queryset=Skill.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = StudentSkill
        fields = (
            'id', 'skill_id', 'skill_name', 'skill_category',
            'proficiency', 'proficiency_score', 'source', 'verified', 'last_updated'
        )
        read_only_fields = ('last_updated',)

    def validate(self, attrs):
        if 'skill' not in attrs:
            raw_name = self.initial_data.get('skill_name') or self.initial_data.get('name')
            if raw_name:
                name_clean = raw_name.strip()
                skill = Skill.objects.filter(name__iexact=name_clean).first()
                if not skill:
                    skill = Skill.objects.create(name=name_clean, category='technical')
                attrs['skill'] = skill
            else:
                raise serializers.ValidationError({'skill_id': 'Either skill_id or skill_name is required.'})
        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.skill:
            ret['skill_name'] = instance.skill.name
            ret['skill_category'] = instance.skill.category
        return ret


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            'id', 'institution_name', 'degree_or_level', 'field_of_study',
            'start_year', 'end_year', 'percentage_or_gpa', 'is_current',
        )

    def validate(self, attrs):
        start = attrs.get('start_year')
        end = attrs.get('end_year')
        if start and end and end < start:
            raise serializers.ValidationError({'end_year': 'End year cannot be before start year.'})
        return attrs


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    score_breakdown = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    weaknesses = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    missing_skills = serializers.SerializerMethodField()
    formatting_issues = serializers.SerializerMethodField()
    bullet_point_improvements = serializers.SerializerMethodField()
    detected_role = serializers.SerializerMethodField()
    word_count = serializers.SerializerMethodField()
    readability_score = serializers.SerializerMethodField()
    action_verbs_score = serializers.SerializerMethodField()

    class Meta:
        from .models import ResumeAnalysis
        model = ResumeAnalysis
        fields = (
            'id', 'student', 'resume_file', 'file_name', 'extracted_name',
            'overall_score', 'ats_score', 'breakdown_scores', 'score_breakdown',
            'extracted_skills', 'normalized_skills', 'extracted_education',
            'extracted_experience', 'extracted_projects', 'strengths',
            'improvements', 'missing_keywords', 'career_alignment',
            'summary', 'weaknesses', 'recommendations', 'skills',
            'missing_skills', 'formatting_issues', 'bullet_point_improvements',
            'detected_role', 'word_count', 'readability_score',
            'action_verbs_score', 'created_at',
        )
        read_only_fields = fields

    def get_score_breakdown(self, obj):
        return obj.breakdown_scores or {}

    def get_summary(self, obj):
        align = obj.career_alignment or {}
        return align.get('summary') or f"ATS evaluation score: {obj.ats_score}/100."

    def get_weaknesses(self, obj):
        align = obj.career_alignment or {}
        return align.get('weaknesses') or obj.improvements or []

    def get_recommendations(self, obj):
        align = obj.career_alignment or {}
        return align.get('recommendations') or obj.improvements or []

    def get_skills(self, obj):
        return obj.normalized_skills or obj.extracted_skills or []

    def get_missing_skills(self, obj):
        align = obj.career_alignment or {}
        return align.get('missing_skills') or obj.missing_keywords or []

    def get_formatting_issues(self, obj):
        return [imp for imp in (obj.improvements or []) if 'format' in imp.lower() or 'summary' in imp.lower()]

    def get_bullet_point_improvements(self, obj):
        return [imp for imp in (obj.improvements or []) if 'verb' in imp.lower() or 'metric' in imp.lower()]

    def get_detected_role(self, obj):
        align = obj.career_alignment or {}
        return align.get('matched_career') or "Software Professional"

    def get_word_count(self, obj):
        bd = obj.breakdown_scores or {}
        return bd.get('word_count', 450)

    def get_readability_score(self, obj):
        bd = obj.breakdown_scores or {}
        return bd.get('formatting', 85)

    def get_action_verbs_score(self, obj):
        bd = obj.breakdown_scores or {}
        return bd.get('achievements', 80)


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    interest_ids = serializers.PrimaryKeyRelatedField(
        source='interests', queryset=Interest.objects.all(), many=True, write_only=True, required=False
    )
    skills = StudentSkillSerializer(many=True, read_only=True)
    education_history = EducationSerializer(many=True, read_only=True)
    target_career_title = serializers.CharField(source='target_career.title', read_only=True)

    # Writable user-level fields & aliases for profile & settings
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    user_first_name = serializers.CharField(required=False, allow_blank=True)
    user_last_name = serializers.CharField(required=False, allow_blank=True)

    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            'id', 'user', 'gender', 'grade_or_class', 'school_or_college',
            'bio', 'profile_picture', 'interests', 'interest_ids',
            'target_career', 'target_career_title',
            'skills', 'education_history', 'created_at', 'updated_at',
            'first_name', 'last_name', 'email', 'phone', 'phone_number',
            'user_username', 'user_first_name', 'user_last_name', 'user_email',
        )
        read_only_fields = ('created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        user = instance.user
        ret['user_first_name'] = getattr(user, 'first_name', '')
        ret['user_last_name'] = getattr(user, 'last_name', '')
        ret['first_name'] = getattr(user, 'first_name', '')
        ret['last_name'] = getattr(user, 'last_name', '')
        ret['email'] = getattr(user, 'email', '')
        ret['phone_number'] = getattr(user, 'phone_number', '')
        ret['phone'] = getattr(user, 'phone_number', '')
        return ret

    def update(self, instance, validated_data):
        user = instance.user
        user_updated = False

        first_name = validated_data.pop('first_name', None) or validated_data.pop('user_first_name', None)
        if first_name is not None:
            user.first_name = first_name
            user_updated = True

        last_name = validated_data.pop('last_name', None) or validated_data.pop('user_last_name', None)
        if last_name is not None:
            user.last_name = last_name
            user_updated = True

        email = validated_data.pop('email', None)
        if email is not None:
            user.email = email
            user_updated = True

        phone = validated_data.pop('phone', None) or validated_data.pop('phone_number', None)
        if phone is not None:
            user.phone_number = phone
            user_updated = True

        if user_updated:
            user.save()

        return super().update(instance, validated_data)

