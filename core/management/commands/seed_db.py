import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker
from users.models import User
from problems.models import Problem, Tag, Submission, TestCase
from contests.models import Contest, ContestProblem, ContestParticipation
from social_feed.models import Post, Comment
from jobs.models import Company, JobPosting
from teams.models import Team, TeamMembership
from learning_paths.models import LearningPath, Topic
from achievements.models import Badge, BadgeCategory

fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with robust dummy data for testing.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        with transaction.atomic():
            self.seed_users()
            self.seed_tags()
            self.seed_problems()
            self.seed_social()
            self.seed_companies_and_jobs()
            self.seed_teams()
            self.seed_achievements()
            self.seed_contests()
            self.seed_learning_paths()
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def seed_users(self):
        self.stdout.write('Seeding users...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write('Created superuser: admin')

        # Create 20 regular users
        for _ in range(20):
            username = fake.user_name()
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=fake.email(),
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                # Random stats
                user.xp = random.randint(100, 5000)
                user.coins = random.randint(50, 2000)
                user.problems_solved = random.randint(5, 100)
                user.save()

    def seed_tags(self):
        self.stdout.write('Seeding tags...')
        tags = ['Arrays', 'Strings', 'Dynamic Programming', 'Graph', 'Tree', 'Greedy', 'Backtracking', 'Bit Manipulation']
        for name in tags:
            Tag.objects.get_or_create(name=name, defaults={'description': f'Problems related to {name}'})

    def seed_problems(self):
        self.stdout.write('Seeding problems...')
        tags = list(Tag.objects.all())
        difficulties = ['easy', 'medium', 'hard']
        
        starter_code = {
            "python": "def solution(nums):\n    # Write your code here\n    pass",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    void solve(vector<int>& nums) {\n        \n    }\n};",
            "java": "class Solution {\n    public void solve(int[] nums) {\n        \n    }\n}",
            "javascript": "function solution(nums) {\n    // Write your code here\n}"
        }

        for _ in range(30):
            title = fake.sentence(nb_words=4).rstrip('.')
            problem, created = Problem.objects.get_or_create(
                slug=fake.slug(),
                defaults={
                    'title': title,
                    'description': fake.paragraph(nb_sentences=10),
                    'difficulty': random.choice(difficulties),
                    'status': 'published',
                    'starter_code': starter_code,
                    'total_submissions': random.randint(10, 500),
                    'accepted_submissions': random.randint(0, 10),
                }
            )
            if created:
                problem.tags.set(random.sample(tags, k=random.randint(1, 3)))
                # Create Test Cases
                TestCase.objects.create(problem=problem, input_data="[1, 2, 3]", expected_output="6", is_hidden=False, order=1)
                TestCase.objects.create(problem=problem, input_data="[-1, 1]", expected_output="0", is_hidden=True, order=2)

    def seed_social(self):
        self.stdout.write('Seeding social feed...')
        users = list(User.objects.all())
        post_types = ['achievement', 'solution', 'discussion']
        
        for _ in range(50):
            author = random.choice(users)
            post = Post.objects.create(
                author=author,
                content=fake.paragraph(),
                post_type=random.choice(post_types),
                likes_count=random.randint(0, 100)
            )
            # Add comments
            for _ in range(random.randint(0, 5)):
                Comment.objects.create(
                    post=post,
                    author=random.choice(users),
                    content=fake.sentence()
                )

    def seed_companies_and_jobs(self):
        self.stdout.write('Seeding jobs...')
        for _ in range(10):
            company, _ = Company.objects.get_or_create(
                name=fake.company(),
                defaults={
                    'slug': fake.slug(),
                    'description': fake.bs(),
                    'website': fake.url(),
                    'recruiter_email': fake.company_email(),
                    'recruiter_name': fake.name()
                }
            )
            
            for _ in range(random.randint(1, 5)):
                JobPosting.objects.create(
                    company=company,
                    title=fake.job(),
                    slug=fake.slug(),
                    description=fake.text(),
                    location=fake.city(),
                    salary_min=random.randint(60000, 100000),
                    salary_max=random.randint(120000, 200000),
                    job_type=random.choice(['full_time', 'internship', 'contract']),
                    experience_level=random.choice(['entry', 'mid', 'senior']),
                    min_experience_years=random.randint(0, 5),
                    expires_at=timezone.now() + timezone.timedelta(days=30),
                    status='active'
                )

    def seed_teams(self):
        self.stdout.write('Seeding teams...')
        users = list(User.objects.all())
        for _ in range(10):
            founder = random.choice(users)
            team_name = fake.bs().split()[0] + " Clan"
            if not Team.objects.filter(name=team_name).exists():
                team = Team.objects.create(
                    name=team_name,
                    slug=fake.slug(),
                    description=fake.catch_phrase(),
                    founder=founder,
                    is_public=True,
                    total_xp=random.randint(1000, 50000)
                )
                # Add members
                members = random.sample(users, k=random.randint(2, 5))
                for member in members:
                    if member != founder:
                        TeamMembership.objects.create(team=team, user=member, role='member')

    def seed_achievements(self):
        self.stdout.write('Seeding achievements...')
        cat, _ = BadgeCategory.objects.get_or_create(name='Problem Solving')
        badges = [
            ('First Step', 'Solve your first problem', 'bronze'),
            ('Algorithm Master', 'Solve 50 Hard problems', 'gold'),
            ('Streak Keeper', 'Maintain a 30-day streak', 'silver')
        ]
        for name, desc, tier in badges:
            Badge.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'tier': tier,
                    'badge_type': 'special',
                    'category': cat,
                    'requirement_value': 1
                }
            )

    def seed_contests(self):
        self.stdout.write('Seeding contests...')
        users = list(User.objects.all())
        # Past Contest
        Contest.objects.get_or_create(
            title="Bi-Weekly Contest 99",
            defaults={
                'slug': 'bi-weekly-99',
                'description': 'A fierce battle of algorithms.',
                'start_time': timezone.now() - timezone.timedelta(days=7),
                'end_time': timezone.now() - timezone.timedelta(days=7, hours=2),
                'duration': timezone.timedelta(hours=2),
                'status': 'finished',
                'created_by': users[0]
            }
        )
        # Upcoming
        Contest.objects.get_or_create(
            title="Weekly Contest 400",
            defaults={
                'slug': 'weekly-400',
                'description': 'Join us for the 400th edition!',
                'start_time': timezone.now() + timezone.timedelta(days=2),
                'end_time': timezone.now() + timezone.timedelta(days=2, hours=2),
                'duration': timezone.timedelta(hours=2),
                'status': 'upcoming',
                'created_by': users[0]
            }
        )

    def seed_learning_paths(self):
        self.stdout.write('Seeding learning paths...')
        # Ensure topics exist
        for topic_name in ['Python', 'Data Structures', 'Web Dev']:
            Topic.objects.get_or_create(name=topic_name, defaults={'description': f'Learn {topic_name}'})

        topics = list(Topic.objects.all())
        user = User.objects.first()
        
        path, created = LearningPath.objects.get_or_create(
            title="Mastering Data Structures",
            defaults={
                'slug': 'mastering-dsa',
                'description': 'Complete guide to Arrays, Linked Lists, Trees, and Graphs.',
                'difficulty': 'intermediate',
                'estimated_duration': 40,
                'created_by': user,
                'is_published': True
            }
        )
        if created:
            path.topics.set(topics)
