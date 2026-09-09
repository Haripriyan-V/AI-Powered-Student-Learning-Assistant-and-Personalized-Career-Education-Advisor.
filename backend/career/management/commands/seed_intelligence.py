"""
Management command: seed_intelligence
Populates skills across categories, career paths, and detailed skill requirements.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from career.models import CareerField, CareerPath, SkillRequirement
from students.models import Skill, Interest


CAREER_DOMAINS = [
    {
        'field': 'Data & Artificial Intelligence',
        'careers': [
            {
                'title': 'AI / Machine Learning Engineer',
                'description': 'Designs, trains, and deploys scalable machine learning and deep learning models into production.',
                'salary': 14.5,
                'growth': 'very_high',
                'skills': [
                    ('Python', 'Programming', 85, 5, True),
                    ('Machine Learning', 'Data Science & AI', 80, 5, True),
                    ('Deep Learning', 'Data Science & AI', 75, 4, True),
                    ('NumPy', 'Data Science & AI', 80, 4, False),
                    ('Pandas', 'Data Science & AI', 80, 4, False),
                    ('SQL', 'Databases', 75, 4, True),
                    ('Statistics', 'Data Science & AI', 75, 4, True),
                    ('PyTorch', 'Data Science & AI', 70, 4, False),
                    ('TensorFlow', 'Data Science & AI', 70, 3, False),
                    ('MLOps', 'Cloud & DevOps', 65, 3, False),
                    ('Docker', 'Cloud & DevOps', 65, 3, False),
                    ('Communication', 'Soft Skills', 75, 3, False),
                ]
            },
            {
                'title': 'Data Scientist',
                'description': 'Extracts actionable business insights, builds statistical predictive models, and delivers data-driven intelligence.',
                'salary': 12.0,
                'growth': 'high',
                'skills': [
                    ('Python', 'Programming', 85, 5, True),
                    ('SQL', 'Databases', 80, 5, True),
                    ('Statistics', 'Data Science & AI', 85, 5, True),
                    ('Pandas', 'Data Science & AI', 85, 4, True),
                    ('NumPy', 'Data Science & AI', 80, 4, True),
                    ('Machine Learning', 'Data Science & AI', 75, 4, True),
                    ('Data Analysis', 'Data Science & AI', 85, 4, True),
                    ('Communication', 'Soft Skills', 80, 4, False),
                ]
            },
        ]
    },
    {
        'field': 'Technology & Software Engineering',
        'careers': [
            {
                'title': 'Full-Stack Software Engineer',
                'description': 'Architects and builds complete web applications across frontend user interfaces and robust backend APIs.',
                'salary': 11.5,
                'growth': 'high',
                'skills': [
                    ('JavaScript', 'Programming', 85, 5, True),
                    ('React', 'Web Development', 85, 5, True),
                    ('Node.js', 'Web Development', 80, 4, True),
                    ('Python', 'Programming', 75, 4, True),
                    ('SQL', 'Databases', 75, 4, True),
                    ('REST APIs', 'Web Development', 85, 5, True),
                    ('Data Structures & Algorithms', 'Computer Science', 80, 5, True),
                    ('Git', 'Cloud & DevOps', 80, 4, True),
                    ('Docker', 'Cloud & DevOps', 65, 3, False),
                    ('Communication', 'Soft Skills', 75, 3, False),
                ]
            },
            {
                'title': 'Cloud DevOps & Platform Engineer',
                'description': 'Automates deployment pipelines, ensures cloud infrastructure reliability, security, and scalability.',
                'salary': 13.0,
                'growth': 'very_high',
                'skills': [
                    ('Linux', 'Operating Systems', 85, 5, True),
                    ('Docker', 'Cloud & DevOps', 85, 5, True),
                    ('Kubernetes', 'Cloud & DevOps', 80, 5, True),
                    ('AWS', 'Cloud & DevOps', 80, 5, True),
                    ('CI/CD Pipelines', 'Cloud & DevOps', 85, 5, True),
                    ('Python', 'Programming', 75, 4, True),
                    ('Git', 'Cloud & DevOps', 85, 4, True),
                    ('Problem Solving', 'Soft Skills', 80, 4, False),
                ]
            },
        ]
    },
    {
        'field': 'Cyber Security',
        'careers': [
            {
                'title': 'Cyber Security Analyst',
                'description': 'Monitors networks for security breaches, investigates incidents, and implements defensive cyber measures.',
                'salary': 11.0,
                'growth': 'very_high',
                'skills': [
                    ('Network Security', 'Security', 85, 5, True),
                    ('Linux', 'Operating Systems', 80, 5, True),
                    ('Cryptography', 'Security', 75, 4, True),
                    ('Ethical Hacking', 'Security', 80, 5, True),
                    ('Python', 'Programming', 75, 4, True),
                    ('SIEM', 'Security', 70, 4, False),
                    ('Problem Solving', 'Soft Skills', 80, 4, False),
                ]
            }
        ]
    },
    {
        'field': 'Cloud Computing',
        'careers': [
            {
                'title': 'Cloud Solutions Architect',
                'description': 'Architects robust, scalable, and secure cloud environments on AWS, Azure, and Google Cloud Platform.',
                'salary': 15.0,
                'growth': 'very_high',
                'skills': [
                    ('AWS', 'Cloud & DevOps', 85, 5, True),
                    ('Docker', 'Cloud & DevOps', 80, 5, True),
                    ('Kubernetes', 'Cloud & DevOps', 80, 5, True),
                    ('Linux', 'Operating Systems', 80, 4, True),
                    ('CI/CD Pipelines', 'Cloud & DevOps', 80, 4, True),
                    ('System Design', 'Computer Science', 85, 5, True),
                    ('Python', 'Programming', 75, 4, False),
                ]
            }
        ]
    },
    {
        'field': 'UI&UX DESIGN',
        'careers': [
            {
                'title': 'UI/UX & Product Designer',
                'description': 'Creates intuitive user experiences, wireframes, user journeys, and pixel-perfect interactive design systems.',
                'salary': 9.5,
                'growth': 'high',
                'skills': [
                    ('Figma', 'Design', 90, 5, True),
                    ('User Research', 'Design', 80, 5, True),
                    ('Wireframing', 'Design', 85, 5, True),
                    ('Prototyping', 'Design', 85, 5, True),
                    ('Design Systems', 'Design', 80, 4, True),
                    ('Communication', 'Soft Skills', 80, 4, False),
                ]
            }
        ]
    },
]


class Command(BaseCommand):
    help = 'Seeds standard skills, career paths, and detailed skill requirements.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding skills and career intelligence...")
        with transaction.atomic():
            for domain in CAREER_DOMAINS:
                field, _ = CareerField.objects.get_or_create(
                    name=domain['field'],
                    defaults={'description': f"Career opportunities in {domain['field']}"}
                )
                for c_data in domain['careers']:
                    career, _ = CareerPath.objects.update_or_create(
                        title=c_data['title'],
                        defaults={
                            'career_field': field,
                            'description': c_data['description'],
                            'average_salary_lpa': c_data['salary'],
                            'growth_outlook': c_data['growth'],
                        }
                    )
                    for s_name, s_cat, req_prof, imp, is_core in c_data['skills']:
                        skill, _ = Skill.objects.get_or_create(
                            name=s_name,
                            defaults={'category': s_cat}
                        )
                        SkillRequirement.objects.update_or_create(
                            career_path=career,
                            skill=skill,
                            defaults={
                                'required_proficiency': req_prof,
                                'importance': imp,
                                'is_core': is_core,
                            }
                        )
                        career.required_skills.add(skill)

        self.stdout.write(self.style.SUCCESS("Successfully seeded career and skill requirements!"))
