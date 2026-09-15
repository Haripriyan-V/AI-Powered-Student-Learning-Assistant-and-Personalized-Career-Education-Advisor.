from django.contrib import admin
from .models import (
    CareerField, CareerPath, AssessmentTest, AssessmentQuestion,
    AssessmentOption, AssessmentResult, CareerRecommendation,
    SkillRequirement, SkillGapAnalysis,
)


@admin.register(CareerField)
class CareerFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(CareerPath)
class CareerPathAdmin(admin.ModelAdmin):
    list_display = ('title', 'career_field', 'average_salary_lpa', 'growth_outlook')
    list_filter = ('career_field', 'growth_outlook')
    search_fields = ('title', 'description')
    filter_horizontal = ('required_skills', 'related_interests')


class AssessmentOptionInline(admin.TabularInline):
    model = AssessmentOption
    extra = 2


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'test', 'related_career_field', 'order')
    inlines = [AssessmentOptionInline]


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 1


@admin.register(AssessmentTest)
class AssessmentTestAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active',)
    inlines = [AssessmentQuestionInline]


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'completed_at')
    search_fields = ('student__username', 'test__title')


@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'career_path', 'match_score', 'generated_at')
    list_filter = ('career_path__career_field',)
    search_fields = ('student__username', 'career_path__title')


@admin.register(SkillRequirement)
class SkillRequirementAdmin(admin.ModelAdmin):
    list_display = ('career_path', 'skill', 'required_proficiency', 'importance', 'is_core')
    list_filter = ('importance', 'is_core', 'career_path__career_field')
    search_fields = ('career_path__title', 'skill__name')


@admin.register(SkillGapAnalysis)
class SkillGapAnalysisAdmin(admin.ModelAdmin):
    list_display = ('student', 'career_path', 'readiness_score', 'total_skills_count', 'updated_at')
    list_filter = ('career_path',)
    search_fields = ('student__username', 'career_path__title')

