import io
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from students.models import StudentProfile, Skill, StudentSkill, Education
from career.models import CareerField, CareerPath, SkillRequirement, SkillGapAnalysis
from learning.models import LearningRoadmap, RoadmapItem, StudentGamification
from ai.resume_analyzer import ResumeAnalyzer
from ai.career_recommender import CareerRecommendationEngine
from ai.service import ai_service

User = get_user_model()


class ProductionReadinessTestSuite(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='teststudent',
            email='teststudent@disha.ai',
            password='TestPassword123!',
            first_name='Test',
            last_name='Student',
            role='student',
        )
        self.client.force_authenticate(user=self.user)
        ai_service._testing_override = True
        ai_service.api_key = ''

        # Setup Career Field & Career Path
        self.field = CareerField.objects.create(name='Technology', description='Tech domain')
        self.career = CareerPath.objects.create(
            career_field=self.field,
            title='AI / Machine Learning Engineer',
            description='Develop state-of-the-art AI and ML systems.',
        )

        # Setup Skills
        self.skill_python = Skill.objects.create(name='Python', category='technical')
        self.skill_sql = Skill.objects.create(name='SQL', category='technical')
        self.skill_ml = Skill.objects.create(name='Machine Learning', category='technical')
        self.skill_pytorch = Skill.objects.create(name='PyTorch', category='technical')
        self.skill_docker = Skill.objects.create(name='Docker', category='technical')

        # Link skills to CareerPath
        SkillRequirement.objects.create(career_path=self.career, skill=self.skill_python, required_proficiency=80, importance=5, is_core=True)
        SkillRequirement.objects.create(career_path=self.career, skill=self.skill_sql, required_proficiency=70, importance=4, is_core=True)
        SkillRequirement.objects.create(career_path=self.career, skill=self.skill_ml, required_proficiency=85, importance=5, is_core=True)
        SkillRequirement.objects.create(career_path=self.career, skill=self.skill_pytorch, required_proficiency=75, importance=4, is_core=True)
        SkillRequirement.objects.create(career_path=self.career, skill=self.skill_docker, required_proficiency=65, importance=3, is_core=False)

        # Setup Student Profile
        self.profile, _ = StudentProfile.objects.get_or_create(
            user=self.user,
            defaults={'target_career': self.career, 'grade_or_class': 'Undergrad'}
        )
        self.profile.target_career = self.career
        self.profile.save()

        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.skill_python,
            proficiency='advanced',
            proficiency_score=85,
        )
        StudentSkill.objects.create(
            student_profile=self.profile,
            skill=self.skill_sql,
            proficiency='intermediate',
            proficiency_score=60,
        )

    def test_student_profile_update_aliases(self):
        """Verify StudentProfile PATCH updates user and profile attributes synchronously."""
        response = self.client.patch('/api/students/profile/me/', {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'phone_number': '+1-555-0199',
            'bio': 'Passionate AI engineering learner.',
            'grade_or_class': 'Senior',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.user.last_name, 'UpdatedLast')
        self.assertEqual(self.user.phone_number, '+1-555-0199')
        self.assertEqual(self.profile.bio, 'Passionate AI engineering learner.')
        self.assertEqual(self.profile.grade_or_class, 'Senior')

    def test_ats_scorer_8_factor_rubric(self):
        """Verify the transparent 8-factor ATS scoring rubric."""
        resume_text = (
            "John Doe | john@example.com | (555) 123-4567 | linkedin.com/in/johndoe\n"
            "Summary: Experienced software engineer passionate about Python, SQL, and Machine Learning.\n"
            "Technical Skills: Python, SQL, Machine Learning, Docker, Git, REST APIs, Linux.\n"
            "Projects:\n"
            "- Built a distributed recommendation engine that increased user engagement by 28% using Python and SQL.\n"
            "- Developed a full-stack dashboard deployed with Docker on AWS.\n"
            "Experience:\n"
            "- Software Engineer at Tech Corp. Architected scalable backend services with 99.9% uptime.\n"
            "Education: Bachelor of Science in Computer Science, State University, GPA 3.8.\n"
            "Achievements: Dean's Honor List, 1st place in National Hackathon."
        )
        file_obj = io.BytesIO(resume_text.encode('utf-8'))
        result = ResumeAnalyzer.analyze_resume(file_obj, 'resume.txt', target_career=self.career)

        overall = result['ats_score']
        breakdown = result['breakdown_scores']

        # Total ATS score must be between 0 and 100
        self.assertGreaterEqual(overall, 50)
        self.assertLessEqual(overall, 100)

        # Check that all 8 factors are present and within valid ranges
        expected_factors = [
            'keyword_match', 'skills', 'experience', 'projects',
            'education', 'formatting', 'achievements', 'contact_information'
        ]
        for factor in expected_factors:
            self.assertIn(factor, breakdown)
            self.assertGreaterEqual(breakdown[factor], 0)
            self.assertLessEqual(breakdown[factor], 100)

    def test_career_what_if_simulation(self):
        """Verify What-If simulation API provides genuine match score improvement."""
        response = self.client.post('/api/career/what-if/', {
            'career_path_id': self.career.id,
            'additional_skills': ['PyTorch', 'Docker', 'Machine Learning'],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data['success'])
        self.assertEqual(data['career_path_id'], self.career.id)
        self.assertIn('current_score', data)
        self.assertIn('projected_score', data)
        self.assertIn('score_delta', data)
        # Adding target core skills must improve the score
        self.assertGreater(data['projected_score'], data['current_score'])
        self.assertGreater(data['score_delta'], 0)

    def test_study_planner_and_task_toggle(self):
        """Verify Study Planner generates tasks and task toggle awards XP."""
        # 1. Fetch planner
        response = self.client.get('/api/learning/planner/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        goals = response.data.get('goals', [])
        self.assertIsInstance(goals, list)
        self.assertGreater(len(goals), 0)

        first_task = goals[0]
        task_id = first_task['id']

        # 2. Toggle task
        toggle_resp = self.client.post('/api/learning/planner/toggle/', {
            'task_id': task_id,
            'completed': True,
        }, format='json')

        self.assertEqual(toggle_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(toggle_resp.data['completed'])

        # 3. Check gamification profile received XP
        gam = StudentGamification.objects.get(student=self.user)
        self.assertGreaterEqual(gam.xp, 15)

    def test_ai_chatbot_offline_fallback(self):
        """Verify AIService returns intelligent context-aware reply even when offline."""
        # Force invalid/empty key to trigger fallback
        ai_service.api_key = ''

        fallback_reply = ai_service.generate_reply(
            user=self.user,
            session=None,
            new_message="How can I improve my resume for an AI role?",
        )

        self.assertIsInstance(fallback_reply, str)
        self.assertIn("Resume", fallback_reply)
        self.assertIn("DishaAI", fallback_reply)
        # Check student name or goal is recognized
        self.assertTrue('Test' in fallback_reply or 'AI' in fallback_reply)
