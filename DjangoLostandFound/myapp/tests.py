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

	def test_signup_page_uses_findit_account_layout(self):
		response = self.client.get(reverse('signup'))

		self.assertContains(response, 'Join FindIt')
		self.assertContains(response, 'Create your member account')
		self.assertContains(response, 'Username')
		self.assertContains(response, 'Campus email')
		self.assertContains(response, 'Confirm password')
		self.assertContains(response, 'name="csrfmiddlewaretoken"')
		self.assertContains(response, 'aria-current="page">Create account</a>')
		self.assertContains(response, 'data-theme-toggle')
		self.assertContains(response, 'localStorage.setItem(storageKey, theme)')
		self.assertContains(
			response,
			'<button class="header-cta" type="button">Report an item</button>',
			html=True,
		)
		self.assertContains(response, 'body.theme-light .submit-button { background: #003e3a; }')

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
				self.assertContains(response, 'errorlist')
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
		self.assertContains(response, 'class="error-summary" role="alert"')
		self.assertContains(response, 'Access your dashboard')

	def test_login_page_has_findit_account_layout_and_csrf(self):
		response = self.client.get(reverse('login'))

		self.assertContains(response, 'Your campus recovery hub')
		self.assertContains(response, 'Access your dashboard')
		self.assertContains(response, 'Campus username')
		self.assertContains(response, 'Log in securely')
		self.assertContains(response, 'name="csrfmiddlewaretoken"')
		self.assertContains(response, 'data-theme-toggle')
		self.assertContains(response, 'localStorage.setItem(storageKey, theme)')
		self.assertContains(response, '--action-green: #003e3a;')
		self.assertContains(
			response,
			'<button class="header-cta" type="button">Report an item</button>',
			html=True,
		)

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
		self.assertContains(
			response,
			'<button class="header-cta" type="button">Report an item</button>',
			html=True,
		)
		self.assertContains(response, f'<form action="{reverse("logout")}" method="post">', html=False)

	def test_homepage_shows_login_and_report_signup_links_when_logged_out(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, f'href="{reverse("login")}"')
		self.assertContains(response, 'Log in')
		self.assertContains(response, f'href="{reverse("signup")}"')
		self.assertContains(response, 'Report an item')
		self.assertContains(response, 'data-theme-toggle')
