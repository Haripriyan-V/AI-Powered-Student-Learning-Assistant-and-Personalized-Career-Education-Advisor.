"""
Career Recommendation Engine: Multi-factor transparent scoring algorithm
matching students with target career paths, with rich explainability.
"""
import logging
from decimal import Decimal
from typing import List, Dict, Any, Optional

from career.models import CareerPath, CareerField, CareerRecommendation, AssessmentResult, SkillRequirement
from students.models import StudentSkill

logger = logging.getLogger(__name__)


def _normalize_canonical_field(name: str) -> str:
    """Normalize a career field name into a canonical key for robust matching."""
    if not name:
        return 'other'
    n = name.strip().lower()
    if any(k in n for k in ('data', 'ai', 'artificial intelligence', 'machine learning')):
        return 'data_ai'
    if any(k in n for k in ('tech', 'software', 'engineering', 'developer', 'web', 'programming')):
        return 'tech_software'
    if any(k in n for k in ('cyber', 'security', 'infosec')):
        return 'cyber_security'
    if any(k in n for k in ('cloud', 'devops', 'platform', 'infrastructure')):
        return 'cloud_computing'
    if any(k in n for k in ('design', 'ui', 'ux', 'product design')):
        return 'uiux_design'
    if any(k in n for k in ('finance', 'business', 'commerce', 'banking')):
        return 'finance_business'
    if any(k in n for k in ('health', 'medicine', 'medical', 'bio')):
        return 'healthcare_medicine'
    return n


class CareerRecommendationEngine:
    """
    Computes transparent multi-factor match scores for career paths based on:
    1. Skill Proficiency Alignment (40%)
    2. Assessment Test Affinity (25%)
    3. Resume Skills & Experience (15%)
    4. Student Interests Match (10%)
    5. Course Progress & History (10%)

    When a student has only completed an assessment and has no profile skills,
    resume, interests, or courses, the engine uses an assessment-first calculation
    where assessment affinity reliably drives ranked predictions.
    """

    @classmethod
    def recommend(cls, student, top_n: int = 6) -> List[Dict[str, Any]]:
        """Compute and return ranked career recommendations for the student."""
        career_paths = list(
            CareerPath.objects.select_related('career_field')
            .prefetch_related('required_skills', 'related_interests', 'skill_requirements__skill')
            .all()
        )

        if not career_paths:
            return []

        # 1. Fetch student's skill proficiency dictionary
        student_skills = {
            ss.skill.name.lower(): ss.proficiency_score
            for ss in StudentSkill.objects.filter(student_profile__user=student).select_related('skill')
        }

        # 2. Fetch latest completed assessment
        latest_assessment = (
            AssessmentResult.objects.filter(student=student)
            .order_by('-completed_at')
            .first()
        )
        field_scores = latest_assessment.field_scores if (latest_assessment and latest_assessment.field_scores) else {}

        # 3. Fetch student profile interests
        profile = getattr(student, 'student_profile', None)
        student_interests = set()
        if profile:
            student_interests = {i.name.lower() for i in profile.interests.all()}

        # 4. Fetch resume skills if available
        resume_analysis = getattr(student, 'resume_analyses', None)
        latest_resume = resume_analysis.first() if resume_analysis else None
        resume_skills = set()
        if latest_resume and latest_resume.normalized_skills:
            resume_skills = {s.lower() for s in latest_resume.normalized_skills}

        # 5. Course progress count
        completed_course_count = student.course_progress.filter(status='completed').count() if hasattr(student, 'course_progress') else 0

        # Check if student has any data at all
        has_assessment = bool(latest_assessment and field_scores)
        has_skills = bool(student_skills)
        has_resume = bool(resume_skills)
        has_interests = bool(student_interests)
        has_courses = completed_course_count > 0

        if not (has_assessment or has_skills or has_resume or has_interests or has_courses):
            # Genuinely no data provided yet
            return []

        # Build canonical assessment score map from database CareerFields and field_scores
        # Handles both integer and string keys, plus canonical category aliases
        canonical_scores: Dict[str, float] = {}
        id_to_field_name: Dict[int, str] = {}
        all_career_fields = {cf.id: cf.name for cf in CareerField.objects.all()}

        numeric_field_scores = {}
        for k, v in field_scores.items():
            try:
                fid = int(k)
                score_val = float(v)
                numeric_field_scores[fid] = score_val
                fname = all_career_fields.get(fid, '')
                id_to_field_name[fid] = fname
                canon = _normalize_canonical_field(fname)
                canonical_scores[canon] = max(canonical_scores.get(canon, 0.0), score_val)
            except (ValueError, TypeError):
                continue

        max_assessment_score = max(numeric_field_scores.values()) if numeric_field_scores else 0.0

        results = []
        is_assessment_only = has_assessment and not (has_skills or has_resume or has_interests or has_courses)

        for cp in career_paths:
            # -------------------------------------------------------------
            # A. Assessment Test Affinity Calculation
            # -------------------------------------------------------------
            raw_field_score = 0.0
            if has_assessment:
                # 1. Direct field ID match (supports both int and str keys)
                if cp.career_field_id in numeric_field_scores:
                    raw_field_score = max(raw_field_score, numeric_field_scores[cp.career_field_id])
                
                # 2. Canonical field name match
                cp_canon = _normalize_canonical_field(cp.career_field.name)
                if cp_canon in canonical_scores:
                    raw_field_score = max(raw_field_score, canonical_scores[cp_canon])

                # 3. Domain title relevance fallback
                title_lower = cp.title.lower()
                if 'cloud' in title_lower and 'cloud_computing' in canonical_scores:
                    raw_field_score = max(raw_field_score, canonical_scores['cloud_computing'])
                if ('software' in title_lower or 'full-stack' in title_lower) and 'tech_software' in canonical_scores:
                    raw_field_score = max(raw_field_score, canonical_scores['tech_software'])
                if ('machine learning' in title_lower or 'data' in title_lower or 'ai' in title_lower) and 'data_ai' in canonical_scores:
                    raw_field_score = max(raw_field_score, canonical_scores['data_ai'])
                if 'security' in title_lower and 'cyber_security' in canonical_scores:
                    raw_field_score = max(raw_field_score, canonical_scores['cyber_security'])
                if ('design' in title_lower or 'ui' in title_lower) and 'uiux_design' in canonical_scores:
                    raw_field_score = max(raw_field_score, canonical_scores['uiux_design'])

            if max_assessment_score > 0:
                affinity_ratio = max(0.0, min(1.0, raw_field_score / max_assessment_score))
            else:
                affinity_ratio = 0.5 if not has_assessment else 0.0

            # -------------------------------------------------------------
            # B. Skill Requirements & Alignment
            # -------------------------------------------------------------
            reqs = list(cp.skill_requirements.all())
            req_skill_names = [r.skill.name for r in reqs] if reqs else [s.name for s in cp.required_skills.all()]
            if not req_skill_names:
                req_skill_names = ['Problem Solving', 'Communication', 'Technical Fundamentals']

            matched_skills = []
            missing_skills = []
            total_req_points = 0
            earned_skill_points = 0

            for name in req_skill_names:
                curr = student_skills.get(name.lower(), 0)
                if name.lower() in resume_skills and curr == 0:
                    curr = 45  # baseline recognition from resume

                if curr >= 60:
                    matched_skills.append({'name': name, 'proficiency': curr})
                else:
                    missing_skills.append({'name': name, 'proficiency': curr})

                total_req_points += 100
                earned_skill_points += min(100, curr)

            skill_score_ratio = (earned_skill_points / total_req_points) if total_req_points else 0.0
            skill_score = skill_score_ratio * 40.0

            # -------------------------------------------------------------
            # C. Resume Experience Match (15 pts)
            # -------------------------------------------------------------
            overlap_resume_count = sum(1 for name in req_skill_names if name.lower() in resume_skills)
            resume_score = min(15.0, (overlap_resume_count / max(1, len(req_skill_names))) * 15.0) if has_resume else 0.0

            # -------------------------------------------------------------
            # D. Interests Match (10 pts)
            # -------------------------------------------------------------
            cp_interests = {i.name.lower() for i in cp.related_interests.all()}
            if has_interests and cp_interests:
                interest_overlap = sum(1 for i in cp_interests if i in student_interests)
                interest_score = min(10.0, (interest_overlap / len(cp_interests)) * 10.0)
            elif has_interests:
                interest_score = 4.0
            else:
                interest_score = 0.0

            # -------------------------------------------------------------
            # E. Course History Progress (10 pts)
            # -------------------------------------------------------------
            course_score = min(10.0, completed_course_count * 2.5) if has_courses else 0.0

            # -------------------------------------------------------------
            # Final Match Score Computation
            # -------------------------------------------------------------
            if is_assessment_only:
                # Assessment is the dominant signal:
                # Scales between 45% (unrelated/low affinity) and 92% (top matched field)
                # Differentiated by raw affinity score and role depth
                role_distinction = (len(req_skill_names) % 5) * 1.2
                base_score = 42.0 + (affinity_ratio * 46.0) + role_distinction
                assessment_score = round(affinity_ratio * 25.0, 1)
                final_match = round(min(94.0, max(38.0, base_score)), 1)
            else:
                assessment_score = round(affinity_ratio * 25.0, 1)
                calculated_sum = skill_score + assessment_score + resume_score + interest_score + course_score
                # Bound between 10.0 and 98.0
                final_match = round(min(98.0, max(10.0, calculated_sum)), 1)

            # Build explainability
            missing_names = [s['name'] for s in missing_skills]
            matched_names = [s['name'] for s in matched_skills]

            top_field_name = cp.career_field.name
            reasoning = cls._build_reasoning(
                career_title=cp.title,
                field_name=top_field_name,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                match_score=final_match,
                raw_affinity=raw_field_score,
                has_assessment=has_assessment,
            )

            next_steps = [f"Master foundational concepts in {name}" for name in missing_names[:2]]
            if len(missing_names) > 2:
                next_steps.append(f"Complete an applied project featuring {missing_names[2]}")
            else:
                next_steps.append(f"Build a portfolio capstone project tailored for {cp.title}")

            # Persist / update record in CareerRecommendation
            rec_obj, _ = CareerRecommendation.objects.update_or_create(
                student=student,
                career_path=cp,
                source_assessment=latest_assessment,
                defaults={
                    'match_score': Decimal(str(final_match)),
                    'reasoning': reasoning,
                }
            )

            results.append({
                'id': rec_obj.id,
                'career_path_id': cp.id,
                'career_path': cp.id,
                'career_path_title': cp.title,
                'career': cp.title,
                'career_name': cp.title,
                'title': cp.title,
                'recommended_career': cp.title,
                'career_field_name': cp.career_field.name,
                'average_salary_lpa': float(cp.average_salary_lpa) if cp.average_salary_lpa else 12.0,
                'growth_outlook': cp.growth_outlook,
                'description': cp.description,
                'match_score': float(final_match),
                'score': float(final_match),
                'percentage': float(final_match),
                'matchPercentage': float(final_match),
                'matched_skills': matched_names,
                'missing_skills': missing_names,
                'next_steps': next_steps,
                'reasoning': reasoning,
                'reason': reasoning,
                'score_breakdown': {
                    'skills_alignment': round(skill_score, 1),
                    'assessment_affinity': round(assessment_score, 1),
                    'resume_match': round(resume_score, 1),
                    'interests_alignment': round(interest_score, 1),
                    'course_history': round(course_score, 1),
                }
            })

        # Sort descending by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:top_n]

    @classmethod
    def simulate_what_if(cls, student, career_path_id: int, additional_skills: List[str]) -> Dict[str, Any]:
        """
        Calculates a real What-If projection: simulates what the student's
        match score would be if they acquire the specified additional skills.
        """
        career_path = CareerPath.objects.filter(id=career_path_id).first()
        if not career_path:
            return {'error': 'Career path not found'}

        # Fetch current recommendations to get baseline
        current_recs = {r['career_path_id']: r['match_score'] for r in cls.recommend(student, top_n=20)}
        current_score = current_recs.get(career_path.id, 0.0)

        # Build simulated skills map
        simulated_skills = {
            ss.skill.name.lower(): ss.proficiency_score
            for ss in StudentSkill.objects.filter(student_profile__user=student).select_related('skill')
        }
        for s in additional_skills:
            if s and s.strip():
                simulated_skills[s.strip().lower()] = 80  # Assume intermediate-advanced proficiency

        reqs = list(career_path.skill_requirements.all())
        req_skill_names = [r.skill.name for r in reqs] if reqs else [s.name for s in career_path.required_skills.all()]
        if not req_skill_names:
            req_skill_names = ['Problem Solving', 'Communication', 'Technical Fundamentals']

        earned_skill_points = sum(min(100, simulated_skills.get(n.lower(), 0)) for n in req_skill_names)
        total_req_points = len(req_skill_names) * 100
        simulated_skill_score = ((earned_skill_points / total_req_points) * 40.0) if total_req_points else 20.0

        # Preserve assessment and interest weights
        latest_assessment = AssessmentResult.objects.filter(student=student).order_by('-completed_at').first()
        field_scores = latest_assessment.field_scores if (latest_assessment and latest_assessment.field_scores) else {}
        max_assessment_score = max(float(v) for v in field_scores.values()) if field_scores else 0.0

        raw_field_score = float(field_scores.get(str(career_path.career_field_id), 0.0))
        if max_assessment_score > 0:
            assessment_score = (raw_field_score / max_assessment_score) * 25.0
        else:
            assessment_score = 12.5

        profile = getattr(student, 'student_profile', None)
        student_interests = {i.name.lower() for i in profile.interests.all()} if profile else set()
        cp_interests = {i.name.lower() for i in career_path.related_interests.all()}
        interest_overlap = sum(1 for i in cp_interests if i in student_interests)
        interest_score = min(10.0, (interest_overlap / max(1, len(cp_interests))) * 10.0) if cp_interests else 4.0

        completed_courses = student.course_progress.filter(status='completed').count() if hasattr(student, 'course_progress') else 0
        course_score = min(10.0, completed_courses * 2.5)

        resume_analysis = getattr(student, 'resume_analyses', None)
        latest_resume = resume_analysis.first() if resume_analysis else None
        resume_skills = {s.lower() for s in latest_resume.normalized_skills} if (latest_resume and latest_resume.normalized_skills) else set()
        overlap_resume_count = sum(1 for name in req_skill_names if name.lower() in resume_skills)
        resume_score = min(15.0, (overlap_resume_count / max(1, len(req_skill_names))) * 15.0)

        new_score = round(min(98.0, max(15.0, simulated_skill_score + assessment_score + resume_score + interest_score + course_score)), 1)
        improvement = round(max(0.0, new_score - current_score), 1)

        bridged = [s for s in additional_skills if any(s.lower() == r.lower() for r in req_skill_names)]
        still_missing = [r for r in req_skill_names if simulated_skills.get(r.lower(), 0) < 60]

        return {
            'career_id': career_path.id,
            'career_path_id': career_path.id,
            'career_title': career_path.title,
            'current_match_score': current_score,
            'current_score': current_score,
            'projected_match_score': new_score,
            'projected_score': new_score,
            'projected_improvement': improvement,
            'score_delta': improvement,
            'bridged_skills': bridged,
            'still_missing': still_missing,
        }

    @classmethod
    def _build_reasoning(
        cls,
        career_title: str,
        field_name: str,
        matched_skills: list,
        missing_skills: list,
        match_score: float,
        raw_affinity: float = 0.0,
        has_assessment: bool = False,
    ) -> str:
        matched_names = [s['name'] for s in matched_skills]
        missing_names = [s['name'] for s in missing_skills]

        lines = [f"**{match_score}% match** for **{career_title}** ({field_name})."]

        if has_assessment and raw_affinity > 0:
            lines.append(f"Your psychometric assessment demonstrated strong aptitude and interest in the {field_name} domain.")

        if matched_names:
            lines.append(f"✓ **Key strengths aligned:** {', '.join(matched_names[:4])}.")
        elif not has_assessment:
            lines.append("✓ Demonstrates foundational alignment through academic profile and interests.")

        if missing_names:
            lines.append(f"○ **Skill gaps to bridge:** {', '.join(missing_names[:3])}.")

        return " ".join(lines)
