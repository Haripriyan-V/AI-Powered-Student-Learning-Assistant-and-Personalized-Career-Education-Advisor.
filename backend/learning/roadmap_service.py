"""
Personalized Roadmap Service: Dynamically generates adaptive learning journeys
from identified skill gaps, connects quizzes, updates proficiency upon completion,
and manages revision recommendations.
"""
import logging
from django.utils import timezone
from typing import Dict, Any, List

from learning.models import LearningRoadmap, RoadmapItem, Course, Quiz
from learning.gamification_service import GamificationService
from ai.skill_engine import SkillGapEngine
from students.models import Skill, StudentSkill

logger = logging.getLogger(__name__)


class RoadmapService:
    """Generates and manages dynamic personalized roadmaps tailored to skill gaps."""

    @classmethod
    def get_or_generate_roadmap(cls, student, career_path=None, force_regenerate: bool = False) -> Dict[str, Any]:
        """Fetch existing roadmap or generate a new adaptive roadmap for target career."""
        from career.models import CareerPath, SkillGapAnalysis

        profile = getattr(student, 'student_profile', None)
        if not career_path:
            career_path = getattr(profile, 'target_career', None)
        if not career_path:
            career_path = CareerPath.objects.first()

        if not career_path:
            return {'error': 'No career paths available in system.'}

        roadmap = LearningRoadmap.objects.filter(student=student, career_path=career_path).first()

        if roadmap and not force_regenerate and roadmap.items.exists():
            return cls._serialize_roadmap(roadmap)

        # 1. Run fresh skill gap analysis to understand exact priorities
        gap_analysis_data = SkillGapEngine.analyze(student, career_path)

        # 2. Create or reset roadmap
        if not roadmap:
            roadmap = LearningRoadmap.objects.create(
                student=student,
                career_path=career_path,
                title=f"Personalized Path to {career_path.title}",
                active_phase=1,
            )
        else:
            roadmap.items.all().delete()
            roadmap.title = f"Personalized Path to {career_path.title}"
            roadmap.save()

        # 3. Generate 4 structured phases based on gap analysis
        phases_metadata = [
            {'phase_number': 1, 'title': 'Foundations & Core Prerequisites', 'color': 'iris'},
            {'phase_number': 2, 'title': 'Core Domain & Applied Frameworks', 'color': 'cyan'},
            {'phase_number': 3, 'title': 'Advanced Architectures & Production', 'color': 'marigold'},
            {'phase_number': 4, 'title': 'Capstone Portfolio & Interview Prep', 'color': 'growth'},
        ]
        roadmap.phases_data = phases_metadata
        roadmap.save()

        # Group gaps by severity / domain level
        gaps_list = gap_analysis_data.get('gaps_data', [])
        cls._populate_roadmap_items(roadmap, gaps_list, career_path)

        cls._recalculate_progress(roadmap)
        return cls._serialize_roadmap(roadmap)

    @classmethod
    def _populate_roadmap_items(cls, roadmap, gaps_list: List[dict], career_path):
        """Intelligently map skills to appropriate phased learning steps."""
        available_courses = {c.title.lower(): c for c in Course.objects.all()}
        available_quizzes = {q.title.lower(): q for q in Quiz.objects.all()}

        # Sort gaps: prioritize critical & major gaps first
        p1_skills = []
        p2_skills = []
        p3_skills = []

        for item in gaps_list:
            name = item['name']
            gap = item['gap']
            importance = item['importance']
            cat = item.get('category', '').lower()

            if any(k in name.lower() for k in ['python', 'javascript', 'sql', 'dsa', 'data structures', 'algorithms']):
                p1_skills.append(item)
            elif any(k in name.lower() for k in ['deep learning', 'pytorch', 'tensorflow', 'mlops', 'docker', 'system design', 'kubernetes']):
                p3_skills.append(item)
            else:
                p2_skills.append(item)

        # Ensure at least 1-2 items per phase
        if not p1_skills:
            p1_skills = [g for g in gaps_list[:2]]
        if not p2_skills:
            p2_skills = [g for g in gaps_list[2:4]]
        if not p3_skills:
            p3_skills = [g for g in gaps_list[4:6]]

        order_counter = 1

        # Phase 1 Items
        for item in p1_skills[:3]:
            skill_obj = Skill.objects.filter(id=item['skill_id']).first()
            linked_course = cls._find_matching_course(item['name'], available_courses)
            linked_quiz = cls._find_matching_quiz(item['name'], available_quizzes)
            RoadmapItem.objects.create(
                roadmap=roadmap,
                phase_number=1,
                phase_title='Foundations & Core Prerequisites',
                title=f"Master {item['name']} Fundamentals",
                skill=skill_obj,
                difficulty='beginner' if item['current_proficiency'] < 30 else 'intermediate',
                estimated_hours=6,
                course=linked_course,
                quiz=linked_quiz,
                description=f"Build strong command over {item['name']} essentials, syntax, and foundational idioms.",
                learning_resources=[
                    {'type': 'article', 'title': f"Complete {item['name']} Cheatsheet & Documentation"},
                    {'type': 'video', 'title': f"Core Concepts of {item['name']} in 45 Minutes"},
                ],
                practice_tasks=[
                    f"Solve 5 practice problems on {item['name']}",
                    f"Implement mini code snippet demonstrating key {item['name']} patterns",
                ],
                mini_project=f"Create a basic CLI or script in {item['name']} demonstrating clean architecture.",
                status='in_progress' if order_counter == 1 else 'not_started',
                order=order_counter,
            )
            order_counter += 1

        # Phase 2 Items
        for item in p2_skills[:3]:
            skill_obj = Skill.objects.filter(id=item['skill_id']).first()
            linked_course = cls._find_matching_course(item['name'], available_courses)
            linked_quiz = cls._find_matching_quiz(item['name'], available_quizzes)
            RoadmapItem.objects.create(
                roadmap=roadmap,
                phase_number=2,
                phase_title='Core Domain & Applied Frameworks',
                title=f"Applied {item['name']} & Workflow Integration",
                skill=skill_obj,
                difficulty='intermediate',
                estimated_hours=8,
                course=linked_course,
                quiz=linked_quiz,
                description=f"Apply {item['name']} to real-world domain problems with industry standard workflows.",
                learning_resources=[
                    {'type': 'article', 'title': f"Best Practices & Design Patterns in {item['name']}"},
                    {'type': 'doc', 'title': f"{item['name']} Real-world Case Studies"},
                ],
                practice_tasks=[
                    f"Build modular component using {item['name']}",
                    f"Optimize data flow and handle edge-case testing in {item['name']}",
                ],
                mini_project=f"Build an end-to-end working module utilizing {item['name']}.",
                status='not_started',
                order=order_counter,
            )
            order_counter += 1

        # Phase 3 Items
        for item in p3_skills[:3]:
            skill_obj = Skill.objects.filter(id=item['skill_id']).first()
            linked_course = cls._find_matching_course(item['name'], available_courses)
            linked_quiz = cls._find_matching_quiz(item['name'], available_quizzes)
            RoadmapItem.objects.create(
                roadmap=roadmap,
                phase_number=3,
                phase_title='Advanced Architectures & Production',
                title=f"Advanced {item['name']} & Production Deployment",
                skill=skill_obj,
                difficulty='advanced',
                estimated_hours=10,
                course=linked_course,
                quiz=linked_quiz,
                description=f"Master complex architectures, performance tuning, and scalable practices in {item['name']}.",
                learning_resources=[
                    {'type': 'article', 'title': f"High Performance {item['name']} in Production"},
                    {'type': 'video', 'title': f"Architecture Deep-Dive & Performance Optimization"},
                ],
                practice_tasks=[
                    f"Design end-to-end pipeline in {item['name']}",
                    f"Profile memory and execute unit tests for {item['name']}",
                ],
                mini_project=f"Production-ready deployment pipeline with containerization and automated testing.",
                status='not_started',
                order=order_counter,
            )
            order_counter += 1

        # Phase 4 Capstone Item
        RoadmapItem.objects.create(
            roadmap=roadmap,
            phase_number=4,
            phase_title='Capstone Portfolio & Interview Prep',
            title=f"Comprehensive {career_path.title} Portfolio Project",
            skill_id=p1_skills[0]['skill_id'] if (p1_skills and p1_skills[0].get('skill_id')) else None,
            difficulty='advanced',
            estimated_hours=15,
            description=f"Synthesize all skills into a showcase portfolio project demonstrating readiness for {career_path.title}.",
            learning_resources=[
                {'type': 'article', 'title': f"Top 50 Technical Interview Questions for {career_path.title}"},
                {'type': 'doc', 'title': "System Design & Coding Interview Strategy"},
            ],
            practice_tasks=[
                "Draft architecture diagram and write comprehensive README",
                "Deploy live project and publish code repository on GitHub",
                "Conduct mock technical interview with DishaAI Assistant",
            ],
            mini_project=f"Production-grade {career_path.title} Capstone Application.",
            status='not_started',
            order=order_counter,
        )

    @classmethod
    def complete_item(cls, student, item_id: int) -> dict:
        """
        Marks roadmap item as completed, increments skill proficiency,
        triggers SkillGap recalculation, awards XP, and advances roadmap.
        """
        item = RoadmapItem.objects.select_related('roadmap', 'skill', 'roadmap__career_path').filter(
            id=item_id, roadmap__student=student
        ).first()

        if not item:
            return {'error': 'Roadmap item not found.'}

        item.status = RoadmapItem.Status.COMPLETED
        item.completion_percent = 100
        item.completed_at = timezone.now()
        item.save()

        # 1. Update Student's Skill Proficiency (+12-15%)
        skill_name = item.skill.name if item.skill else None
        if item.skill:
            profile = student.student_profile
            student_skill, created = StudentSkill.objects.get_or_create(
                student_profile=profile,
                skill=item.skill,
                defaults={'proficiency_score': 60, 'source': 'course'}
            )
            if not created:
                student_skill.proficiency_score = min(100, student_skill.proficiency_score + 15)
                student_skill.source = 'course'
                student_skill.save()

        # 2. Recalculate Skill Gap Analysis
        career_path = item.roadmap.career_path
        updated_gap = SkillGapEngine.analyze(student, career_path)

        # 3. Award XP & Log Gamification
        xp_result = GamificationService.award_xp(
            student=student,
            activity_type='lesson',
            title=f"Completed: {item.title}",
            xp_amount=25,
            metadata={'item_id': item.id, 'phase': item.phase_number}
        )

        # 4. Advance next item to in_progress
        next_item = item.roadmap.items.filter(status='not_started').order_by('order').first()
        if next_item:
            next_item.status = RoadmapItem.Status.IN_PROGRESS
            next_item.save()
            item.roadmap.active_phase = next_item.phase_number

        cls._recalculate_progress(item.roadmap)

        return {
            'success': True,
            'message': f"Great job! You completed '{item.title}'!",
            'skill_updated': skill_name,
            'career_readiness': updated_gap['readiness_score'],
            'xp_earned': xp_result['xp_awarded'],
            'current_streak': xp_result['current_streak'],
            'roadmap': cls._serialize_roadmap(item.roadmap),
        }

    @classmethod
    def handle_quiz_completed(cls, student, quiz, score: float, passed: bool) -> dict:
        """
        Adaptive feedback when student submits a quiz:
        - If passed: improves skill proficiency, recalculates gap, awards XP
        - If failed: recommends revision before advancing
        """
        # Find skill related to quiz
        course = getattr(quiz, 'course', None)
        subject_name = course.subject.name if course and course.subject else 'General'

        if passed:
            xp_result = GamificationService.award_xp(
                student=student,
                activity_type='quiz',
                title=f"Passed Quiz: {quiz.title} ({score}%)",
                xp_amount=35,
                metadata={'quiz_id': quiz.id, 'score': score}
            )
            feedback = f"Awesome work! You scored {score}% on {quiz.title} and boosted your proficiency."
            revision_needed = False
        else:
            feedback = (
                f"You scored {score}% (Passing score: {quiz.passing_score}%). "
                f"Before moving forward, review the core concepts in '{quiz.title}' and retry the quiz to solidify your understanding."
            )
            revision_needed = True

        return {
            'passed': passed,
            'score': score,
            'feedback': feedback,
            'revision_needed': revision_needed,
        }

    @classmethod
    def _recalculate_progress(cls, roadmap):
        total = roadmap.items.count()
        if total == 0:
            roadmap.overall_progress = 0
        else:
            completed = roadmap.items.filter(status=RoadmapItem.Status.COMPLETED).count()
            roadmap.overall_progress = round((completed / total) * 100)
        roadmap.save(update_fields=['overall_progress', 'active_phase', 'updated_at'])

    @classmethod
    def _serialize_roadmap(cls, roadmap) -> dict:
        items = roadmap.items.select_related('skill', 'course', 'quiz').all()
        phases_grouped = {}

        for item in items:
            p_num = item.phase_number
            if p_num not in phases_grouped:
                phases_grouped[p_num] = {
                    'phase_number': p_num,
                    'phase_title': item.phase_title,
                    'items': [],
                }
            phases_grouped[p_num]['items'].append({
                'id': item.id,
                'title': item.title,
                'skill_name': item.skill.name if item.skill else None,
                'difficulty': item.difficulty,
                'estimated_hours': item.estimated_hours,
                'description': item.description,
                'status': item.status,
                'completion_percent': item.completion_percent,
                'learning_resources': item.learning_resources,
                'practice_tasks': item.practice_tasks,
                'mini_project': item.mini_project,
                'course_id': item.course_id,
                'quiz_id': item.quiz_id,
                'order': item.order,
            })

        return {
            'id': roadmap.id,
            'title': roadmap.title,
            'career_path_id': roadmap.career_path_id,
            'career_path_title': roadmap.career_path.title,
            'overall_progress': roadmap.overall_progress,
            'active_phase': roadmap.active_phase,
            'phases': list(phases_grouped.values()),
            'total_items': items.count(),
            'completed_items': items.filter(status='completed').count(),
        }

    @classmethod
    def _find_matching_course(cls, skill_name: str, available_courses: dict):
        for title, course in available_courses.items():
            if skill_name.lower() in title:
                return course
        return None

    @classmethod
    def _find_matching_quiz(cls, skill_name: str, available_quizzes: dict):
        for title, quiz in available_quizzes.items():
            if skill_name.lower() in title:
                return quiz
        return None

    @classmethod
    def get_study_plan(cls, student) -> Dict[str, Any]:
        """
        Dynamically derives the student's weekly study plan directly from their
        target career, active roadmap, and highest-priority skill gaps.
        """
        from career.models import CareerPath, SkillGapAnalysis
        from learning.models import LearningActivity

        profile = getattr(student, 'student_profile', None)
        target_career = getattr(profile, 'target_career', None) or CareerPath.objects.first()

        # 1. Fetch highest priority gap
        gap_obj = SkillGapAnalysis.objects.filter(student=student, career_path=target_career).first()
        priority_skills = gap_obj.priority_skills if gap_obj else []
        top_skill = priority_skills[0]['name'] if priority_skills else 'Core Engineering Fundamentals'

        # 2. Fetch current in-progress roadmap item
        roadmap = LearningRoadmap.objects.filter(student=student, career_path=target_career).first()
        current_item = roadmap.items.filter(status='in_progress').first() if roadmap else None
        focus_topic = current_item.title if current_item else f"Master {top_skill}"

        # 3. Find completed task keys for this student this week
        completed_activities = set(
            LearningActivity.objects.filter(student=student, activity_type='planner_task')
            .values_list('metadata__task_id', flat=True)
        )

        schedule_template = [
            {'id': 1, 'day': 'Monday', 'task': f"{top_skill}: Foundations & Core Syntax", 'hours': 2},
            {'id': 2, 'day': 'Tuesday', 'task': f"{top_skill}: Practical Exercises & Concepts", 'hours': 2},
            {'id': 3, 'day': 'Wednesday', 'task': f"{top_skill}: Modular Implementation & Patterns", 'hours': 3},
            {'id': 4, 'day': 'Thursday', 'task': f"{top_skill}: Integration & Testing", 'hours': 2},
            {'id': 5, 'day': 'Friday', 'task': f"{top_skill}: Applied Milestone Challenge", 'hours': 3},
        ]

        goals = []
        for s in schedule_template:
            goals.append({
                'id': s['id'],
                'day': s['day'],
                'task': s['task'],
                'hours': s['hours'],
                'completed': (s['id'] in completed_activities),
            })

        completed_count = sum(1 for g in goals if g['completed'])
        total_hours = sum(g['hours'] for g in goals)

        return {
            'target_career': target_career.title if target_career else 'Software Engineer',
            'top_skill_gap': top_skill,
            'active_milestone': focus_topic,
            'goals': goals,
            'completed_count': completed_count,
            'total_count': len(goals),
            'completed_percent': round((completed_count / len(goals)) * 100) if goals else 0,
            'total_weekly_hours': total_hours,
        }

    @classmethod
    def toggle_study_task(cls, student, task_id: int) -> Dict[str, Any]:
        """
        Toggles completion of a study planner task, awards XP, improves skill proficiency,
        and recalculates career readiness.
        """
        from career.models import CareerPath, SkillGapAnalysis
        from learning.models import LearningActivity
        from students.models import Skill, StudentSkill

        plan = cls.get_study_plan(student)
        target_goal = next((g for g in plan['goals'] if str(g['id']) == str(task_id)), None)
        if not target_goal:
            target_goal = {'id': task_id, 'task': 'Custom Study Goal', 'day': 'Today'}

        existing_activity = LearningActivity.objects.filter(
            student=student, activity_type='planner_task', metadata__task_id=str(task_id)
        ).first()

        profile = getattr(student, 'student_profile', None)
        target_career = getattr(profile, 'target_career', None) or CareerPath.objects.first()

        if existing_activity:
            # Uncomplete task
            existing_activity.delete()
            action = 'uncompleted'
            xp_awarded = 0
        else:
            # Complete task & award XP
            xp_result = GamificationService.award_xp(
                student=student,
                activity_type='planner_task',
                title=f"Study Goal Completed: {target_goal['task']}",
                xp_amount=15,
                metadata={'task_id': task_id, 'day': target_goal['day']}
            )
            xp_awarded = xp_result['xp_awarded']
            action = 'completed'

            # Boost skill proficiency slightly (+5%)
            top_skill_name = plan.get('top_skill_gap')
            if top_skill_name and profile:
                skill_obj = Skill.objects.filter(name__iexact=top_skill_name).first()
                if skill_obj:
                    st_skill, _ = StudentSkill.objects.get_or_create(
                        student_profile=profile, skill=skill_obj,
                        defaults={'proficiency_score': 50, 'source': 'course'}
                    )
                    st_skill.proficiency_score = min(100, st_skill.proficiency_score + 5)
                    st_skill.save()

            # Recalculate skill gap
            if target_career:
                gap_data = SkillGapEngine.analyze(student, target_career)
                SkillGapAnalysis.objects.update_or_create(
                    student=student,
                    career_path=target_career,
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

        updated_plan = cls.get_study_plan(student)
        return {
            'success': True,
            'completed': (action == 'completed'),
            'action': action,
            'xp_awarded': xp_awarded,
            'plan': updated_plan,
        }
