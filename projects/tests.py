import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from users.models import User

from .models import Project


TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class BaseTestCase(TestCase):
    pass


def make_user(
    email="user@example.com",
    name="Иван",
    surname="Иванов",
    password="testpass123",
):
    return User.objects.create_user(
        email=email, name=name, surname=surname, password=password
    )


def make_project(owner, name="Тестовый проект", status="open"):
    return Project.objects.create(name=name, owner=owner, status=status)


class ProjectModelTest(BaseTestCase):
    def test_str_returns_name(self):
        user = make_user()
        project = make_project(user)
        self.assertEqual(str(project), "Тестовый проект")

    def test_default_status_open(self):
        user = make_user()
        project = make_project(user)
        self.assertEqual(project.status, "open")

    def test_ordering_newest_first(self):
        user = make_user()
        p1 = make_project(user, name="Первый")
        p2 = make_project(user, name="Второй")
        projects = list(Project.objects.all())
        self.assertEqual(projects[0], p2)
        self.assertEqual(projects[1], p1)


class ProjectFormTest(BaseTestCase):
    def test_valid_form(self):
        from .forms import ProjectForm

        form = ProjectForm(
            data={
                "name": "Мой проект",
                "description": "Описание",
                "github_url": "https://github.com/user/repo",
                "status": "open",
            }
        )
        self.assertTrue(form.is_valid())

    def test_name_required(self):
        from .forms import ProjectForm

        form = ProjectForm(
            data={
                "name": "",
                "description": "",
                "github_url": "",
                "status": "open",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_invalid_github_url_rejected(self):
        from .forms import ProjectForm

        form = ProjectForm(
            data={
                "name": "Проект",
                "description": "",
                "github_url": "https://gitlab.com/user/repo",
                "status": "open",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_empty_github_url_allowed(self):
        from .forms import ProjectForm

        form = ProjectForm(
            data={
                "name": "Проект",
                "description": "",
                "github_url": "",
                "status": "open",
            }
        )
        self.assertTrue(form.is_valid())


class ProjectListViewTest(BaseTestCase):
    def setUp(self):
        self.user = make_user()
        for i in range(15):
            make_project(self.user, name=f"Проект {i}")

    def test_first_page_has_12_projects(self):
        response = self.client.get(reverse("projects:project_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["projects"]), 12)

    def test_second_page_has_remaining(self):
        response = self.client.get(reverse("projects:project_list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["projects"]), 3)


class ProjectDetailViewTest(BaseTestCase):
    def test_returns_project_in_context(self):
        user = make_user()
        project = make_project(user)
        response = self.client.get(
            reverse("projects:project_detail", kwargs={"project_id": project.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["project"], project)

    def test_404_for_nonexistent_project(self):
        response = self.client.get(
            reverse("projects:project_detail", kwargs={"project_id": 99999})
        )
        self.assertEqual(response.status_code, 404)


class CreateProjectViewTest(BaseTestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def test_unauthenticated_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("projects:create_project"))
        self.assertEqual(response.status_code, 302)

    def test_get_returns_form_with_is_edit_false(self):
        response = self.client.get(reverse("projects:create_project"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["is_edit"])

    def test_post_creates_project_and_redirects(self):
        response = self.client.post(
            reverse("projects:create_project"),
            {
                "name": "Новый проект",
                "description": "Описание",
                "github_url": "",
                "status": "open",
            },
        )
        project = Project.objects.get(name="Новый проект")
        self.assertRedirects(
            response,
            reverse("projects:project_detail", kwargs={"project_id": project.pk}),
        )

    def test_creator_is_owner_and_participant(self):
        self.client.post(
            reverse("projects:create_project"),
            {
                "name": "Мой проект",
                "description": "",
                "github_url": "",
                "status": "open",
            },
        )
        project = Project.objects.get(name="Мой проект")
        self.assertEqual(project.owner, self.user)
        self.assertIn(self.user, project.participants.all())


class EditProjectViewTest(BaseTestCase):
    def setUp(self):
        self.owner = make_user()
        self.other = make_user(email="other@example.com")
        self.project = make_project(self.owner)

    def test_get_prefills_form(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("projects:edit_project", kwargs={"project_id": self.project.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_edit"])

    def test_non_owner_gets_404(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("projects:edit_project", kwargs={"project_id": self.project.pk})
        )
        self.assertEqual(response.status_code, 404)


class CompleteProjectViewTest(BaseTestCase):
    def setUp(self):
        self.owner = make_user()
        self.project = make_project(self.owner)
        self.client.force_login(self.owner)

    def test_complete_open_project(self):
        response = self.client.post(
            reverse("projects:complete_project", kwargs={"project_id": self.project.pk})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["project_status"], "closed")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")

    def test_complete_already_closed_returns_400(self):
        self.project.status = "closed"
        self.project.save()
        response = self.client.post(
            reverse("projects:complete_project", kwargs={"project_id": self.project.pk})
        )
        self.assertEqual(response.status_code, 400)

    def test_non_owner_cannot_complete(self):
        other = make_user(email="other@example.com")
        self.client.force_login(other)
        response = self.client.post(
            reverse("projects:complete_project", kwargs={"project_id": self.project.pk})
        )
        self.assertEqual(response.status_code, 404)


class ToggleParticipateViewTest(BaseTestCase):
    def setUp(self):
        self.owner = make_user()
        self.participant = make_user(email="part@example.com")
        self.project = make_project(self.owner)
        self.client.force_login(self.participant)

    def test_join_project(self):
        response = self.client.post(
            reverse(
                "projects:toggle_participate",
                kwargs={"project_id": self.project.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["participant"])
        self.assertIn(self.participant, self.project.participants.all())

    def test_leave_project(self):
        self.project.participants.add(self.participant)
        response = self.client.post(
            reverse(
                "projects:toggle_participate",
                kwargs={"project_id": self.project.pk},
            )
        )
        data = response.json()
        self.assertFalse(data["participant"])
