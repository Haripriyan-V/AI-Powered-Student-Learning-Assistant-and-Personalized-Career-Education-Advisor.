"""
Management command: seed_learning
----------------------------------
Populates the database with sample data for:
  - Subject
  - Course
  - LearningResource
  - Scholarship
  - College

Usage:
    python manage.py seed_learning
    python manage.py seed_learning --clear   # wipe and re-seed
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from learning.models import Subject, Course, LearningResource, Scholarship, College


SUBJECTS = [
    {'name': 'Computer Science', 'description': 'Programming, algorithms, software engineering, and more.'},
    {'name': 'Data Science & AI', 'description': 'Machine learning, statistics, and artificial intelligence.'},
    {'name': 'Mathematics', 'description': 'Pure and applied mathematics for competitive exams and beyond.'},
    {'name': 'Physics', 'description': 'Mechanics, electromagnetism, optics, and modern physics.'},
    {'name': 'Commerce & Finance', 'description': 'Accounting, economics, and business fundamentals.'},
    {'name': 'Biology & Life Sciences', 'description': 'Cell biology, genetics, ecology, and medical prep.'},
]

COURSES = [
    {
        'title': 'Python for Beginners',
        'subject': 'Computer Science',
        'level': 'beginner',
        'duration_hours': 20,
        'description': 'Learn Python programming from scratch — variables, loops, functions, and OOP.',
        'resources': [
            {'title': 'Intro to Python - Video Series', 'resource_type': 'video', 'url': 'https://youtube.com/playlist?list=PLGjplNEQ1it8-0CmoljS5yeV-GlKSUEt0'},
            {'title': 'Python Cheatsheet PDF', 'resource_type': 'pdf', 'url': 'https://perso.limsi.fr/pointal/python:memento'},
        ],
    },
    {
        'title': 'Data Structures & Algorithms',
        'subject': 'Computer Science',
        'level': 'intermediate',
        'duration_hours': 40,
        'description': 'Master arrays, linked lists, trees, graphs, sorting, and dynamic programming for placements.',
        'resources': [
            {'title': 'DSA Full Course', 'resource_type': 'video', 'url': 'https://youtu.be/8hly31xKli0'},
        ],
    },
    {
        'title': 'Machine Learning Fundamentals',
        'subject': 'Data Science & AI',
        'level': 'intermediate',
        'duration_hours': 35,
        'description': 'Understand supervised, unsupervised learning, model evaluation, and scikit-learn.',
        'resources': [
            {'title': 'ML Crash Course by Google', 'resource_type': 'link', 'url': 'https://developers.google.com/machine-learning/crash-course'},
        ],
    },
    {
        'title': 'Deep Learning with PyTorch',
        'subject': 'Data Science & AI',
        'level': 'advanced',
        'duration_hours': 50,
        'description': 'Build neural networks, CNNs, RNNs and Transformers using PyTorch.',
        'resources': [
            {'title': 'PyTorch Official Tutorials', 'resource_type': 'link', 'url': 'https://pytorch.org/tutorials/'},
        ],
    },
    {
        'title': 'JEE Mathematics — Calculus',
        'subject': 'Mathematics',
        'level': 'advanced',
        'duration_hours': 60,
        'description': 'Complete calculus preparation covering limits, derivatives, integration, and differential equations.',
        'resources': [
            {'title': 'NCERT Solutions - Mathematics', 'resource_type': 'pdf', 'url': 'https://ncert.nic.in/textbook.php'},
        ],
    },
    {
        'title': 'Class 12 Physics — Waves & Optics',
        'subject': 'Physics',
        'level': 'intermediate',
        'duration_hours': 30,
        'description': 'In-depth study of wave nature of light, interference, diffraction, and polarisation.',
        'resources': [
            {'title': 'Physics Wallah — Waves & Optics', 'resource_type': 'video', 'url': 'https://youtube.com/@PhysicsWallah'},
        ],
    },
    {
        'title': 'Accountancy for Class 12',
        'subject': 'Commerce & Finance',
        'level': 'beginner',
        'duration_hours': 25,
        'description': 'Partnership accounts, company accounts, and financial statements — complete CBSE guide.',
        'resources': [],
    },
    {
        'title': 'NEET Biology — Human Physiology',
        'subject': 'Biology & Life Sciences',
        'level': 'advanced',
        'duration_hours': 45,
        'description': 'Digestive, circulatory, respiratory, and nervous systems — NEET level coverage.',
        'resources': [
            {'title': 'NCERT Biology Textbook', 'resource_type': 'pdf', 'url': 'https://ncert.nic.in/textbook.php?kebo1=0-22'},
        ],
    },
]

SCHOLARSHIPS = [
    {
        'name': 'National Scholarship Portal — PM Scholarship',
        'provider': 'Ministry of Education, Govt. of India',
        'description': 'Central sector scholarship for meritorious students pursuing higher education.',
        'scholarship_type': 'merit',
        'amount': 12000,
        'eligibility': 'Students who cleared Class 12 in the top 20 percentile of their respective boards.',
        'application_url': 'https://scholarships.gov.in',
    },
    {
        'name': 'Post-Matric Scholarship for SC/ST/OBC',
        'provider': 'Ministry of Social Justice, Govt. of India',
        'description': 'Financial assistance to SC, ST, and OBC students for post-matric and post-secondary education.',
        'scholarship_type': 'government',
        'amount': 30000,
        'eligibility': 'SC/ST/OBC students with family income below ₹2.5 lakh per annum.',
        'application_url': 'https://scholarships.gov.in',
    },
    {
        'name': 'Aicte Pragati Scholarship (Girls)',
        'provider': 'AICTE',
        'description': 'Scholarship for girl students admitted to AICTE-approved institutions for technical education.',
        'scholarship_type': 'merit',
        'amount': 30000,
        'eligibility': 'Girl students in 1st year of Diploma/Degree in AICTE-approved institutions.',
        'application_url': 'https://scholarships.gov.in/fresh/loginPage',
    },
    {
        'name': 'Tata Capital Pankh Scholarship',
        'provider': 'Tata Capital Limited',
        'description': 'Supports underprivileged students from Classes 6–12 and undergraduates pursuing professional courses.',
        'scholarship_type': 'need',
        'amount': 15000,
        'eligibility': 'Students with family income below ₹4 lakh p.a. and above 60% in last exam.',
        'application_url': 'https://www.b4s.in/tatacapital/TPN7',
    },
    {
        'name': 'Inspire Scholarship — DST',
        'provider': 'Department of Science & Technology, Govt. of India',
        'description': 'Scholarships for students pursuing natural and basic sciences at the undergraduate and postgraduate level.',
        'scholarship_type': 'merit',
        'amount': 80000,
        'eligibility': 'Top 1% in Class 12 board exams pursuing BSc / BS / Int. MSc in Natural Sciences.',
        'application_url': 'https://www.online-inspire.gov.in/',
    },
    {
        'name': 'Sitaram Jindal Foundation Scholarship',
        'provider': 'Sitaram Jindal Foundation',
        'description': 'Monthly stipend for meritorious and needy students across various streams.',
        'scholarship_type': 'need',
        'amount': 24000,
        'eligibility': 'Students above 60% marks and family income below ₹2.5 lakh p.a.',
        'application_url': 'https://www.sitaramjindalfoundation.org/scholarship.php',
    },
]

COLLEGES = [
    {
        'name': 'Indian Institute of Technology, Bombay',
        'location': 'Mumbai, Maharashtra',
        'college_type': 'iit',
        'affiliation': 'Autonomous — UGC',
        'ranking': 3,
        'website': 'https://www.iitb.ac.in/',
        'established_year': 1958,
        'description': 'One of the premier engineering institutions in India, known for research and innovation.',
    },
    {
        'name': 'Indian Institute of Technology, Delhi',
        'location': 'New Delhi, Delhi',
        'college_type': 'iit',
        'affiliation': 'Autonomous — UGC',
        'ranking': 2,
        'website': 'https://home.iitd.ac.in/',
        'established_year': 1961,
        'description': 'Leading science and technology institute offering undergraduate, postgraduate, and doctoral programs.',
    },
    {
        'name': 'National Institute of Technology, Trichy',
        'location': 'Tiruchirappalli, Tamil Nadu',
        'college_type': 'nit',
        'affiliation': 'Deemed University — UGC',
        'ranking': 8,
        'website': 'https://www.nitt.edu/',
        'established_year': 1964,
        'description': 'One of the oldest and most reputed NITs, known for engineering programs and campus culture.',
    },
    {
        'name': 'BITS Pilani',
        'location': 'Pilani, Rajasthan',
        'college_type': 'deemed',
        'affiliation': 'Deemed University',
        'ranking': 26,
        'website': 'https://www.bits-pilani.ac.in/',
        'established_year': 1964,
        'description': 'Top-ranked private technical university with campuses in Pilani, Goa, Hyderabad, and Dubai.',
    },
    {
        'name': 'Jadavpur University',
        'location': 'Kolkata, West Bengal',
        'college_type': 'state',
        'affiliation': 'State University',
        'ranking': 12,
        'website': 'https://jadavpuruniversity.in/',
        'established_year': 1955,
        'description': 'Premier state university offering engineering, arts, and science programs with strong research output.',
    },
    {
        'name': 'IIIT Hyderabad',
        'location': 'Hyderabad, Telangana',
        'college_type': 'iiit',
        'affiliation': 'Deemed University',
        'ranking': 48,
        'website': 'https://www.iiit.ac.in/',
        'established_year': 1998,
        'description': 'Specialised institute focused on computer science and information technology research.',
    },
    {
        'name': 'Delhi University — North Campus',
        'location': 'New Delhi, Delhi',
        'college_type': 'central',
        'affiliation': 'Central University',
        'ranking': 11,
        'website': 'https://www.du.ac.in/',
        'established_year': 1922,
        'description': 'One of India\'s largest universities offering arts, science, commerce, and law programs.',
    },
    {
        'name': 'Vellore Institute of Technology (VIT)',
        'location': 'Vellore, Tamil Nadu',
        'college_type': 'deemed',
        'affiliation': 'Deemed University',
        'ranking': 11,
        'website': 'https://vit.ac.in/',
        'established_year': 1984,
        'description': 'Large private deemed university known for engineering and technology programs.',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample Learning app data (courses, scholarships, colleges).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing learning data before seeding.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing learning data...')
            Scholarship.objects.all().delete()
            College.objects.all().delete()
            LearningResource.objects.all().delete()
            Course.objects.all().delete()
            Subject.objects.all().delete()
            self.stdout.write(self.style.WARNING('  Existing data cleared.'))

        # Subjects
        self.stdout.write('Seeding subjects...')
        subject_map = {}
        for s in SUBJECTS:
            obj, created = Subject.objects.get_or_create(name=s['name'], defaults={'description': s['description']})
            subject_map[s['name']] = obj
            self.stdout.write(f"  {'[+]' if created else '[ ]'} Subject: {obj.name}")

        # Courses + resources
        self.stdout.write('Seeding courses and resources...')
        for c in COURSES:
            subject = subject_map.get(c['subject'])
            if not subject:
                self.stdout.write(self.style.ERROR(f"  Subject not found: {c['subject']}"))
                continue
            course, created = Course.objects.get_or_create(
                title=c['title'],
                defaults={
                    'subject': subject,
                    'level': c['level'],
                    'duration_hours': c['duration_hours'],
                    'description': c['description'],
                    'is_published': True,
                },
            )
            self.stdout.write(f"  {'[+]' if created else '[ ]'} Course: {course.title}")
            if created:
                for idx, r in enumerate(c.get('resources', [])):
                    LearningResource.objects.create(
                        course=course,
                        title=r['title'],
                        resource_type=r['resource_type'],
                        url=r.get('url'),
                        order=idx,
                    )

        # Scholarships
        self.stdout.write('Seeding scholarships...')
        for s in SCHOLARSHIPS:
            obj, created = Scholarship.objects.get_or_create(
                name=s['name'],
                defaults={k: v for k, v in s.items() if k != 'name'},
            )
            self.stdout.write(f"  {'[+]' if created else '[ ]'} Scholarship: {obj.name}")

        # Colleges
        self.stdout.write('Seeding colleges...')
        for c in COLLEGES:
            obj, created = College.objects.get_or_create(
                name=c['name'],
                defaults={k: v for k, v in c.items() if k != 'name'},
            )
            self.stdout.write(f"  {'[+]' if created else '[ ]'} College: {obj.name}")

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!'))
