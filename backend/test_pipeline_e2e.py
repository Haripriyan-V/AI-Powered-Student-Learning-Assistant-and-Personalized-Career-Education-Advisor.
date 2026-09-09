import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from career.models import (
    CareerField, CareerPath, AssessmentTest, AssessmentQuestion,
    AssessmentOption, AssessmentResult, CareerRecommendation, SkillRequirement
)
from students.models import StudentProfile, Skill, StudentSkill, Interest, ResumeAnalysis
from ai.career_recommender import CareerRecommendationEngine

User = get_user_model()

def run_tests():
    print("=" * 60)
    print("RUNNING PIPELINE E2E INTEGRATION TESTS")
    print("=" * 60)

    # 1. Setup test user
    username = "test_pipeline_student"
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password="Password123!", email="test_student@example.com")
    profile, _ = StudentProfile.objects.get_or_create(user=user)

    client = APIClient()
    client.force_authenticate(user=user)

    # 2. Verify assessment tests exist and questions have options with varied weights
    test = AssessmentTest.objects.filter(is_active=True).first()
    assert test is not None, "Active AssessmentTest must exist"
    questions = list(test.questions.all())
    assert len(questions) > 0, "Test must contain questions"
    print(f"[PASS] AssessmentTest '{test.title}' has {len(questions)} questions")

    # Verify options have graduated weights (not all 1)
    all_weights = set(AssessmentOption.objects.filter(question__test=test).values_list('score_weight', flat=True))
    assert len(all_weights) > 1, f"Option weights should vary, got: {all_weights}"
    print(f"[PASS] Options have varied score weights: {all_weights}")

    # TEST CASE 1: Submit answers for all questions
    # Choose answers that strongly favor Data Science / AI
    answers = {}
    for q in questions:
        # If question is related to data/ai, pick highest weight option; otherwise pick moderate
        opts = list(q.options.order_by('-score_weight'))
        if q.related_career_field and 'data' in q.related_career_field.name.lower():
            answers[str(q.id)] = opts[0].id
        else:
            answers[str(q.id)] = opts[-1].id

    submit_url = f"/api/career/tests/{test.id}/submit/"
    res = client.post(submit_url, {'answers': answers}, format='json')
    assert res.status_code == status.HTTP_201_CREATED, f"Submit failed: {res.data}"
    data = res.json()
    assert 'result' in data and 'recommendations' in data
    recs = data['recommendations']
    assert len(recs) > 0, "Recommendations must not be empty after submission"
    print(f"[PASS] Assessment submitted successfully! Created result ID {data['result']['id']}, generated {len(recs)} recommendations")

    # Verify ranking: top recommendation should be Data Science or AI
    top_rec = recs[0]
    print(f"       Top Recommendation: {top_rec['career']} ({top_rec['match_score']}%) in {top_rec['career_field_name']}")
    assert 'data' in top_rec['career_field_name'].lower() or 'data' in top_rec['career'].lower() or 'ai' in top_rec['career'].lower(), \
        f"Expected Data/AI career to rank top, got {top_rec['career']}"
    assert 60 <= top_rec['match_score'] <= 100, f"Top match score should be realistic, got {top_rec['match_score']}"

    # TEST CASE 2: Assessment-only student
    # Student has NO skills, NO resume, NO interests, NO courses
    my_recs_res = client.get('/api/career/my-recommendations/')
    assert my_recs_res.status_code == status.HTTP_200_OK
    my_recs = my_recs_res.json()
    assert len(my_recs) >= 4, f"Expected at least 4 recommendations, got {len(my_recs)}"
    scores = [r['match_score'] for r in my_recs]
    assert len(set(scores)) > 1, f"Recommendations must not have identical scores: {scores}"
    assert scores == sorted(scores, reverse=True), f"Recommendations must be sorted descending: {scores}"
    print(f"[PASS] Assessment-only student recommendations returned: {scores}")

    # TEST CASE 3: Add Skills to Profile and check ranking influence
    # Give student intermediate skills in Cyber Security
    net_sec, _ = Skill.objects.get_or_create(name='Network Security', defaults={'category': 'Security'})
    eth_hack, _ = Skill.objects.get_or_create(name='Ethical Hacking', defaults={'category': 'Security'})
    crypt, _ = Skill.objects.get_or_create(name='Cryptography', defaults={'category': 'Security'})
    StudentSkill.objects.create(student_profile=profile, skill=net_sec, proficiency='advanced', proficiency_score=90)
    StudentSkill.objects.create(student_profile=profile, skill=eth_hack, proficiency='advanced', proficiency_score=85)
    StudentSkill.objects.create(student_profile=profile, skill=crypt, proficiency='intermediate', proficiency_score=80)

    recs_with_skills = CareerRecommendationEngine.recommend(user, top_n=6)
    cyber_rec = next((r for r in recs_with_skills if 'cyber' in r['career'].lower() or 'security' in r['career'].lower()), None)
    assert cyber_rec is not None, "Cyber Security recommendation should exist"
    assert cyber_rec['score_breakdown']['skills_alignment'] > 0, "Skills should boost cyber security skill alignment score"
    print(f"[PASS] Student skills boosted Cyber Security alignment: skills_score={cyber_rec['score_breakdown']['skills_alignment']}")

    # TEST CASE 4: Add Resume Skills
    ResumeAnalysis.objects.create(
        student=user,
        file_name="test_resume.pdf",
        extracted_name="Test Student",
        overall_score=85,
        ats_score=80,
        normalized_skills=['python', 'aws', 'docker', 'kubernetes', 'ci/cd pipelines'],
    )
    recs_with_resume = CareerRecommendationEngine.recommend(user, top_n=6)
    cloud_rec = next((r for r in recs_with_resume if 'cloud' in r['career'].lower()), None)
    assert cloud_rec is not None, "Cloud recommendation should exist"
    assert cloud_rec['score_breakdown']['resume_match'] > 0, "Resume skills should boost resume_match"
    print(f"[PASS] Resume skills boosted Cloud Architect match: resume_score={cloud_rec['score_breakdown']['resume_match']}")

    # TEST CASE 5: Add Student Interests
    design_interest, _ = Interest.objects.get_or_create(name='UI/UX Design')
    profile.interests.add(design_interest)
    uiux_path = CareerPath.objects.filter(title__icontains='UI/UX').first()
    if uiux_path:
        uiux_path.related_interests.add(design_interest)

    recs_with_interest = CareerRecommendationEngine.recommend(user, top_n=6)
    uiux_rec = next((r for r in recs_with_interest if 'ui/ux' in r['career'].lower() or 'designer' in r['career'].lower()), None)
    if uiux_rec:
        assert uiux_rec['score_breakdown']['interests_alignment'] > 0, "Interests should contribute"
        print(f"[PASS] Interests boosted UI/UX Designer: interest_score={uiux_rec['score_breakdown']['interests_alignment']}")

    # TEST CASE 6: Repeat Assessment with Cloud preference
    cloud_answers = {}
    for q in questions:
        opts = list(q.options.order_by('-score_weight'))
        if q.related_career_field and 'cloud' in q.related_career_field.name.lower():
            cloud_answers[str(q.id)] = opts[0].id
        else:
            cloud_answers[str(q.id)] = opts[-1].id

    res2 = client.post(submit_url, {'answers': cloud_answers}, format='json')
    assert res2.status_code == status.HTTP_201_CREATED
    latest_ar = AssessmentResult.objects.filter(student=user).order_by('-completed_at').first()
    assert latest_ar.id == res2.json()['result']['id'], "Latest assessment must be the newly submitted one"
    print(f"[PASS] Repeated assessment creates new latest result ID {latest_ar.id}")

    # TEST CASE 7: Set as Target Career
    target_cp = CareerPath.objects.first()
    set_target_res = client.post('/api/career/target-career/', {'career_id': target_cp.id}, format='json')
    assert set_target_res.status_code == status.HTTP_200_OK
    profile.refresh_from_db()
    assert profile.target_career_id == target_cp.id, "Target career must be updated in StudentProfile"
    print(f"[PASS] Set as Target Role successfully updated target to '{target_cp.title}' (ID {target_cp.id})")

    # TEST CASE 8: Skill Gap integration
    gap_res = client.get(f'/api/career/skill-gap/?career_id={target_cp.id}')
    assert gap_res.status_code == status.HTTP_200_OK
    gap_data = gap_res.json()
    assert gap_data['career_path'] == target_cp.id, f"Skill Gap Analyzer must analyze targeted career {target_cp.id}"
    assert 'readiness_score' in gap_data
    print(f"[PASS] Skill Gap Analyzer analyzed target career path '{target_cp.title}' (Readiness: {gap_data['readiness_score']}%)")

    # TEST CASE 9: Invalid Answer validation
    invalid_res = client.post(submit_url, {'answers': {99999: 99999}}, format='json')
    # Should safely handle without 500 error
    assert invalid_res.status_code in (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST)
    print("[PASS] Invalid answer handled safely without server crash")

    # TEST CASE 10: Career Paths list accessible by student
    paths_res = client.get('/api/career/paths/')
    assert paths_res.status_code == status.HTTP_200_OK, f"Authenticated student must be able to list career paths, got {paths_res.status_code}"
    print(f"[PASS] Authenticated student can list career paths: {len(paths_res.json())} paths found")

    # Cleanup test user
    User.objects.filter(username=username).delete()

    print("=" * 60)
    print("ALL 10 TEST CASES PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
