from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthenticationTests(TestCase):
	password = 'CampusFind!2026Strong'

	def create_user(self, username='test-user'):
		return User.objects.create_user(
			username=username,
			email=f'{username}@example.com',
			password=self.password,
		)

	def test_signup_creates_user_with_valid_information(self):
		response = self.client.post(reverse('signup'), {
			'username': 'new-user',
			'email': 'new-user@example.com',
			'password1': self.password,
			'password2': self.password,
		})

		self.assertRedirects(response, reverse('login'))
		user = User.objects.get(username='new-user')
		self.assertEqual(user.email, 'new-user@example.com')
		self.assertTrue(user.check_password(self.password))
		self.assertFalse(user.is_staff)
		self.assertFalse(user.is_superuser)

	def test_signup_rejects_invalid_or_mismatched_passwords(self):
		invalid_submissions = (
			('mismatched-user', self.password, 'Different!2026Password'),
			('weak-password-user', '123', '123'),
		)

		for username, password1, password2 in invalid_submissions:
			with self.subTest(username=username):
				response = self.client.post(reverse('signup'), {
					'username': username,
					'email': f'{username}@example.com',
					'password1': password1,
					'password2': password2,
				})

				self.assertEqual(response.status_code, 200)
				self.assertTrue(response.context['form'].errors)
				self.assertFalse(User.objects.filter(username=username).exists())

	def test_login_accepts_valid_credentials(self):
		user = self.create_user()

		response = self.client.post(reverse('login'), {
			'username': user.username,
			'password': self.password,
		})

		self.assertRedirects(response, reverse('home'))
		self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

	def test_login_rejects_invalid_credentials(self):
		user = self.create_user()

		response = self.client.post(reverse('login'), {
			'username': user.username,
			'password': 'incorrect-password',
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.wsgi_request.user.is_authenticated)
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_logout_ends_authenticated_session(self):
		user = self.create_user()
		self.client.force_login(user)

		response = self.client.post(reverse('logout'))

		self.assertRedirects(response, reverse('home'))
		self.assertNotIn('_auth_user_id', self.client.session)

	def test_homepage_displays_authenticated_username(self):
		user = self.create_user()
		self.client.force_login(user)

		response = self.client.get(reverse('home'))

		self.assertContains(response, f'Welcome, {user.username}!')
		self.assertContains(response, 'Logout')

	def test_homepage_shows_login_and_signup_links_when_logged_out(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, f'href="{reverse("login")}"')
		self.assertContains(response, 'Login')
		self.assertContains(response, f'href="{reverse("signup")}"')
		self.assertContains(response, 'Sign Up')
