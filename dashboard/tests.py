from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import UserProfile
from dashboard.models import DailyProgress, Habit, HabitLog, DailyGrowthScore, DailyTask, EveningReflection
from workouts.models import Exercise, WorkoutSession, WorkoutExercise
from growth.models import Goal, GrowthCategory, GoalHierarchy
from nutrition.models import FoodLog, MealEntry
from mind.models import MoodLog, JournalEntry
from learning.models import LearningGoal, LearningSession
from career.models import CareerProfile, CareerSkill, CareerMilestone
from habits.models import DisciplineHabit, DisciplineHabitLog
from skills_trade.models import SkillTradeListing, TradeRequest
from notifications.models import NotificationPreference, InAppNotification


class FullPersonalGrowthPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='subash_tester',
            email='tester@example.com',
            password='testpassword123',
            first_name='Subash'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            age=24,
            gender='male',
            height_cm=175.0,
            weight_kg=74.5,
            target_weight_kg=70.0,
            fitness_goal='fat_loss',
            body_goal='athletic',
            fitness_experience='intermediate',
            workout_location='gym',
            available_equipment=['full_gym'],
            daily_workout_minutes=45,
            workout_days_per_week=5,
            sleep_target_hours=8.0,
            water_target_liters=3.5,
            profile_completed=True
        )

    def test_holistic_multi_pillar_growth_score(self):
        """Test the 6-pillar holistic growth score calculation."""
        score = DailyGrowthScore.objects.create(
            user=self.user,
            body_score=85,
            mind_score=80,
            learning_score=75,
            career_score=70,
            discipline_score=80,
            habits_score=90
        )
        overall = score.compute_overall()
        self.assertGreaterEqual(overall, 75)
        self.assertLessEqual(overall, 100)

    def test_mind_checkin_and_journal(self):
        """Test mind 1-10 check-in and journal endpoints."""
        self.client.login(username='subash_tester', password='testpassword123')
        # Check-in update
        res = self.client.post('/mind/api/checkin/', {'field': 'focus', 'value': 9})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'ok')

        # Journal creation
        res2 = self.client.post('/mind/api/journal/', {
            'title': 'Test Reflection',
            'content': 'Focused morning on algorithms and solid recovery sleep.'
        })
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()['status'], 'ok')

    def test_learning_roadmap_and_study_log(self):
        """Test learning curriculum creation and study session logging."""
        self.client.login(username='subash_tester', password='testpassword123')
        res = self.client.post('/learning/api/create-roadmap/', {
            'topic': 'Python Concurrency',
            'category': 'programming',
            'target_hours': 30
        })
        self.assertEqual(res.status_code, 200)
        goal_id = res.json()['goal_id']

        res2 = self.client.post('/learning/api/log-session/', {
            'goal_id': goal_id,
            'duration_minutes': 60,
            'topics_covered': 'Asyncio & ThreadPoolExecutor',
            'problems_solved': 2
        })
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()['status'], 'ok')

    def test_career_matrix_and_milestones(self):
        """Test career target role, skill gap matrix, and milestone creation."""
        self.client.login(username='subash_tester', password='testpassword123')
        res = self.client.post('/career/api/skills/', {
            'action': 'add',
            'name': 'Docker',
            'proficiency': 'learning'
        })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(CareerSkill.objects.filter(user=self.user, skill_name='Docker').exists())

        res2 = self.client.post('/career/api/milestones/', {
            'action': 'add',
            'title': 'Deploy Microservice to AWS',
            'category': 'project'
        })
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(CareerMilestone.objects.filter(user=self.user, title='Deploy Microservice to AWS').exists())

    def test_habits_and_streaks(self):
        """Test discipline habit streak incrementing."""
        self.client.login(username='subash_tester', password='testpassword123')
        habit = DisciplineHabit.objects.create(user=self.user, name="Morning Meditation", icon="🧘")
        res = self.client.post('/habits/api/toggle/', {'habit_id': habit.id})
        self.assertEqual(res.status_code, 200)
        habit.refresh_from_db()
        self.assertEqual(habit.current_streak, 1)

    def test_skill_trade_marketplace(self):
        """Test peer skill exchange listing creation."""
        self.client.login(username='subash_tester', password='testpassword123')
        res = self.client.post('/skills-trade/api/create-listing/', {
            'skill_offering': 'Django Backend',
            'skill_seeking': 'Machine Learning',
            'description': '1 hr weekly tutoring exchange',
            'contact_handle': 'test_discord'
        })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(SkillTradeListing.objects.filter(user=self.user, skill_offering='Django Backend').exists())

    def test_goal_hierarchy(self):
        """Test 10-year cascading vision hierarchy."""
        self.client.login(username='subash_tester', password='testpassword123')
        res = self.client.post('/goals/api/hierarchy/', {
            'ten_year_vision': 'Lead AI Engineer',
            'yearly_goal': 'Land Senior Role',
            'monthly_goal': 'Build 2 Projects',
            'weekly_goal': 'Solve 10 DSA Problems',
            'daily_action': '60 min coding today'
        })
        self.assertEqual(res.status_code, 200)
        self.assertTrue(GoalHierarchy.objects.filter(user=self.user, ten_year_vision='Lead AI Engineer').exists())

    def test_notifications_system(self):
        """Test notification preferences, trigger test, and mark read."""
        self.client.login(username='subash_tester', password='testpassword123')
        
        # Test trigger alert
        res = self.client.post('/notifications/api/trigger-test/', {'type': 'workout'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['status'], 'ok')
        self.assertTrue(InAppNotification.objects.filter(user=self.user, notification_type='workout').exists())

        # Test mark read
        res2 = self.client.post('/notifications/api/mark-read/')
        self.assertEqual(res2.status_code, 200)
        self.assertFalse(InAppNotification.objects.filter(user=self.user, is_read=False).exists())
