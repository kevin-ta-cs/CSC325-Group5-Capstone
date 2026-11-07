from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import LostItem


class AuthenticationTests(TestCase):
    def test_registration_saves_user_and_logs_them_in(self):
        response = self.client.post(
            "/register/",
            {
                "username": "campus_user",
                "password1": "StrongPass!9274",
                "password2": "StrongPass!9274",
            },
        )

        self.assertRedirects(response, "/")
        user = get_user_model().objects.get(username="campus_user")
        self.assertTrue(user.check_password("StrongPass!9274"))
        self.assertNotEqual(user.password, "StrongPass!9274")
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_invalid_password_does_not_authenticate(self):
        get_user_model().objects.create_user(
            username="campus_user",
            password="StrongPass!9274",
        )

        response = self.client.post(
            "/login/",
            {"username": "campus_user", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_and_logout(self):
        get_user_model().objects.create_user(
            username="campus_user",
            password="StrongPass!9274",
        )

        response = self.client.post(
            "/login/",
            {"username": "campus_user", "password": "StrongPass!9274"},
        )
        self.assertRedirects(response, "/")
        self.assertIn("_auth_user_id", self.client.session)

        response = self.client.post("/logout/")
        self.assertRedirects(response, "/")
        self.assertNotIn("_auth_user_id", self.client.session)


class LostItemReportingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="reporter",
            password="StrongPass!9274",
        )
        self.client.force_login(self.user)

    def report_data(self, date_lost=None):
        return {
            "item_name": "Blue backpack",
            "description": "A blue backpack with a notebook inside.",
            "category": "Bags",
            "location_lost": "Library",
            "date_lost": date_lost or (timezone.localdate() - timedelta(days=1)).isoformat(),
        }

    def test_authenticated_user_can_access_report_form(self):
        response = self.client.get(reverse("report_lost_item"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report a lost item")

    def test_valid_report_is_saved_for_logged_in_user(self):
        response = self.client.post(
            reverse("report_lost_item"),
            self.report_data(),
            follow=True,
        )

        report = LostItem.objects.get()
        self.assertEqual(report.submitted_by, self.user)
        self.assertContains(response, "Your lost-item report was submitted.")

    def test_invalid_report_displays_validation_error(self):
        future_date = (timezone.localdate() + timedelta(days=1)).isoformat()

        response = self.client.post(
            reverse("report_lost_item"),
            self.report_data(date_lost=future_date),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The lost date cannot be in the future.")
        self.assertEqual(LostItem.objects.count(), 0)

    def test_required_fields_are_validated(self):
        response = self.client.post(reverse("report_lost_item"), {})

        self.assertEqual(response.status_code, 200)
        for field in ("item_name", "description", "category", "location_lost", "date_lost"):
            self.assertIn(field, response.context["form"].errors)
        self.assertEqual(LostItem.objects.count(), 0)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse("report_lost_item"))

        expected_url = f"{reverse('login')}?next={reverse('report_lost_item')}"
        self.assertRedirects(response, expected_url)

    def test_anonymous_user_cannot_submit_report(self):
        self.client.logout()

        response = self.client.post(
            reverse("report_lost_item"),
            self.report_data(),
        )

        expected_url = f"{reverse('login')}?next={reverse('report_lost_item')}"
        self.assertRedirects(response, expected_url)
        self.assertEqual(LostItem.objects.count(), 0)
