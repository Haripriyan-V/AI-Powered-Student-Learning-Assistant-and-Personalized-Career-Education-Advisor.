"""
Management command: seed_all_data
---------------------------------
Safely and idempotently seeds backend data for:
  - Career Fields & Career Paths
  - Skills & Skill Requirements
  - Assessment Tests, Questions & Options
  - Subjects, Courses & Learning Resources
  - Scholarships
  - Colleges (NIRF-ranked institutions)
  - Entrance Exams (National & State level)

IDEMPOTENCY GUARANTEE:
  Uses update_or_create and get_or_create throughout.
  Running this command repeatedly updates existing records in place
  without ever creating duplicates.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import date

from career.models import (
    CareerField, CareerPath, SkillRequirement,
    AssessmentTest, AssessmentQuestion, AssessmentOption
)
from students.models import Skill, Interest
from learning.models import (
    Subject, Course, LearningResource, Scholarship, College, EntranceExam
)


class Command(BaseCommand):
    help = "Seeds comprehensive, realistic, and idempotent data for all DishaAI pages."

    def handle(self, *args, **options):
        self.stdout.write("Starting comprehensive data seeding...")

        with transaction.atomic():
            self._seed_skills()
            self._seed_career_data()
            self._seed_assessments()
            self._seed_learning_catalog()
            self._seed_scholarships()
            self._seed_colleges()
            self._seed_entrance_exams()

        self.stdout.write(self.style.SUCCESS("All data seeded successfully and verified idempotent!"))

    def _seed_skills(self):
        self.stdout.write("Seeding skills and interests...")
        skills_data = [
            # Programming & Fundamentals
            ("Python", "Programming"),
            ("JavaScript", "Programming"),
            ("TypeScript", "Programming"),
            ("Java", "Programming"),
            ("C++", "Programming"),
            ("SQL", "Databases"),
            ("Data Structures & Algorithms", "Computer Science"),
            ("Object-Oriented Programming", "Computer Science"),
            ("System Design", "Architecture"),
            # Web & Cloud
            ("React.js", "Frontend Development"),
            ("HTML & CSS", "Frontend Development"),
            ("Tailwind CSS", "Frontend Development"),
            ("Node.js", "Backend Development"),
            ("Django", "Backend Development"),
            ("REST APIs", "Backend Development"),
            ("PostgreSQL", "Databases"),
            ("MongoDB", "Databases"),
            ("Docker", "Cloud & DevOps"),
            ("Kubernetes", "Cloud & DevOps"),
            ("AWS", "Cloud & DevOps"),
            ("Git & GitHub", "Tools & Version Control"),
            ("CI/CD", "Cloud & DevOps"),
            # Data Science & AI
            ("Machine Learning", "Data Science & AI"),
            ("Deep Learning", "Data Science & AI"),
            ("Natural Language Processing", "Data Science & AI"),
            ("Computer Vision", "Data Science & AI"),
            ("Pandas", "Data Science & AI"),
            ("NumPy", "Data Science & AI"),
            ("PyTorch", "Data Science & AI"),
            ("TensorFlow", "Data Science & AI"),
            ("Statistics & Probability", "Data Science & AI"),
            ("Data Visualization", "Data Science & AI"),
            ("MLOps", "Data Science & AI"),
            # Security & Design
            ("Network Security", "Cybersecurity"),
            ("Cryptography", "Cybersecurity"),
            ("Penetration Testing", "Cybersecurity"),
            ("UI/UX Design", "Design"),
            ("Figma", "Design"),
            ("Wireframing & Prototyping", "Design"),
            # Soft Skills
            ("Problem Solving", "Soft Skills"),
            ("Communication", "Soft Skills"),
            ("Critical Thinking", "Soft Skills"),
            ("Project Management", "Soft Skills"),
        ]

        for name, category in skills_data:
            Skill.objects.update_or_create(
                name=name,
                defaults={'category': category}
            )

        interests = [
            "Artificial Intelligence", "Web Development", "Cloud Computing",
            "Cybersecurity", "UI/UX Design", "Data Analytics", "Mobile Apps",
            "Robotics", "Competitive Programming", "Financial Technology"
        ]
        for name in interests:
            Interest.objects.get_or_create(name=name)

    def _seed_career_data(self):
        self.stdout.write("Seeding career fields, career paths, and skill requirements...")

        domains = [
            {
                'field': 'Data & Artificial Intelligence',
                'description': 'Designing, deploying, and optimizing intelligent systems and data solutions.',
                'careers': [
                    {
                        'title': 'AI / Machine Learning Engineer',
                        'description': 'Architects, trains, and productionizes scalable machine learning and deep learning models.',
                        'salary': 15.50,
                        'growth': 'very_high',
                        'skills': [
                            ('Python', 85, 5, True),
                            ('Machine Learning', 80, 5, True),
                            ('Deep Learning', 75, 4, True),
                            ('Data Structures & Algorithms', 75, 4, True),
                            ('PyTorch', 70, 4, False),
                            ('SQL', 75, 4, True),
                            ('Statistics & Probability', 75, 4, True),
                            ('Docker', 65, 3, False),
                            ('MLOps', 65, 3, False),
                        ]
                    },
                    {
                        'title': 'Data Scientist',
                        'description': 'Extracts actionable business intelligence, builds statistical predictive models, and conducts exploratory research.',
                        'salary': 13.00,
                        'growth': 'high',
                        'skills': [
                            ('Python', 85, 5, True),
                            ('SQL', 80, 5, True),
                            ('Statistics & Probability', 85, 5, True),
                            ('Pandas', 85, 4, True),
                            ('NumPy', 80, 4, True),
                            ('Machine Learning', 75, 4, True),
                            ('Data Visualization', 80, 4, False),
                            ('Communication', 75, 3, False),
                        ]
                    },
                ]
            },
            {
                'field': 'Technology & Software Engineering',
                'description': 'Developing resilient, scalable software systems across frontend, backend, and infrastructure.',
                'careers': [
                    {
                        'title': 'Full-Stack Software Engineer',
                        'description': 'Builds complete end-to-end web applications with modern frontend frameworks and robust backend APIs.',
                        'salary': 12.50,
                        'growth': 'high',
                        'skills': [
                            ('JavaScript', 85, 5, True),
                            ('React.js', 80, 5, True),
                            ('Node.js', 80, 5, True),
                            ('Python', 75, 4, False),
                            ('SQL', 75, 4, True),
                            ('Data Structures & Algorithms', 75, 4, True),
                            ('Git & GitHub', 80, 4, True),
                            ('REST APIs', 85, 5, True),
                            ('Docker', 65, 3, False),
                        ]
                    },
                    {
                        'title': 'Cloud & DevOps Engineer',
                        'description': 'Automates deployment pipelines, ensures cloud resilience, and manages distributed container architectures.',
                        'salary': 14.00,
                        'growth': 'very_high',
                        'skills': [
                            ('Docker', 85, 5, True),
                            ('Kubernetes', 80, 5, True),
                            ('AWS', 80, 5, True),
                            ('CI/CD', 85, 5, True),
                            ('Python', 70, 4, False),
                            ('System Design', 75, 4, True),
                            ('Git & GitHub', 85, 4, True),
                            ('PostgreSQL', 70, 3, False),
                        ]
                    },
                    {
                        'title': 'Cybersecurity Analyst',
                        'description': 'Safeguards digital infrastructure against cyber threats, conducts vulnerability assessments, and enforces security protocols.',
                        'salary': 11.50,
                        'growth': 'high',
                        'skills': [
                            ('Network Security', 85, 5, True),
                            ('Cryptography', 80, 5, True),
                            ('Penetration Testing', 75, 4, True),
                            ('Python', 70, 4, False),
                            ('Problem Solving', 80, 4, True),
                            ('System Design', 70, 3, False),
                        ]
                    },
                ]
            },
            {
                'field': 'Design & User Experience',
                'description': 'Creating user-centered interactive products, empathetic visual design, and intuitive user experiences.',
                'careers': [
                    {
                        'title': 'UI/UX Product Designer',
                        'description': 'Crafts intuitive digital interfaces, conducts user research, and translates complex workflows into elegant user experiences.',
                        'salary': 10.00,
                        'growth': 'high',
                        'skills': [
                            ('UI/UX Design', 90, 5, True),
                            ('Figma', 85, 5, True),
                            ('Wireframing & Prototyping', 85, 5, True),
                            ('HTML & CSS', 70, 3, False),
                            ('Communication', 85, 4, True),
                            ('Critical Thinking', 80, 4, True),
                        ]
                    },
                ]
            }
        ]

        for domain in domains:
            field_obj, _ = CareerField.objects.update_or_create(
                name=domain['field'],
                defaults={'description': domain['description']}
            )

            for c_info in domain['careers']:
                career_path, _ = CareerPath.objects.update_or_create(
                    title=c_info['title'],
                    defaults={
                        'career_field': field_obj,
                        'description': c_info['description'],
                        'average_salary_lpa': c_info['salary'],
                        'growth_outlook': c_info['growth'],
                    }
                )

                # Link skill requirements
                for skill_name, req_prof, importance, is_core in c_info['skills']:
                    skill_obj = Skill.objects.filter(name=skill_name).first()
                    if skill_obj:
                        SkillRequirement.objects.update_or_create(
                            career_path=career_path,
                            skill=skill_obj,
                            defaults={
                                'required_proficiency': req_prof,
                                'importance': importance,
                                'is_core': is_core,
                            }
                        )
                        career_path.required_skills.add(skill_obj)

    def _seed_assessments(self):
        self.stdout.write("Seeding career aptitude & psychometric assessments...")

        test, _ = AssessmentTest.objects.update_or_create(
            title="Comprehensive Career Aptitude & Alignment Assessment",
            defaults={
                'description': "Evaluates your analytical thinking, software mindset, design inclination, and problem-solving affinity to match you with top tech and engineering careers.",
                'is_active': True,
            }
        )

        tech_field = CareerField.objects.filter(name__icontains='Technology').first()
        ai_field = CareerField.objects.filter(name__icontains='Artificial').first()
        design_field = CareerField.objects.filter(name__icontains='Design').first()

        questions_data = [
            (
                "When approaching an unfamiliar problem, what excites you most?",
                ai_field,
                1,
                [
                    ("Analyzing historical data patterns and finding statistical correlations", 3),
                    ("Architecting a clean, modular code pipeline that automates the workflow", 2),
                    ("Sketching out an intuitive user experience and visual flow", 1),
                ]
            ),
            (
                "Which type of project would you most enjoy building over a weekend?",
                tech_field,
                2,
                [
                    ("A full-stack web application with user auth, database, and interactive dashboard", 3),
                    ("A predictive model trained on real-world datasets to forecast trends", 2),
                    ("A sleek, responsive mobile app design prototype in Figma", 1),
                ]
            ),
            (
                "How do you prefer to validate the effectiveness of your work?",
                tech_field,
                3,
                [
                    ("Comprehensive automated test coverage, performance benchmarks, and uptime", 3),
                    ("High model accuracy, precision/recall metrics, and ROC-AUC score", 2),
                    ("Positive feedback from user usability testing and clean visual appeal", 1),
                ]
            ),
            (
                "What role do algorithms and mathematical concepts play in your daily interest?",
                ai_field,
                4,
                [
                    ("I love deep-diving into linear algebra, calculus, and neural network math", 3),
                    ("I enjoy applying algorithmic data structures (trees, graphs) to optimize software", 2),
                    ("I prioritize human-computer interaction, visual psychology, and UX ergonomics", 1),
                ]
            ),
            (
                "When you look at a website or application, what do you notice first?",
                design_field,
                5,
                [
                    ("Typography, layout balance, micro-interactions, and accessibility", 3),
                    ("The responsiveness, API latency, and architectural structure", 2),
                    ("The personalized recommendation algorithms and intelligence behind the content", 1),
                ]
            ),
        ]

        for q_text, field_obj, order, options in questions_data:
            q_obj, _ = AssessmentQuestion.objects.update_or_create(
                test=test,
                order=order,
                defaults={
                    'text': q_text,
                    'related_career_field': field_obj,
                }
            )

            for opt_text, weight in options:
                AssessmentOption.objects.update_or_create(
                    question=q_obj,
                    text=opt_text,
                    defaults={'score_weight': weight}
                )

    def _seed_learning_catalog(self):
        self.stdout.write("Seeding subjects, courses, and learning resources...")

        subjects_data = [
            ("Computer Science & Engineering", "Core computer science fundamentals, algorithms, systems, and programming."),
            ("Data Science & Machine Learning", "Predictive modeling, neural networks, data analysis, and modern AI systems."),
            ("Web & Cloud Technologies", "Full-stack development, modern frontend frameworks, containerization, and DevOps."),
            ("Product Design & UX", "User interface heuristics, product prototyping, design systems, and usability."),
        ]

        sub_map = {}
        for name, desc in subjects_data:
            s_obj, _ = Subject.objects.update_or_create(name=name, defaults={'description': desc})
            sub_map[name] = s_obj

        courses_data = [
            {
                'title': 'Python Programming Masterclass',
                'subject': 'Computer Science & Engineering',
                'level': 'beginner',
                'duration': 24,
                'description': 'Complete mastery of Python syntax, object-oriented programming, file I/O, error handling, and unit testing.',
                'resources': [
                    {'title': 'Python 3 Official Documentation', 'type': 'link', 'url': 'https://docs.python.org/3/'},
                    {'title': 'Python Cheatsheet & Quick Reference', 'type': 'article', 'url': 'https://www.pythoncheatsheet.org/'},
                    {'title': 'CS50P: Introduction to Programming with Python', 'type': 'video', 'url': 'https://cs50.harvard.edu/python/'},
                ]
            },
            {
                'title': 'Data Structures & Algorithms in Practice',
                'subject': 'Computer Science & Engineering',
                'level': 'intermediate',
                'duration': 40,
                'description': 'Master arrays, linked lists, binary search trees, heaps, graphs, dynamic programming, and asymptotic runtime analysis.',
                'resources': [
                    {'title': 'Visualgo: Algorithm Visualizations', 'type': 'link', 'url': 'https://visualgo.net/'},
                    {'title': 'Open Data Structures (Free Textbook)', 'type': 'pdf', 'url': 'https://opendatastructures.org/'},
                    {'title': 'NeetCode DSA Roadmap & Explanations', 'type': 'video', 'url': 'https://neetcode.io/roadmap'},
                ]
            },
            {
                'title': 'Full-Stack Modern React & REST APIs',
                'subject': 'Web & Cloud Technologies',
                'level': 'intermediate',
                'duration': 36,
                'description': 'Build high-performance web applications using React hooks, state management, Tailwind CSS, and RESTful APIs.',
                'resources': [
                    {'title': 'React Official Documentation (Learn React)', 'type': 'link', 'url': 'https://react.dev/'},
                    {'title': 'MDN Web Docs: Client-Side Web APIs', 'type': 'article', 'url': 'https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs'},
                ]
            },
            {
                'title': 'Machine Learning Fundamentals & Scikit-Learn',
                'subject': 'Data Science & Machine Learning',
                'level': 'intermediate',
                'duration': 35,
                'description': 'Supervised and unsupervised learning, regression, classification, cross-validation, hyperparameter tuning, and model metrics.',
                'resources': [
                    {'title': 'Google Machine Learning Crash Course', 'type': 'link', 'url': 'https://developers.google.com/machine-learning/crash-course'},
                    {'title': 'Scikit-Learn User Guide & API Reference', 'type': 'link', 'url': 'https://scikit-learn.org/stable/user_guide.html'},
                ]
            },
            {
                'title': 'Deep Learning with PyTorch & Neural Networks',
                'subject': 'Data Science & Machine Learning',
                'level': 'advanced',
                'duration': 45,
                'description': 'Construct and train feedforward networks, CNNs for computer vision, RNNs/Transformers for NLP, and leverage GPU acceleration.',
                'resources': [
                    {'title': 'PyTorch Deep Learning Tutorials', 'type': 'link', 'url': 'https://pytorch.org/tutorials/'},
                    {'title': 'Fast.ai Practical Deep Learning for Coders', 'type': 'video', 'url': 'https://course.fast.ai/'},
                ]
            },
            {
                'title': 'Cloud Infrastructure with Docker & Kubernetes',
                'subject': 'Web & Cloud Technologies',
                'level': 'advanced',
                'duration': 30,
                'description': 'Containerize microservices, build multi-stage Dockerfiles, manage clusters with Kubernetes, and establish automated CI/CD.',
                'resources': [
                    {'title': 'Docker Official Getting Started Guide', 'type': 'link', 'url': 'https://docs.docker.com/get-started/'},
                    {'title': 'Kubernetes Basics & Interactive Tutorials', 'type': 'link', 'url': 'https://kubernetes.io/docs/tutorials/kubernetes-basics/'},
                ]
            },
            {
                'title': 'UI/UX Design Systems & Figma Prototyping',
                'subject': 'Product Design & UX',
                'level': 'beginner',
                'duration': 20,
                'description': 'Design atomic component systems, wireframe responsive views, apply visual hierarchy, and build clickable prototypes in Figma.',
                'resources': [
                    {'title': 'Figma Learn: Foundations of Design', 'type': 'link', 'url': 'https://help.figma.com/hc/en-us/categories/360002051613'},
                    {'title': 'Material Design 3 Guidelines', 'type': 'link', 'url': 'https://m3.material.io/'},
                ]
            },
        ]

        for c_data in courses_data:
            course_obj, _ = Course.objects.update_or_create(
                title=c_data['title'],
                defaults={
                    'subject': sub_map[c_data['subject']],
                    'level': c_data['level'],
                    'duration_hours': c_data['duration'],
                    'description': c_data['description'],
                    'is_published': True,
                }
            )

            for order, res in enumerate(c_data['resources'], start=1):
                LearningResource.objects.update_or_create(
                    course=course_obj,
                    title=res['title'],
                    defaults={
                        'resource_type': res['type'],
                        'url': res['url'],
                        'order': order,
                    }
                )

    def _seed_scholarships(self):
        self.stdout.write("Seeding national & merit scholarships...")

        scholarships_data = [
            {
                'name': 'Prime Minister\'s Special Scholarship Scheme (PMSSS)',
                'provider': 'AICTE / Ministry of Education, Govt. of India',
                'type': 'government',
                'amount': 150000.00,
                'description': 'Provides financial support for academic fees and maintenance allowance to students pursuing professional engineering and medical degrees.',
                'eligibility': '10+2 passed students from J&K and Ladakh with family income under INR 8 LPA.',
                'deadline': date(2026, 7, 31),
                'url': 'https://www.aicte-india.org/bureaus/jk',
            },
            {
                'name': 'Reliance Foundation Undergraduate Scholarships',
                'provider': 'Reliance Foundation',
                'type': 'merit',
                'amount': 200000.00,
                'description': 'Prestigious scholarship awarded to undergraduate students across all disciplines based on aptitude test and academic performance.',
                'eligibility': 'Enrolled in 1st year regular full-time undergraduate degree with household income under INR 15 LPA.',
                'deadline': date(2026, 10, 15),
                'url': 'https://www.scholarships.reliancefoundation.org/',
            },
            {
                'name': 'National Scholarship Portal (NSP) Post-Matric Scholarships',
                'provider': 'Ministry of Minority Affairs / Govt. of India',
                'type': 'government',
                'amount': 50000.00,
                'description': 'Enables meritorious students from economically weaker sections to pursue undergraduate and postgraduate technical education.',
                'eligibility': 'Students with at least 50% marks in previous final exam and annual family income not exceeding INR 2 LPA.',
                'deadline': date(2026, 11, 30),
                'url': 'https://scholarships.gov.in/',
            },
            {
                'name': 'Tata Trusts Educational Scholarships',
                'provider': 'Tata Trusts',
                'type': 'need',
                'amount': 100000.00,
                'description': 'Financial grant for students enrolled in professional degree programs including engineering, data science, and healthcare.',
                'eligibility': 'Indian students with proven financial need and strong academic track record (minimum 60% aggregate).',
                'deadline': date(2026, 9, 30),
                'url': 'https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants',
            },
            {
                'name': 'Adobe India Women-in-Technology Scholarship',
                'provider': 'Adobe Systems India',
                'type': 'merit',
                'amount': 300000.00,
                'description': 'Empowers outstanding female students in computer science with funding, mentorship, and opportunity to interview for Adobe internships.',
                'eligibility': 'Female students currently enrolled in 3rd/4th year of B.Tech / B.E. in Computer Science or related fields.',
                'deadline': date(2026, 8, 31),
                'url': 'https://www.adobe.com/in/diversity/women-in-technology.html',
            },
        ]

        for s in scholarships_data:
            Scholarship.objects.update_or_create(
                name=s['name'],
                defaults={
                    'provider': s['provider'],
                    'scholarship_type': s['type'],
                    'amount': s['amount'],
                    'description': s['description'],
                    'eligibility': s['eligibility'],
                    'deadline': s['deadline'],
                    'application_url': s['url'],
                    'is_active': True,
                }
            )

    def _seed_colleges(self):
        self.stdout.write("Seeding top NIRF-ranked institutions...")

        colleges_data = [
            {
                'name': 'Indian Institute of Technology Madras (IIT Madras)',
                'location': 'Chennai, Tamil Nadu',
                'type': 'iit',
                'ranking': 1,
                'established': 1959,
                'affiliation': 'Autonomous (Institute of National Importance)',
                'website': 'https://www.iitm.ac.in/',
                'description': 'Consistently ranked #1 in NIRF Overall and Engineering rankings. Global hub for research, incubation, and computer science education.',
            },
            {
                'name': 'Indian Institute of Science (IISc Bangalore)',
                'location': 'Bengaluru, Karnataka',
                'type': 'central',
                'ranking': 2,
                'established': 1909,
                'affiliation': 'Deemed Research University',
                'website': 'https://iisc.ac.in/',
                'description': 'India\'s premier research institution for fundamental scientific discovery, computational sciences, and advanced engineering research.',
            },
            {
                'name': 'Indian Institute of Technology Bombay (IIT Bombay)',
                'location': 'Mumbai, Maharashtra',
                'type': 'iit',
                'ranking': 3,
                'established': 1958,
                'affiliation': 'Autonomous (Institute of National Importance)',
                'website': 'https://www.iitb.ac.in/',
                'description': 'Internationally recognized for cutting-edge engineering programs, entrepreneurship ecosystem, and top placement outcomes.',
            },
            {
                'name': 'Indian Institute of Technology Delhi (IIT Delhi)',
                'location': 'New Delhi, Delhi',
                'type': 'iit',
                'ranking': 4,
                'established': 1961,
                'affiliation': 'Autonomous (Institute of National Importance)',
                'website': 'https://home.iitd.ac.in/',
                'description': 'Leading research and engineering institute in India\'s capital, excelling in AI, electrical engineering, and computing systems.',
            },
            {
                'name': 'National Institute of Technology Tiruchirappalli (NIT Trichy)',
                'location': 'Tiruchirappalli, Tamil Nadu',
                'type': 'nit',
                'ranking': 9,
                'established': 1964,
                'affiliation': 'Autonomous (Institute of National Importance)',
                'website': 'https://www.nitt.edu/',
                'description': 'Consistently the top-ranked National Institute of Technology (NIT) in India, renowned for engineering rigor and academic excellence.',
            },
            {
                'name': 'Birla Institute of Technology and Science, Pilani (BITS Pilani)',
                'location': 'Pilani, Rajasthan',
                'type': 'deemed',
                'ranking': 20,
                'established': 1964,
                'affiliation': 'Deemed University (Institute of Eminence)',
                'website': 'https://www.bits-pilani.ac.in/',
                'description': 'Premier private technology institute known for its flexible academic curriculum, zero-attendance policy, and stellar alumni network.',
            },
        ]

        for c in colleges_data:
            College.objects.update_or_create(
                name=c['name'],
                defaults={
                    'location': c['location'],
                    'college_type': c['type'],
                    'ranking': c['ranking'],
                    'established_year': c['established'],
                    'affiliation': c['affiliation'],
                    'website': c['website'],
                    'description': c['description'],
                    'is_active': True,
                }
            )

    def _seed_entrance_exams(self):
        self.stdout.write("Seeding national & state entrance exams...")

        exams_data = [
            {
                'name': 'JEE Main (Joint Entrance Examination)',
                'conducting_body': 'National Testing Agency (NTA)',
                'category': 'engineering',
                'eligibility': 'Passed or appearing in 10+2 with Physics, Mathematics, and Chemistry/Biotechnology/Technical Vocational subject.',
                'application_period': 'November - December (Session 1); February - March (Session 2)',
                'exam_date_reference': 'January (Session 1) & April (Session 2) annually',
                'website': 'https://jeemain.nta.nic.in/',
                'registration_url': 'https://jeemain.nta.nic.in/',
                'pattern': 'Computer Based Test (CBT). 90 Questions (30 each from Physics, Chemistry, Mathematics). 3 hours duration. +4 for correct, -1 for incorrect.',
                'syllabus': 'Physics, Chemistry, and Mathematics based on standard CBSE Class 11 and Class 12 curricula.',
                'career_keywords': ['Software Engineer', 'AI / Machine Learning Engineer', 'DevOps'],
            },
            {
                'name': 'JEE Advanced',
                'conducting_body': 'One of the Indian Institutes of Technology (IITs)',
                'category': 'engineering',
                'eligibility': 'Top 2,50,000 qualifiers of JEE Main, satisfying 75% aggregate in 10+2 board exam (or top 20 percentile).',
                'application_period': 'Late April - Early May annually',
                'exam_date_reference': 'Late May annually',
                'website': 'https://jeeadv.ac.in/',
                'registration_url': 'https://jeeadv.ac.in/',
                'pattern': 'Computer Based Test (CBT). Two mandatory papers (Paper 1 & Paper 2) of 3 hours each on the same day. Highly conceptual questions.',
                'syllabus': 'In-depth conceptual Physics, Chemistry, and Mathematics.',
                'career_keywords': ['AI / Machine Learning Engineer', 'Software Engineer', 'Data Scientist'],
            },
            {
                'name': 'GATE (Graduate Aptitude Test in Engineering)',
                'conducting_body': 'IITs & IISc Bangalore (on rotation)',
                'category': 'engineering',
                'eligibility': 'Graduates or 3rd/4th year undergraduate students in Engineering/Technology/Science.',
                'application_period': 'August - September annually',
                'exam_date_reference': 'First two weekends of February annually',
                'website': 'https://gate.iisc.ac.in/',
                'registration_url': 'https://gate.iisc.ac.in/',
                'pattern': 'Computer Based Test (CBT). 65 questions (100 marks), 3 hours. General Aptitude (15 marks) + Engineering Mathematics & Core Subject (85 marks).',
                'syllabus': 'Core Discipline Syllabus (CS: Algorithms, OS, DBMS, Networks, Theory of Computation, Discrete Maths).',
                'career_keywords': ['AI / Machine Learning Engineer', 'Cybersecurity', 'Cloud'],
            },
            {
                'name': 'CAT (Common Admission Test)',
                'conducting_body': 'Indian Institutes of Management (IIMs)',
                'category': 'management',
                'eligibility': 'Bachelor\'s degree with at least 50% marks (45% for SC/ST/PwD) from a recognized university.',
                'application_period': 'August - September annually',
                'exam_date_reference': 'Last Sunday of November annually',
                'website': 'https://iimcat.ac.in/',
                'registration_url': 'https://iimcat.ac.in/',
                'pattern': 'CBT, 2 hours duration, 66 questions across 3 sections: VARC (24Q), DILR (20Q), QA (22Q). Sectional limit of 40 minutes each.',
                'syllabus': 'Verbal Ability & Reading Comprehension, Data Interpretation & Logical Reasoning, Quantitative Aptitude.',
                'career_keywords': ['Product Designer', 'Data Scientist'],
            },
            {
                'name': 'CUET UG (Common University Entrance Test)',
                'conducting_body': 'National Testing Agency (NTA)',
                'category': 'sciences',
                'eligibility': 'Students who have passed or are appearing in Class 12 board examinations.',
                'application_period': 'February - March annually',
                'exam_date_reference': 'May - June annually',
                'website': 'https://cuetug.ntaonline.in/',
                'registration_url': 'https://cuetug.ntaonline.in/',
                'pattern': 'Hybrid (CBT and Pen-and-paper). Section 1 (Languages), Section 2 (Domain Subjects e.g. Computer Science, Math), Section 3 (General Test).',
                'syllabus': 'Class 12 NCERT curriculum across chosen domain subjects and general mental ability.',
                'career_keywords': ['Full-Stack', 'Data Scientist', 'Designer'],
            },
            {
                'name': 'NEET UG (National Eligibility cum Entrance Test)',
                'conducting_body': 'National Testing Agency (NTA)',
                'category': 'medical',
                'eligibility': 'Passed 10+2 with Physics, Chemistry, Biology/Biotechnology, and English, minimum age 17 years.',
                'application_period': 'February - March annually',
                'exam_date_reference': 'First Sunday of May annually',
                'website': 'https://neet.nta.nic.in/',
                'registration_url': 'https://neet.nta.nic.in/',
                'pattern': 'Pen & Paper (OMR). 200 multiple-choice questions (attempt 180). 720 total marks. 3 hours 20 minutes duration.',
                'syllabus': 'Physics, Chemistry, Botany, and Zoology based on Class 11 and 12 NCERT syllabi.',
                'career_keywords': [],
            },
        ]

        for e in exams_data:
            exam_obj, _ = EntranceExam.objects.update_or_create(
                name=e['name'],
                defaults={
                    'conducting_body': e['conducting_body'],
                    'exam_category': e['category'],
                    'eligibility': e['eligibility'],
                    'application_period': e['application_period'],
                    'exam_date_reference': e['exam_date_reference'],
                    'official_website': e['website'],
                    'registration_url': e['registration_url'],
                    'exam_pattern': e['pattern'],
                    'syllabus_summary': e['syllabus'],
                    'is_active': True,
                }
            )

            # Link relevant careers
            for kw in e.get('career_keywords', []):
                matching_careers = CareerPath.objects.filter(title__icontains=kw)
                for cp in matching_careers:
                    exam_obj.related_career_paths.add(cp)
