"""
Management command to create demo data for testing.
Usage: python manage.py create_demo_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from problems.models import Problem, Tag, TestCase
from django.utils.text import slugify
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo data for testing CompileMate'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of demo users to create'
        )
        parser.add_argument(
            '--problems',
            type=int,
            default=20,
            help='Number of demo problems to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo data...'))

        # Create tags
        tags = self._create_tags()
        self.stdout.write(self.style.SUCCESS(f'Created {len(tags)} tags'))

        # Create users
        users = self._create_users(options['users'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(users)} demo users'))

        # Create problems
        problems = self._create_problems(options['problems'], tags)
        self.stdout.write(self.style.SUCCESS(f'Created {len(problems)} demo problems'))

        self.stdout.write(self.style.SUCCESS('Demo data creation complete!'))

    def _create_tags(self):
        """Create common problem tags."""
        tag_names = [
            'Array', 'String', 'Hash Table', 'Dynamic Programming',
            'Math', 'Sorting', 'Greedy', 'Depth-First Search',
            'Binary Search', 'Breadth-First Search', 'Tree', 'Graph',
            'Backtracking', 'Stack', 'Queue', 'Heap', 'Two Pointers',
            'Sliding Window', 'Recursion', 'Bit Manipulation'
        ]

        tags = []
        for name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={'description': f'Problems related to {name}'}
            )
            tags.append(tag)

        return tags

    def _create_users(self, count):
        """Create demo users."""
        users = []
        for i in range(count):
            username = f'demo_user_{i}'
            email = f'demo{i}@compilemate.com'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'coins': random.randint(50, 500),
                    'xp': random.randint(0, 5000),
                    'level': random.randint(1, 10),
                    'problems_solved': random.randint(0, 50),
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
                users.append(user)

        return users

    def _create_problems(self, count, tags):
        """Create demo problems."""
        problems = []
        difficulties = ['easy', 'medium', 'hard']

        problem_templates = [
            {
                'title': 'Two Sum',
                'description': 'Given an array of integers, return indices of two numbers that add up to a target.',
                'difficulty': 'easy',
                'tags': ['Array', 'Hash Table']
            },
            {
                'title': 'Reverse String',
                'description': 'Write a function that reverses a string.',
                'difficulty': 'easy',
                'tags': ['String', 'Two Pointers']
            },
            {
                'title': 'Valid Parentheses',
                'description': 'Given a string containing just the characters \'(\', \')\', \'{\', \'}\', \'[\' and \']\', determine if the input string is valid.',
                'difficulty': 'easy',
                'tags': ['String', 'Stack']
            },
            {
                'title': 'Merge Two Sorted Lists',
                'description': 'Merge two sorted linked lists and return it as a sorted list.',
                'difficulty': 'easy',
                'tags': ['Array', 'Sorting']
            },
            {
                'title': 'Maximum Subarray',
                'description': 'Given an integer array, find the contiguous subarray which has the largest sum.',
                'difficulty': 'medium',
                'tags': ['Array', 'Dynamic Programming']
            },
        ]

        for i in range(count):
            if i < len(problem_templates):
                template = problem_templates[i]
            else:
                template = {
                    'title': f'Demo Problem {i}',
                    'description': f'This is a demo problem for testing purposes. Solve this problem to earn coins!',
                    'difficulty': random.choice(difficulties),
                    'tags': random.sample([tag.name for tag in tags], k=random.randint(2, 4))
                }

            problem, created = Problem.objects.get_or_create(
                slug=slugify(template['title']),
                defaults={
                    'title': template['title'],
                    'description': template['description'],
                    'difficulty': template['difficulty'],
                    'status': 'published',
                    'constraints': 'Time: O(n), Space: O(1)',
                    'examples': [
                        {'input': '[2,7,11,15], target=9', 'output': '[0,1]'},
                        {'input': '[3,2,4], target=6', 'output': '[1,2]'}
                    ],
                    'starter_code': {
                        'python': 'def solution(arr):\n    pass',
                        'cpp': 'vector<int> solution(vector<int>& arr) {\n    \n}',
                    },
                    'acceptance_rate': random.uniform(20, 80),
                    'coin_reward': 10 if template['difficulty'] == 'easy' else 20 if template['difficulty'] == 'medium' else 30,
                    'xp_reward': 50 if template['difficulty'] == 'easy' else 100 if template['difficulty'] == 'medium' else 200,
                }
            )

            if created:
                # Add tags
                problem_tags = Tag.objects.filter(name__in=template['tags'])
                problem.tags.set(problem_tags)

                # Add test cases
                TestCase.objects.create(
                    problem=problem,
                    input_data='[2, 7, 11, 15]\n9',
                    expected_output='[0, 1]',
                    is_hidden=False,
                    order=1
                )
                TestCase.objects.create(
                    problem=problem,
                    input_data='[3, 2, 4]\n6',
                    expected_output='[1, 2]',
                    is_hidden=False,
                    order=2
                )

                problems.append(problem)

        return problems

