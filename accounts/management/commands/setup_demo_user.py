"""
Django management command to create a demo user with rich data across all 10 life growth pillars.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from dashboard.models import DailyProgress, Habit, HabitLog, DailyGrowthScore, DailyTask, EveningReflection
from growth.models import GrowthCategory, Goal, GoalHierarchy
from progress.models import WeightHistory
from mind.models import MoodLog, JournalEntry
from learning.models import LearningGoal, LearningSession
from career.models import CareerProfile, CareerSkill, CareerMilestone
from habits.models import DisciplineHabit, DisciplineHabitLog
from skills_trade.models import SkillTradeListing
from notifications.models import NotificationPreference, InAppNotification
from coach.models import AIMemoryItem
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = "Creates or resets a complete demo user 'subash' with rich data across all 10 life growth dimensions."

    def handle(self, *args, **options):
        username = "subash"
        email = "subash@example.com"
        password = "password123"

        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": "Subash"}
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        # Profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.age = 24
        profile.gender = "male"
        profile.height_cm = 175.0
        profile.weight_kg = 74.5
        profile.target_weight_kg = 70.0
        profile.fitness_goal = "fat_loss"
        profile.body_goal = "athletic"
        profile.fitness_experience = "intermediate"
        profile.workout_location = "gym"
        profile.available_equipment = ["full_gym", "dumbbells", "pull_up_bar"]
        profile.daily_workout_minutes = 45
        profile.workout_days_per_week = 5
        profile.sleep_target_hours = 8.0
        profile.water_target_liters = 3.5
        profile.daily_schedule = "Software Engineer / Student (9 AM - 6 PM)"
        profile.available_free_hours = 3.5
        profile.mental_development_goals = ["Better focus", "Reduce procrastination", "Positive mindset"]
        profile.learning_goals_list = ["Python Backend", "DSA in C++", "AI / ML"]
        profile.career_target_role = "Python Backend & AI Engineer"
        profile.career_current_skills = ["Python", "Django", "SQL", "REST APIs"]
        profile.career_skills_to_learn = ["DSA", "System Design", "Docker", "Redis"]
        profile.personal_long_term_goals = "Become a Lead AI Architect & Build Scalable Systems"
        profile.profile_completed = True
        profile.save()

        today = timezone.now().date()

        # 1. Mind & Mental
        MoodLog.objects.update_or_create(
            user=user, date=today,
            defaults={
                'mood': 8, 'energy': 8, 'focus': 9, 'stress': 3,
                'motivation': 9, 'sleep_quality': 8, 'mental_clarity': 9
            }
        )
        JournalEntry.objects.get_or_create(
            user=user, date=today,
            defaults={
                'title': 'Focused deep work sprint',
                'content': 'Managed to complete 2 hours of deep work without touching my phone. Energy remained steady after the morning gym session.',
                'ai_reflection': 'Protecting your morning focus block has visibly boosted your cognitive output. Keep your phone outside the workspace.',
                'detected_patterns': ['Morning productivity peak', 'High focus after exercise'],
                'actionable_advice': 'Maintain this exact 90-minute focus window tomorrow morning.'
            }
        )

        # 2. Learning & Knowledge
        dsa_goal, _ = LearningGoal.objects.get_or_create(
            user=user,
            title="Data Structures & Algorithms (LeetCode)",
            defaults={
                'category': 'dsa',
                'target_hours': 60,
                'completed_hours': 24.5,
                'roadmap': [
                    {"week_number": 1, "week_title": "Arrays, Two Pointers & Hashing", "estimated_hours": 12, "completed": True},
                    {"week_number": 2, "week_title": "Sliding Window & Binary Search", "estimated_hours": 12, "completed": True},
                    {"week_number": 3, "week_title": "Linked Lists, Stacks & Queues", "estimated_hours": 12, "completed": False},
                    {"week_number": 4, "week_title": "Trees, Tries & Heap Patterns", "estimated_hours": 12, "completed": False},
                    {"week_number": 5, "week_title": "Graphs & Dynamic Programming", "estimated_hours": 12, "completed": False},
                ]
            }
        )
        LearningSession.objects.get_or_create(
            goal=dsa_goal, date=today,
            defaults={'duration_minutes': 60, 'topics_covered': 'Binary Search on Rotated Sorted Array', 'practice_problems_solved': 3}
        )

        # 3. Career & Skills Matrix
        car_prof, _ = CareerProfile.objects.get_or_create(user=user, defaults={'target_role': 'Python Backend & AI Engineer', 'interview_readiness_score': 74})
        career_skills = [
            ("Python", "advanced", False, 1),
            ("Django & DRF", "advanced", False, 2),
            ("SQL & PostgreSQL", "competent", False, 3),
            ("Data Structures & Algorithms", "learning", True, 4),
            ("System Design", "learning", True, 5),
            ("Docker & CI/CD", "learning", False, 6),
        ]
        for sname, prof, is_gap, order in career_skills:
            CareerSkill.objects.update_or_create(user=user, skill_name=sname, defaults={'proficiency': prof, 'is_critical_gap': is_gap, 'priority_order': order})

        CareerMilestone.objects.get_or_create(
            user=user, title="Build AI Life Coach Platform with Unit Tests",
            defaults={'category': 'project', 'completed': True}
        )
        CareerMilestone.objects.get_or_create(
            user=user, title="Complete 50 LeetCode Medium Problems",
            defaults={'category': 'interview_prep', 'completed': False}
        )

        # 4. Habits & Streaks
        habits_list = [
            ("Morning Sunlight & Cold Hydration", "☀️", 12),
            ("45-Minute Workout", "💪", 6),
            ("Read 20 Pages Non-Fiction", "📖", 8),
            ("60-Minute Focused Coding", "💻", 14),
            ("Zero Screen 30m Before Bed", "🌙", 5),
        ]
        for hname, hicon, streak in habits_list:
            hab, _ = DisciplineHabit.objects.get_or_create(user=user, name=hname, defaults={'icon': hicon, 'current_streak': streak, 'best_streak': max(streak, 15)})
            DisciplineHabitLog.objects.get_or_create(habit=hab, date=today, defaults={'completed': True})

        # 5. Long-term Goal Hierarchy
        GoalHierarchy.objects.get_or_create(
            user=user,
            ten_year_vision="Become a Principal AI & Backend Systems Architect and build impactful software globally.",
            defaults={
                'yearly_goal': "Land Senior Backend / AI Engineer position & launch 2 production open-source tools.",
                'monthly_goal': "Master Graph & Tree algorithms and implement Redis caching pipelines.",
                'weekly_goal': "Solve 10 LeetCode Mediums + 5 Gym sessions + 4 hours System Design.",
                'daily_action': "45 min Gym workout + 60 min DSA practice today."
            }
        )

        # 6. Skill Trading Marketplace Listings
        SkillTradeListing.objects.get_or_create(
            user=user,
            skill_offering="Python, Django & Backend Architecture",
            defaults={
                'skill_seeking': "Spoken English & Advanced System Design",
                'description': "Happy to do 1-on-1 backend code reviews and mentor in Django in exchange for mock technical interview practice.",
                'preferred_schedule': "Weekends (1 hr call)",
                'contact_handle': "Discord: subash_dev"
            }
        )

        # 7. AI Memory Items
        ai_memories = [
            ("preference", "Prefers Evening Workouts", "Has highest physical power output and mental focus between 5 PM and 7 PM."),
            ("strength", "Consistent Deep Work Ability", "Capable of sustaining 90-minute distraction-free coding blocks."),
            ("weakness", "Weekend Hydration Dip", "Tends to drink 1L less water on Saturdays/Sundays."),
            ("goal", "Target: Senior Python/AI Role", "Actively preparing for engineering interview rounds within 6 months.")
        ]
        for cat, title, detail in ai_memories:
            AIMemoryItem.objects.get_or_create(user=user, title=title, defaults={'category': cat, 'detail': detail, 'confidence': 'High'})

        # 8. Daily Tasks
        DailyTask.objects.get_or_create(user=user, date=today, title="Complete Chest & Triceps Workout", defaults={'priority': 'high', 'completed': True})
        DailyTask.objects.get_or_create(user=user, date=today, title="Solve 3 Tree Traversal Problems in DSA", defaults={'priority': 'high', 'completed': True})
        DailyTask.objects.get_or_create(user=user, date=today, title="Review System Design Caching Strategies", defaults={'priority': 'medium', 'completed': False})
        DailyTask.objects.get_or_create(user=user, date=today, title="Read 20 pages of Atomic Habits", defaults={'priority': 'low', 'completed': True})

        # 9. Evening Reflection
        EveningReflection.objects.update_or_create(
            user=user, date=today,
            defaults={
                'what_went_well': "Maintained laser focus during coding and hit my protein target cleanly.",
                'what_could_be_better': "Could have taken a short walk in the afternoon to refresh cognitive energy.",
                'one_improvement_tomorrow': "Take a 10-minute fresh air break after lunch.",
                'ai_summary': "Consistent high-performance day logged."
            }
        )

        # 10. Notification Preferences & In-App Alert
        NotificationPreference.objects.get_or_create(user=user)
        InAppNotification.objects.get_or_create(
            user=user,
            title="🎯 Great Weekly Momentum",
            defaults={'message': "You're on a 6-day workout streak! Your Body & Learning scores are both above 80% this week.", 'notification_type': 'coach'}
        )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded comprehensive data for user '{username}' across all 10 life growth pillars!"
        ))
