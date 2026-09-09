from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fields', views.CareerFieldViewSet, basename='career-field')
router.register(r'paths', views.CareerPathViewSet, basename='career-path')
router.register(r'tests', views.AssessmentTestViewSet, basename='assessment-test')
router.register(r'questions', views.AssessmentQuestionViewSet, basename='assessment-question')
router.register(r'options', views.AssessmentOptionViewSet, basename='assessment-option')
router.register(r'results', views.AssessmentResultViewSet, basename='assessment-result')
router.register(r'recommendations', views.CareerRecommendationViewSet, basename='career-recommendation')
router.register(r'skill-requirements', views.SkillRequirementViewSet, basename='skill-requirement')

urlpatterns = [
    path('my-recommendations/', views.MyRecommendationsView.as_view(), name='my-recommendations'),
    path('skill-gap/', views.SkillGapAnalysisView.as_view(), name='skill-gap'),
    path('skill-gap/analyze/', views.SkillGapAnalysisView.as_view(), name='skill-gap-analyze'),
    path('target-career/', views.TargetCareerView.as_view(), name='target-career'),
    path('what-if/', views.WhatIfView.as_view(), name='what-if'),
    path('', include(router.urls)),
]

