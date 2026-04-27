"""
Management command to create test users and projects.
"""
from django.core.management.base import BaseCommand
from users.models import User, Skill
from projects.models import Project


class Command(BaseCommand):
    help = "Create test users and projects"

    def handle(self, *args, **options):
        skills_data = [
            "Python", "Django", "JavaScript", "React", "Vue.js",
            "PostgreSQL", "Docker", "Git", "REST API", "Figma",
            "Flutter", "Go", "TypeScript", "Node.js", "CSS",
        ]
        skills = {}
        for name in skills_data:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills[name] = skill
        self.stdout.write(f"Created {len(skills)} skills")

        users_data = [
            {
                "email": "admin@example.com",
                "name": "Никита",
                "surname": "Воронов",
                "password": "admin123",
                "about": "Фулстек-разработчик с 5 годами опыта.",
                "phone": "+79001234567",
                "github_url": "https://github.com/alexivanov",
                "is_staff": True,
                "is_superuser": True,
                "skill_names": ["Python", "Django", "PostgreSQL", "Docker"],
            },
            {
                "email": "maria@yandex.ru",
                "name": "Екатерина",
                "surname": "Белова",
                "password": "password",
                "about": "Фронтенд-разработчик, люблю создавать красивые интерфейсы.",
                "phone": "+79009876543",
                "github_url": "https://github.com/mariapet",
                "skill_names": ["JavaScript", "React", "CSS", "Figma"],
            },
            {
                "email": "dmitry@mail.ru",
                "name": "Артём",
                "surname": "Крылов",
                "password": "password123",
                "about": "Мобильный разработчик, Flutter и Dart.",
                "phone": "+79005551234",
                "github_url": "https://github.com/dmitrys",
                "skill_names": ["Flutter", "Docker", "Git"],
            },
            {
                "email": "anna@gmail.com",
                "name": "Валерия",
                "surname": "Громова",
                "password": "securepass",
                "about": "Data Science и машинное обучение.",
                "phone": "+79007778899",
                "skill_names": ["Python", "PostgreSQL", "REST API"],
            },
        ]

        created_users = []
        for data in users_data:
            email = data["email"]
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                self.stdout.write(f"User {email} already exists")
            else:
                skill_names = data.pop("skill_names")
                extra = {k: v for k, v in data.items()
                         if k not in ("email", "name", "surname", "password")}
                user = User.objects.create_user(
                    email=data["email"],
                    name=data["name"],
                    surname=data["surname"],
                    password=data["password"],
                    **extra,
                )
                data["skill_names"] = skill_names
                for sname in skill_names:
                    user.skills.add(skills[sname])
                self.stdout.write(f"Created user {email}")
            created_users.append(user)

        projects_data = [
            {
                "owner_email": "admin@example.com",
                "name": "TeamFinder Platform",
                "description": "Платформа для поиска команды разработчиков для pet-проектов.",
                "github_url": "https://github.com/alexivanov/team-finder",
                "status": "open",
            },
            {
                "owner_email": "maria@yandex.ru",
                "name": "CoolUI Components",
                "description": "Библиотека React-компонентов с современным дизайном.",
                "github_url": "https://github.com/mariapet/cool-ui",
                "status": "open",
            },
            {
                "owner_email": "dmitry@mail.ru",
                "name": "FlutterGo App",
                "description": "Мобильное приложение для отслеживания личных целей.",
                "status": "open",
            },
            {
                "owner_email": "anna@gmail.com",
                "name": "ML Dashboard",
                "description": "Веб-дашборд для визуализации данных машинного обучения.",
                "github_url": "https://github.com/annakozlova/ml-dashboard",
                "status": "closed",
            },
            {
                "owner_email": "admin@example.com",
                "name": "DevBlog Engine",
                "description": "Движок для технических блогов разработчиков.",
                "status": "open",
            },
        ]

        for data in projects_data:
            owner_email = data.pop("owner_email")
            owner = User.objects.get(email=owner_email)
            if not Project.objects.filter(name=data["name"]).exists():
                project = Project.objects.create(owner=owner, **data)
                project.participants.add(owner)
                self.stdout.write(f"Created project: {project.name}")

        # Add some participants to projects
        tf_project = Project.objects.filter(name="TeamFinder Platform").first()
        if tf_project:
            for u in User.objects.exclude(email="admin@example.com"):
                tf_project.participants.add(u)

        cool_project = Project.objects.filter(name="CoolUI Components").first()
        if cool_project:
            admin_user = User.objects.get(email="admin@example.com")
            cool_project.participants.add(admin_user)

        self.stdout.write(self.style.SUCCESS("Test data created successfully!"))
