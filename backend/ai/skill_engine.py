"""
Skill Engine: Central intelligence module for skill normalization,
skill gap analysis, career readiness scoring, and priority calculation.
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Canonical normalization map: alias/variation -> canonical name
SKILL_NORMALIZATION_MAP = {
    # Programming Languages
    'python': 'Python',
    'python3': 'Python',
    'python programming': 'Python',
    'javascript': 'JavaScript',
    'js': 'JavaScript',
    'es6': 'JavaScript',
    'typescript': 'TypeScript',
    'ts': 'TypeScript',
    'java': 'Java',
    'core java': 'Java',
    'c++': 'C++',
    'cpp': 'C++',
    'c#': 'C#',
    'csharp': 'C#',
    'golang': 'Go',
    'go': 'Go',
    'rust': 'Rust',
    'php': 'PHP',
    'ruby': 'Ruby',
    'r': 'R',

    # Web & Frontend
    'react': 'React',
    'react.js': 'React',
    'reactjs': 'React',
    'react js': 'React',
    'next.js': 'Next.js',
    'nextjs': 'Next.js',
    'vue': 'Vue.js',
    'vue.js': 'Vue.js',
    'vuejs': 'Vue.js',
    'angular': 'Angular',
    'angularjs': 'Angular',
    'html': 'HTML5',
    'html5': 'HTML5',
    'css': 'CSS3',
    'css3': 'CSS3',
    'tailwind': 'Tailwind CSS',
    'tailwindcss': 'Tailwind CSS',
    'tailwind css': 'Tailwind CSS',
    'bootstrap': 'Bootstrap',
    'redux': 'Redux',

    # Backend & Frameworks
    'node': 'Node.js',
    'nodejs': 'Node.js',
    'node.js': 'Node.js',
    'express': 'Express.js',
    'expressjs': 'Express.js',
    'express.js': 'Express.js',
    'django': 'Django',
    'django rest framework': 'Django REST Framework',
    'drf': 'Django REST Framework',
    'fastapi': 'FastAPI',
    'flask': 'Flask',
    'spring': 'Spring Boot',
    'springboot': 'Spring Boot',
    'spring boot': 'Spring Boot',
    'graphql': 'GraphQL',
    'rest': 'REST APIs',
    'rest api': 'REST APIs',
    'restful api': 'REST APIs',
    'restful apis': 'REST APIs',

    # Databases
    'sql': 'SQL',
    'mysql': 'MySQL',
    'postgresql': 'PostgreSQL',
    'postgres': 'PostgreSQL',
    'sqlite': 'SQLite',
    'mongodb': 'MongoDB',
    'mongo': 'MongoDB',
    'redis': 'Redis',

    # Data Science, ML & AI
    'machine learning': 'Machine Learning',
    'ml': 'Machine Learning',
    'deep learning': 'Deep Learning',
    'dl': 'Deep Learning',
    'neural networks': 'Deep Learning',
    'artificial intelligence': 'Artificial Intelligence',
    'ai': 'Artificial Intelligence',
    'data science': 'Data Science',
    'data analysis': 'Data Analysis',
    'statistics': 'Statistics',
    'numpy': 'NumPy',
    'pandas': 'Pandas',
    'scikit-learn': 'Scikit-Learn',
    'sklearn': 'Scikit-Learn',
    'tensorflow': 'TensorFlow',
    'tf': 'TensorFlow',
    'pytorch': 'PyTorch',
    'torch': 'PyTorch',
    'nlp': 'Natural Language Processing',
    'natural language processing': 'Natural Language Processing',
    'computer vision': 'Computer Vision',
    'cv': 'Computer Vision',
    'genai': 'Generative AI',
    'generative ai': 'Generative AI',
    'llm': 'Large Language Models',
    'llms': 'Large Language Models',
    'transformers': 'Transformers (HuggingFace)',
    'huggingface': 'Transformers (HuggingFace)',
    'langchain': 'LangChain',
    'mlops': 'MLOps',

    # Cloud & DevOps
    'docker': 'Docker',
    'kubernetes': 'Kubernetes',
    'k8s': 'Kubernetes',
    'aws': 'AWS',
    'amazon web services': 'AWS',
    'azure': 'Microsoft Azure',
    'microsoft azure': 'Microsoft Azure',
    'gcp': 'Google Cloud Platform',
    'google cloud': 'Google Cloud Platform',
    'git': 'Git',
    'github': 'GitHub',
    'ci/cd': 'CI/CD Pipelines',
    'cicd': 'CI/CD Pipelines',
    'linux': 'Linux',

    # CS Fundamentals & Soft Skills
    'data structures': 'Data Structures & Algorithms',
    'dsa': 'Data Structures & Algorithms',
    'algorithms': 'Data Structures & Algorithms',
    'system design': 'System Design',
    'oop': 'Object-Oriented Programming',
    'object oriented programming': 'Object-Oriented Programming',
    'communication': 'Communication',
    'problem solving': 'Problem Solving',
    'teamwork': 'Team Collaboration',
    'agile': 'Agile / Scrum',
    'scrum': 'Agile / Scrum',
}

# Configurable Gap Classification Thresholds
GAP_THRESHOLDS = [
    (0, 10, 'Strong', 'success'),
    (11, 25, 'Minor Gap', 'info'),
    (26, 50, 'Moderate Gap', 'warning'),
    (51, 75, 'Major Gap', 'danger'),
    (76, 100, 'Critical Gap', 'critical'),
]


def normalize_skill_name(raw_name: str) -> str:
    """Normalize skill name to standard canonical casing and terminology."""
    if not raw_name:
        return ""
    clean = raw_name.strip().lower()
    return SKILL_NORMALIZATION_MAP.get(clean, raw_name.strip().title())


def classify_gap(gap_percentage: int) -> Tuple[str, str]:
    """Classify gap percentage into status label and color badge variant."""
    for low, high, label, variant in GAP_THRESHOLDS:
        if low <= gap_percentage <= high:
            return label, variant
    return 'Critical Gap', 'critical'


class SkillGapEngine:
    """
    Core engine that compares student skills against career path requirements,
    computes deterministic gap scores, prioritizes learning sequence, and produces
    rich explainable breakdown data for charts and dashboards.
    """

    @classmethod
    def analyze(cls, student, career_path) -> dict:
        """
        Execute full skill gap analysis between student and target career path.
        Returns a rich structured dictionary ready for database persistence and API responses.
        """
        from students.models import StudentSkill, Skill
        from career.models import SkillRequirement

        # 1. Fetch student's existing skills
        student_skills = {
            ss.skill.name.lower(): ss.proficiency_score
            for ss in StudentSkill.objects.filter(student_profile__user=student).select_related('skill')
        }

        # 2. Fetch career requirements (or fall back to career_path.required_skills M2M)
        requirements = list(
            SkillRequirement.objects.filter(career_path=career_path)
            .select_related('skill')
            .order_by('-importance', '-required_proficiency')
        )

        # If no explicit SkillRequirements yet, create or use M2M required_skills with sensible defaults
        if not requirements:
            m2m_skills = career_path.required_skills.all()
            if m2m_skills.exists():
                for skill in m2m_skills:
                    req, _ = SkillRequirement.objects.get_or_create(
                        career_path=career_path,
                        skill=skill,
                        defaults={'required_proficiency': 75, 'importance': 4, 'is_core': True}
                    )
                    requirements.append(req)

        # Fallback if career has zero requirements: populate default domain requirements
        if not requirements:
            requirements = cls._seed_default_requirements_for_career(career_path)

        skill_rows = []
        total_importance = 0
        weighted_fulfillment = 0.0

        counts = {
            'strong': 0,
            'minor': 0,
            'moderate': 0,
            'major': 0,
            'critical': 0,
        }

        category_accumulator = {}

        for req in requirements:
            skill_name = req.skill.name
            skill_category = req.skill.category or 'General'
            req_prof = req.required_proficiency
            importance = req.importance
            is_core = req.is_core

            curr_prof = student_skills.get(skill_name.lower(), 0)
            gap = max(0, req_prof - curr_prof)
            status_label, status_variant = classify_gap(gap)

            # Priority Formula: Importance * Gap * Career Relevance
            relevance_multiplier = 1.2 if is_core else 0.9
            priority_score = round(importance * gap * relevance_multiplier, 1)

            # Categorize counts
            if gap <= 10:
                counts['strong'] += 1
            elif gap <= 25:
                counts['minor'] += 1
            elif gap <= 50:
                counts['moderate'] += 1
            elif gap <= 75:
                counts['major'] += 1
            else:
                counts['critical'] += 1

            # Weighted career readiness contribution
            total_importance += importance
            fulfillment_ratio = min(1.0, curr_prof / req_prof) if req_prof > 0 else 1.0
            weighted_fulfillment += fulfillment_ratio * importance

            # Category stats for charts
            if skill_category not in category_accumulator:
                category_accumulator[skill_category] = {'current': 0, 'required': 0, 'count': 0}
            category_accumulator[skill_category]['current'] += curr_prof
            category_accumulator[skill_category]['required'] += req_prof
            category_accumulator[skill_category]['count'] += 1

            skill_rows.append({
                'skill_id': req.skill.id,
                'name': skill_name,
                'category': skill_category,
                'current_proficiency': curr_prof,
                'required_proficiency': req_prof,
                'gap': gap,
                'importance': importance,
                'is_core': is_core,
                'priority_score': priority_score,
                'status': status_label,
                'variant': status_variant,
            })

        # Overall Career Readiness Percentage
        if total_importance > 0:
            readiness_score = round((weighted_fulfillment / total_importance) * 100, 2)
        else:
            readiness_score = 0.0

        # Sort priority skills (highest priority score first)
        priority_skills = sorted(
            [s for s in skill_rows if s['gap'] > 0],
            key=lambda x: x['priority_score'],
            reverse=True
        )[:5]

        # Structure category summary for radar chart
        category_summary = []
        for cat, data in category_accumulator.items():
            cnt = data['count'] or 1
            category_summary.append({
                'category': cat,
                'current_avg': round(data['current'] / cnt, 1),
                'required_avg': round(data['required'] / cnt, 1),
            })

        # Generate Explainability
        ai_explanation = cls._generate_explainability(
            career_title=career_path.title,
            readiness=readiness_score,
            priority_skills=priority_skills,
            strong_count=counts['strong'],
            total_count=len(skill_rows),
        )

        return {
            'career_path_id': career_path.id,
            'career_title': career_path.title,
            'readiness_score': float(readiness_score),
            'total_skills_count': len(skill_rows),
            'counts': counts,
            'gaps_data': skill_rows,
            'priority_skills': priority_skills,
            'category_summary': category_summary,
            'ai_explanation': ai_explanation,
        }

    @classmethod
    def _generate_explainability(cls, career_title: str, readiness: float, priority_skills: list, strong_count: int, total_count: int) -> str:
        """Construct detailed, transparent explainability for student guidance."""
        if not priority_skills:
            return (
                f"Outstanding achievement! Your skill profile meets or exceeds all target requirements for "
                f"**{career_title}** with a Career Readiness of **{readiness}%**. "
                f"You are well positioned for interviews and senior project roles."
            )

        top_gap = priority_skills[0]
        top_name = top_gap['name']
        top_req = top_gap['required_proficiency']
        top_curr = top_gap['current_proficiency']
        top_gap_val = top_gap['gap']

        lines = [
            f"### Career Readiness Analysis for {career_title}",
            f"Your current career readiness is **{readiness}%**. You have demonstrated proficiency in **{strong_count} of {total_count}** core skills required for this role.",
            f"\n#### Biggest Growth Area: {top_name}",
            f"- **Target Requirement:** {top_req}%",
            f"- **Current Level:** {top_curr}% (Skill Gap: **{top_gap_val}%**)",
            f"- **Why it matters:** {top_name} is a foundational pillar for {career_title}. Closing this gap directly boosts your career readiness by up to {min(15, round(top_gap_val * 0.25))}%."
        ]

        if len(priority_skills) > 1:
            second = priority_skills[1]['name']
            lines.append(f"\n#### Recommended Learning Sequence:")
            lines.append(f"1. **{top_name}**: Master fundamental concepts, practical syntax, and mini-exercises.")
            lines.append(f"2. **{second}**: Progress to applied exercises and real-world integration.")
            if len(priority_skills) > 2:
                third = priority_skills[2]['name']
                lines.append(f"3. **{third}**: Combine into portfolio-grade capstone projects.")

        lines.append(f"\nYour personalized roadmap below has been dynamically customized to guide you through these priority skills step by step.")
        return "\n".join(lines)

    @classmethod
    def _seed_default_requirements_for_career(cls, career_path):
        """Seed reasonable skills and requirements if database is fresh."""
        from students.models import Skill
        from career.models import SkillRequirement

        title_lower = career_path.title.lower()
        skills_to_link = []

        if 'machine learning' in title_lower or 'ai' in title_lower or 'data science' in title_lower:
            skill_defs = [
                ('Python', 'Programming', 85, 5, True),
                ('Machine Learning', 'AI & ML', 80, 5, True),
                ('Deep Learning', 'AI & ML', 75, 4, True),
                ('NumPy', 'Data Science', 80, 4, False),
                ('Pandas', 'Data Science', 80, 4, False),
                ('SQL', 'Databases', 75, 4, True),
                ('Statistics', 'Data Science', 75, 4, True),
                ('PyTorch', 'AI & ML', 70, 4, False),
                ('TensorFlow', 'AI & ML', 70, 3, False),
                ('MLOps', 'DevOps & Cloud', 65, 3, False),
                ('Docker', 'DevOps & Cloud', 65, 3, False),
                ('Communication', 'Soft Skills', 75, 3, False),
            ]
        else: # Software Engineer / Full Stack
            skill_defs = [
                ('Python', 'Programming', 80, 4, True),
                ('JavaScript', 'Programming', 85, 5, True),
                ('React', 'Web Development', 85, 5, True),
                ('Node.js', 'Web Development', 80, 4, True),
                ('SQL', 'Databases', 75, 4, True),
                ('REST APIs', 'Web Development', 80, 4, True),
                ('Data Structures & Algorithms', 'Computer Science', 80, 5, True),
                ('Git', 'DevOps & Cloud', 80, 4, True),
                ('Docker', 'DevOps & Cloud', 65, 3, False),
                ('Communication', 'Soft Skills', 75, 3, False),
            ]

        req_list = []
        for name, category, req_prof, imp, is_core in skill_defs:
            skill, _ = Skill.objects.get_or_create(name=name, defaults={'category': category})
            req, _ = SkillRequirement.objects.get_or_create(
                career_path=career_path,
                skill=skill,
                defaults={
                    'required_proficiency': req_prof,
                    'importance': imp,
                    'is_core': is_core,
                }
            )
            req_list.append(req)
        return req_list
