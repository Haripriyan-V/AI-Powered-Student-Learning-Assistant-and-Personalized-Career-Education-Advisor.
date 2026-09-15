from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'resources', views.LearningResourceViewSet, basename='learning-resource')
router.register(r'quizzes', views.QuizViewSet, basename='quiz')
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'choices', views.ChoiceViewSet, basename='choice')
router.register(r'attempts', views.QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'progress', views.StudentProgressViewSet, basename='student-progress')
router.register(r'scholarships', views.ScholarshipViewSet, basename='scholarship')
router.register(r'colleges', views.CollegeViewSet, basename='college')
router.register(r'entrance-exams', views.EntranceExamViewSet, basename='entrance-exam')
router.register(r'study-tasks', views.StudyTaskViewSet, basename='study-task')

urlpatterns = [
    path('roadmap/', views.LearningRoadmapView.as_view(), name='learning-roadmap'),
    path('roadmap/generate/', views.LearningRoadmapView.as_view(), name='learning-roadmap-generate'),
    path('roadmap/items/<int:pk>/complete/', views.RoadmapItemCompleteView.as_view(), name='roadmap-item-complete'),
    path('gamification/', views.GamificationView.as_view(), name='gamification-summary'),
    path('gamification/daily-checkin/', views.DailyCheckinView.as_view(), name='gamification-checkin'),
    path('planner/', views.StudyPlannerView.as_view(), name='study-planner'),
    path('planner/toggle/', views.StudyPlannerToggleView.as_view(), name='study-planner-toggle'),
    path('', include(router.urls)),
]

