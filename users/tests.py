import json
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Skill, User


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


class SkillModelTest(BaseTestCase):
    def test_create_skill(self):
        skill = Skill.objects.create(name="Python")
        self.assertEqual(str(skill), "Python")

    def test_skill_name_unique(self):
        Skill.objects.create(name="Django")
        with self.assertRaises(Exception):
            Skill.objects.create(name="Django")


class UserModelTest(BaseTestCase):
    def test_create_user_generates_avatar(self):
        user = make_user()
        self.assertTrue(bool(user.avatar))

    def test_email_is_username_field(self):
        user = make_user(email="test2@example.com")
        self.assertEqual(user.get_username(), "test2@example.com")

    def test_is_active_default_true(self):
        user = make_user(email="active@example.com")
        self.assertTrue(user.is_active)

    def test_is_staff_default_false(self):
        user = make_user(email="staff@example.com")
        self.assertFalse(user.is_staff)


class RegisterFormTest(BaseTestCase):
    def test_valid_registration(self):
        from .forms import RegisterForm

        form = RegisterForm(
            data={
                "name": "Анна",
                "surname": "Смирнова",
                "email": "anna@example.com",
                "password": "securepass",
            }
        )
        self.assertTrue(form.is_valid())

    def test_duplicate_email_rejected(self):
        from .forms import RegisterForm

        make_user(email="dup@example.com")
        form = RegisterForm(
            data={
                "name": "Jane",
                "surname": "Doe",
                "email": "dup@example.com",
                "password": "pass",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class EditProfileFormTest(BaseTestCase):
    def setUp(self):
        self.user = make_user()

    def test_phone_8_normalizes_to_plus7(self):
        from .forms import EditProfileForm

        form = EditProfileForm(
            data={
                "name": "А",
                "surname": "Б",
                "phone": "89001234567",
                "about": "",
                "github_url": "",
            },
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["phone"], "+79001234567")

    def test_invalid_phone_rejected(self):
        from .forms import EditProfileForm

        form = EditProfileForm(
            data={
                "name": "А",
                "surname": "Б",
                "phone": "1234",
                "about": "",
                "github_url": "",
            },
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_duplicate_phone_rejected(self):
        from .forms import EditProfileForm

        other = make_user(email="other@example.com")
        other.phone = "+79001234567"
        other.save()
        form = EditProfileForm(
            data={
                "name": "А",
                "surname": "Б",
                "phone": "+79001234567",
                "about": "",
                "github_url": "",
            },
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_non_github_url_rejected(self):
        from .forms import EditProfileForm

        form = EditProfileForm(
            data={
                "name": "А",
                "surname": "Б",
                "phone": "",
                "about": "",
                "github_url": "https://gitlab.com/user",
            },
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_valid_github_url(self):
        from .forms import EditProfileForm

        form = EditProfileForm(
            data={
                "name": "А",
                "surname": "Б",
                "phone": "",
                "about": "",
                "github_url": "https://github.com/username",
            },
            instance=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)


class RegisterViewTest(BaseTestCase):
    def test_get_register_returns_200(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_post_register_creates_user_and_redirects(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Новый",
                "surname": "Пользователь",
                "email": "newuser@example.com",
                "password": "securepassword",
            },
        )
        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_post_register_invalid_shows_form(self):
        make_user(email="dup@example.com")
        response = self.client.post(
            reverse("users:register"),
            {
                "name": "Jane",
                "surname": "Smith",
                "email": "dup@example.com",
                "password": "pass",
            },
        )
        self.assertEqual(response.status_code, 200)


class LoginViewTest(BaseTestCase):
    def setUp(self):
        self.user = make_user(email="login@example.com", password="pass123")

    def test_get_login_returns_200(self):
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_valid_login_redirects(self):
        response = self.client.post(
            reverse("users:login"),
            {"email": "login@example.com", "password": "pass123"},
        )
        self.assertRedirects(response, reverse("projects:project_list"))

    def test_invalid_login_shows_error(self):
        response = self.client.post(
            reverse("users:login"),
            {"email": "login@example.com", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный")


class LogoutViewTest(BaseTestCase):
    def test_logout_redirects_to_project_list(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, reverse("projects:project_list"))


class UserDetailViewTest(BaseTestCase):
    def test_get_user_detail(self):
        user = make_user()
        response = self.client.get(reverse("users:user_detail", kwargs={"user_id": user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"], user)


class ParticipantsViewTest(BaseTestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name="Python")
        self.user = make_user()
        self.user.skills.add(self.skill)
        make_user(email="other@example.com")

    def test_list_all_users(self):
        response = self.client.get(reverse("users:participants"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("participants", response.context)
        self.assertIn("all_skills", response.context)
        self.assertEqual(len(response.context["participants"]), 2)

    def test_filter_by_skill(self):
        response = self.client.get(reverse("users:participants") + "?skill=Python")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["active_skill"], "Python")
        participants = list(response.context["participants"])
        self.assertIn(self.user, participants)
        self.assertEqual(len(participants), 1)

    def test_filter_no_match_returns_empty(self):
        response = self.client.get(
            reverse("users:participants") + "?skill=Несуществующий"
        )
        self.assertEqual(len(list(response.context["participants"])), 0)


class SkillAutocompleteTest(BaseTestCase):
    def setUp(self):
        Skill.objects.create(name="Python")
        Skill.objects.create(name="PostgreSQL")
        Skill.objects.create(name="React")

    def test_autocomplete_returns_matching(self):
        response = self.client.get(reverse("users:skill_autocomplete") + "?q=Py")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Python")

    def test_autocomplete_case_insensitive(self):
        response = self.client.get(reverse("users:skill_autocomplete") + "?q=py")
        data = response.json()
        self.assertEqual(len(data), 1)

    def test_autocomplete_empty_query_returns_all(self):
        response = self.client.get(reverse("users:skill_autocomplete") + "?q=")
        data = response.json()
        self.assertEqual(len(data), 3)


class UserSkillViewTest(BaseTestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def test_add_skill_by_name_creates_and_links(self):
        response = self.client.post(
            reverse("users:add_user_skill", kwargs={"user_id": self.user.pk}),
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("skill_id", data)
        self.assertTrue(data["created"])
        self.assertTrue(data["added"])
        self.assertTrue(self.user.skills.filter(name="Django").exists())

    def test_add_existing_skill_by_id(self):
        skill = Skill.objects.create(name="Flask")
        response = self.client.post(
            reverse("users:add_user_skill", kwargs={"user_id": self.user.pk}),
            data=json.dumps({"skill_id": skill.pk}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["created"])
        self.assertTrue(data["added"])

    def test_add_duplicate_skill_not_added_again(self):
        skill = Skill.objects.create(name="Vue")
        self.user.skills.add(skill)
        response = self.client.post(
            reverse("users:add_user_skill", kwargs={"user_id": self.user.pk}),
            data=json.dumps({"skill_id": skill.pk}),
            content_type="application/json",
        )
        data = response.json()
        self.assertFalse(data["added"])

    def test_add_skill_to_other_user_returns_403(self):
        other = make_user(email="other@example.com")
        response = self.client.post(
            reverse("users:add_user_skill", kwargs={"user_id": other.pk}),
            data=json.dumps({"name": "Go"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_remove_skill(self):
        skill = Skill.objects.create(name="Redis")
        self.user.skills.add(skill)
        response = self.client.post(
            reverse(
                "users:remove_user_skill",
                kwargs={"user_id": self.user.pk, "skill_id": skill.pk},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.skills.filter(pk=skill.pk).exists())
