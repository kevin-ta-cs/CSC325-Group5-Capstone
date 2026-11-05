from django.contrib.auth import get_user_model
from django.test import TestCase


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
