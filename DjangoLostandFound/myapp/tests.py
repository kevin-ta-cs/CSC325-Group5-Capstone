from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import FoundItem, FoundItemInquiry
from .pages import REPORTS

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
		self.assertContains(response, f'href="{reverse("found_report")}">Report found</a>')
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
		self.assertContains(response, f'href="{reverse("found_report")}">Report found</a>')
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

	def test_dashboard_requires_login(self):
		response = self.client.get(reverse('user_dashboard'))

		self.assertRedirects(
			response,
			f'{reverse("login")}?next={reverse("user_dashboard")}',
		)

	def test_dashboard_shows_account_information_and_username_form(self):
		user = self.create_user()
		self.client.force_login(user)

		response = self.client.get(reverse('user_dashboard'))

		self.assertContains(response, 'User dashboard')
		self.assertContains(response, f'Welcome back, {user.username}.')
		self.assertContains(response, user.username)
		self.assertContains(response, user.email)
		self.assertContains(response, 'Member since')
		self.assertContains(response, 'name="username"')
		self.assertContains(response, 'name="csrfmiddlewaretoken"')
		self.assertContains(response, 'class="dashboard-stats"')
		self.assertContains(response, 'Your reports')
		self.assertContains(response, 'Smart matches')
		self.assertContains(response, 'Claims tracked')
		self.assertContains(response, 'Item status tracking')

	def test_dashboard_updates_the_authenticated_users_username(self):
		user = self.create_user()
		self.client.force_login(user)

		response = self.client.post(reverse('user_dashboard'), {'username': 'updated-user'})

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, reverse('user_dashboard'), fetch_redirect_response=False)
		user.refresh_from_db()
		self.assertEqual(user.username, 'updated-user')
		response = self.client.get(reverse('user_dashboard'))
		self.assertContains(response, 'Your username was updated.')

	def test_dashboard_rejects_an_existing_username(self):
		user = self.create_user()
		self.create_user(username='another-user')
		self.client.force_login(user)

		response = self.client.post(reverse('user_dashboard'), {'username': 'another-user'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'A user with that username already exists.')
		user.refresh_from_db()
		self.assertEqual(user.username, 'test-user')

	def test_homepage_displays_authenticated_username(self):
		user = self.create_user()
		self.client.force_login(user)

		response = self.client.get(reverse('home'))

		self.assertContains(
			response,
			f'Welcome, <span class="account-username">{user.username}</span>!',
			html=True,
		)
		self.assertContains(response, 'Log out')
		self.assertContains(response, '<details class="account-menu">', html=False)
		self.assertContains(response, '.account-menu:hover .account-menu-panel,')
		self.assertContains(response, '.account-menu:focus-within .account-menu-panel,')
		self.assertContains(response, '<span class="account-username">test-user</span>', html=True)
		self.assertContains(response, '.account-menu summary:hover .account-username,')
		self.assertContains(response, '.account-menu[open] .account-menu-panel { display: grid; }')
		self.assertContains(
			response,
			f'<a class="header-cta" href="{reverse("found_report")}">Report an item</a>',
			html=True,
		)
		self.assertContains(response, f'<form action="{reverse("logout")}" method="post">', html=False)
		self.assertContains(
			response,
			f'<a class="dashboard-action" href="{reverse("user_dashboard")}">Open your dashboard &nbsp;→</a>',
			html=True,
		)
		self.assertContains(response, f'href="{reverse("user_dashboard")}">Your dashboard</a>')

	def test_homepage_shows_login_and_report_signup_links_when_logged_out(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, f'href="{reverse("login")}"')
		self.assertContains(response, 'Log in')
		self.assertContains(response, f'href="{reverse("signup")}"')
		self.assertContains(response, 'Report an item')
		self.assertContains(response, f'href="{reverse("found_report")}">I found something</a>')
		self.assertContains(
			response,
			f'href="{reverse("login")}?next={reverse("user_dashboard")}">Open your dashboard',
		)
		self.assertContains(response, 'data-theme-toggle')

	def test_homepage_light_mode_action_buttons_have_contrast(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, 'body.theme-light .pill-button {')
		self.assertContains(response, 'border-color: var(--action-green); background: var(--action-green); color: #fff;')
		self.assertContains(response, 'body.theme-light .pill-button.outline {')
		self.assertContains(response, 'border-color: var(--action-green); background: #fff; color: var(--action-green);')
		self.assertContains(
			response,
			'.browse-link { display: flex; width: fit-content; margin: 28px auto 0; color: var(--white); font-weight: 750; text-decoration: none; }',
		)

	def test_homepage_dark_mode_surfaces_are_dark(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, 'body.theme-dark {')
		self.assertContains(response, '--paper: #111918;')
		self.assertContains(response, 'body.theme-dark .step { background: #192321; }')
		self.assertContains(response, 'body.theme-dark .filters { background: #192321; color: #eef5f3; }')
		self.assertContains(response, 'border-color: #465451; background-color: #111918; color: #eef5f3; color-scheme: dark;')
		self.assertContains(response, 'body.theme-dark .report-card { border-color: #34423f; background: #192321; color: #eef5f3; }')
		self.assertContains(response, 'body.theme-dark .dashboard-card.secondary {')
		self.assertContains(response, 'body.theme-dark .dashboard-card:not(.secondary) { background: #192321; }')

	def test_homepage_dashboard_cards_match_in_light_mode(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, 'body.theme-light .dashboard-card:not(.secondary) {')
		self.assertContains(response, 'border: 1px solid #cfe7e1; background: #eaf7f4; color: #163d38;')
		self.assertContains(response, 'body.theme-light .dashboard-card:not(.secondary) p { color: #596b67; }')
		self.assertContains(response, 'body.theme-light .dashboard-card:not(.secondary) a,')

	def test_report_filter_dropdowns_have_right_padding(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, '.filters select {')
		self.assertContains(response, 'appearance: none;')
		self.assertContains(response, 'background-position: calc(100% - 17px) 50%, calc(100% - 13px) 50%;')

	def test_match_card_matches_dashboard_surfaces_in_both_themes(self):
		response = self.client.get(reverse('home'))

		self.assertContains(response, 'background: #192321; color: #eef5f3;')
		self.assertContains(
			response,
			'body.theme-light .match-card {\n      border-color: #cfe7e1; background: #eaf7f4; color: #163d38;',
		)
		self.assertContains(response, 'body.theme-light .match-card p { color: #163d38; }')
		self.assertContains(response, 'body.theme-light .match-card .match-score { color: #596b67; }')

	def test_account_dark_mode_surfaces_are_dark(self):
		response = self.client.get(reverse('login'))

		self.assertContains(response, 'body.theme-dark .auth-panel {')
		self.assertContains(response, 'body.theme-dark .form-panel { background: #111918; }')
		self.assertContains(response, 'body.theme-dark .auth-tabs { background: #202b29; }')
		self.assertContains(response, 'body.theme-dark .auth-input {')


class FoundItemReportTests(TestCase):
	password = 'CampusFind!2026Strong'

	def create_user(self):
		return User.objects.create_user(
			username='found-item-reporter',
			email='found-item-reporter@example.com',
			password=self.password,
		)

	def create_found_item(self, reporter, item_name):
		return FoundItem.objects.create(
			reporter=reporter,
			item_name=item_name,
			description='A reported campus item.',
			category='Accessories',
			location='Campus Center',
			date_found=date(2026, 11, 10),
			time_found=time(14, 35),
		)

	def test_found_item_report_requires_login(self):
		response = self.client.get(reverse('found_report'))

		self.assertRedirects(
			response,
			f'{reverse("login")}?next={reverse("found_report")}',
		)

	def test_found_item_form_has_required_location_date_time_and_existing_categories(self):
		self.client.force_login(self.create_user())

		response = self.client.get(reverse('found_report'))

		self.assertContains(response, 'Report a found item')
		self.assertContains(response, 'class="report-layout"')
		self.assertContains(response, 'The right details create better matches.')
		self.assertContains(response, 'class="primary-nav"')
		self.assertContains(response, '<select name="location"', html=False)
		self.assertContains(response, 'name="date_found"')
		self.assertContains(response, 'type="date"')
		self.assertContains(response, 'name="time_found"')
		self.assertContains(response, 'type="time"')
		self.assertContains(response, '>Publish report</button>', html=False)
		for category in ('Accessories', 'Bags &amp; Luggage', 'Electronics', 'Keys'):
			with self.subTest(category=category):
				self.assertContains(response, category)
		for building in (
			'Amphitheater',
			'Aviation Center',
			'Broad Hollow Bioscience Park One',
			'Broad Hollow Bioscience Park Two',
			'Campus Center',
			'Campus Commons',
			'Conference Center',
			'Gleeson Hall',
			'Greenley Library',
			'Hale Hall',
			'Hooper Hall',
			'Horton Hall',
			'Knapp Hall',
			'Laffin Hall',
			'Lupton Hall',
			'Memorial Hall',
			'Nold Athletic Complex',
			'Quintyne Hall',
			'Roosevelt Hall',
			'School of Business',
			'Sinclair Hall',
			'Thompson Hall',
			'Ward Hall',
			'Whitman Hall',
		):
			with self.subTest(building=building):
				self.assertContains(response, building)

	def test_found_item_report_rejects_missing_required_details(self):
		self.client.force_login(self.create_user())

		response = self.client.post(reverse('found_report'), {'item_name': 'Umbrella'})

		self.assertEqual(response.status_code, 200)
		for field_name in ('category', 'location', 'date_found', 'time_found'):
			with self.subTest(field=field_name):
				self.assertContains(response, f'id="{field_name}-errors"')
		self.assertFalse(FoundItem.objects.exists())

	def test_found_item_report_rejects_categories_outside_the_dropdown(self):
		self.client.force_login(self.create_user())

		response = self.client.post(reverse('found_report'), {
			'item_name': 'Umbrella',
			'category': 'Furniture',
			'location': 'Campus Center',
			'date_found': '2026-11-10',
			'time_found': '14:35',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Select a valid choice')
		self.assertFalse(FoundItem.objects.exists())

	def test_found_item_report_rejects_buildings_outside_the_dropdown(self):
		self.client.force_login(self.create_user())

		response = self.client.post(reverse('found_report'), {
			'item_name': 'Umbrella',
			'category': 'Accessories',
			'location': 'Off Campus',
			'date_found': '2026-11-10',
			'time_found': '14:35',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Select a valid choice')
		self.assertFalse(FoundItem.objects.exists())

	def test_found_item_report_saves_and_appears_in_catalog(self):
		user = self.create_user()
		self.client.force_login(user)

		response = self.client.post(reverse('found_report'), {
			'item_name': 'Blue water bottle',
			'description': 'Found beside the north entrance.',
			'category': 'Accessories',
			'location': 'Campus Center',
			'date_found': '2026-11-10',
			'time_found': '14:35',
		})

		self.assertRedirects(
			response,
			reverse('found_report'),
			fetch_redirect_response=False,
		)
		item = FoundItem.objects.get()
		self.assertEqual(item.reporter, user)
		self.assertEqual(item.category, 'Accessories')
		self.assertEqual(item.location, 'Campus Center')
		self.assertEqual(item.date_found.isoformat(), '2026-11-10')
		self.assertEqual(item.time_found.strftime('%H:%M'), '14:35')

		response = self.client.get(reverse('found_report'))
		self.assertContains(response, 'Your found item was reported.')
		response = self.client.get(reverse('home'))
		self.assertContains(response, 'Blue water bottle')
		self.assertContains(response, 'Campus Center')
		self.assertContains(response, '2:35 PM')

	def test_catalog_found_report_opens_its_item_details(self):
		user = self.create_user()
		item = self.create_found_item(user, 'Silver watch')

		response = self.client.get(reverse('home'))

		self.assertContains(
			response,
			f'href="{reverse("found_item_detail", args=(item.pk,))}"',
			html=False,
		)
		self.assertContains(response, 'View details')

	def test_every_catalog_item_has_a_public_details_page(self):
		response = self.client.get(reverse('home'))

		for index, report in enumerate(REPORTS):
			with self.subTest(item=report['title']):
				detail_url = reverse(
					'found_item_detail',
					args=(f'sample-{index}',),
				)
				self.assertContains(response, f'href="{detail_url}"', html=False)
				detail_response = self.client.get(detail_url)
				self.assertContains(detail_response, report['title'])
				self.assertContains(
					detail_response,
					report['category'].replace('&', '&amp;'),
				)
				self.assertContains(detail_response, report['building'])
				self.assertContains(detail_response, 'item-detail-card')
				self.assertContains(detail_response, 'class="primary-nav"')
				self.assertContains(detail_response, 'site-footer')
				self.assertContains(
					detail_response,
					'This sample listing has no reporter account.',
				)

	def test_invalid_item_detail_identifiers_return_not_found(self):
		self.assertEqual(
			self.client.get(reverse('found_item_detail', args=('not-an-id',))).status_code,
			404,
		)
		self.assertEqual(
			self.client.get(reverse('found_item_detail', args=('sample-99',))).status_code,
			404,
		)

	def test_found_item_detail_shows_information_and_private_request_prompt(self):
		reporter = self.create_user()
		requester = User.objects.create_user(
			username='item-owner',
			email='item-owner@example.com',
			password=self.password,
		)
		item = self.create_found_item(reporter, 'Silver watch')
		self.client.force_login(requester)

		response = self.client.get(reverse('found_item_detail', args=(item.pk,)))

		self.assertContains(response, 'Silver watch')
		self.assertContains(response, 'A reported campus item.')
		self.assertContains(response, 'Campus Center')
		self.assertContains(response, 'Request information privately')
		self.assertContains(response, 'name="message"')
		self.assertContains(response, 'Send private request')
		self.assertNotContains(response, reporter.email)

		self.client.force_login(reporter)
		reporter_response = self.client.get(reverse('found_item_detail', args=(item.pk,)))
		self.assertContains(reporter_response, 'Silver watch')
		self.assertContains(
			reporter_response,
			'You reported this item, so you cannot send a request to yourself.',
		)

	def test_private_information_request_is_saved_and_only_shown_to_reporter(self):
		reporter = self.create_user()
		requester = User.objects.create_user(
			username='item-owner',
			email='item-owner@example.com',
			password=self.password,
		)
		item = self.create_found_item(reporter, 'Silver watch')
		detail_url = reverse('found_item_detail', args=(item.pk,))
		request_url = reverse('request_found_item_information', args=(item.pk,))
		self.client.force_login(requester)

		response = self.client.post(
			request_url,
			{'message': 'Could you tell me where you found this watch?'},
		)

		self.assertRedirects(
			response,
			detail_url,
			fetch_redirect_response=False,
		)
		inquiry = FoundItemInquiry.objects.get()
		self.assertEqual(inquiry.item, item)
		self.assertEqual(inquiry.requester, requester)
		self.assertEqual(inquiry.message, 'Could you tell me where you found this watch?')
		self.assertContains(self.client.get(detail_url), 'Your private request was sent')

		self.client.force_login(reporter)
		reporter_dashboard = self.client.get(reverse('user_dashboard'))
		self.assertContains(reporter_dashboard, 'Private information requests')
		self.assertContains(reporter_dashboard, 'Silver watch')
		self.assertContains(reporter_dashboard, requester.username)
		self.assertContains(reporter_dashboard, inquiry.message)

		self.client.force_login(requester)
		requester_dashboard = self.client.get(reverse('user_dashboard'))
		self.assertNotContains(requester_dashboard, inquiry.message)

	def test_reporter_cannot_request_information_about_their_own_item(self):
		reporter = self.create_user()
		item = self.create_found_item(reporter, 'My own report')
		self.client.force_login(reporter)

		response = self.client.post(
			reverse('request_found_item_information', args=(item.pk,)),
			{'message': 'Tell me more.'},
		)

		self.assertRedirects(
			response,
			reverse('found_item_detail', args=(item.pk,)),
			fetch_redirect_response=False,
		)
		self.assertFalse(FoundItemInquiry.objects.exists())

	def test_private_request_requires_login_and_a_posted_message(self):
		reporter = self.create_user()
		item = self.create_found_item(reporter, 'Silver watch')
		request_url = reverse('request_found_item_information', args=(item.pk,))

		response = self.client.post(request_url, {'message': 'Tell me more.'})

		self.assertRedirects(
			response,
			f'{reverse("login")}?next={request_url}',
		)
		self.client.force_login(User.objects.create_user(
			username='item-owner',
			email='item-owner@example.com',
			password=self.password,
		))
		self.assertEqual(self.client.get(request_url).status_code, 405)
		response = self.client.post(request_url, {'message': ''})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'id="message-errors"')
		self.assertFalse(FoundItemInquiry.objects.exists())

	def test_dashboard_lists_only_reports_owned_by_the_signed_in_user(self):
		user = self.create_user()
		other_user = User.objects.create_user(
			username='another-reporter',
			email='another-reporter@example.com',
			password=self.password,
		)
		owned_item = self.create_found_item(user, 'My blue umbrella')
		other_item = self.create_found_item(other_user, "Someone else's keys")
		self.client.force_login(user)

		response = self.client.get(reverse('user_dashboard'))

		self.assertContains(response, 'Your reports')
		self.assertContains(response, 'My blue umbrella')
		self.assertNotContains(response, "Someone else's keys")
		self.assertContains(
			response,
			f'href="{reverse("edit_found_item", args=(owned_item.pk,))}">Edit</a>',
		)
		self.assertContains(
			response,
			f'action="{reverse("delete_found_item", args=(owned_item.pk,))}"',
			html=False,
		)
		self.assertNotContains(
			response,
			reverse('edit_found_item', args=(other_item.pk,)),
			html=False,
		)

	def test_user_can_edit_their_own_found_item_report(self):
		user = self.create_user()
		item = self.create_found_item(user, 'Old item name')
		self.client.force_login(user)
		edit_url = reverse('edit_found_item', args=(item.pk,))

		response = self.client.get(edit_url)

		self.assertContains(response, 'Edit found item')
		self.assertContains(response, 'value="Old item name"')
		response = self.client.post(edit_url, {
			'item_name': 'Updated item name',
			'description': 'Updated description.',
			'category': 'Keys',
			'location': 'Greenley Library',
			'date_found': '2026-11-11',
			'time_found': '15:45',
		})

		self.assertRedirects(
			response,
			reverse('user_dashboard'),
			fetch_redirect_response=False,
		)
		item.refresh_from_db()
		self.assertEqual(item.reporter, user)
		self.assertEqual(item.item_name, 'Updated item name')
		self.assertEqual(item.description, 'Updated description.')
		self.assertEqual(item.category, 'Keys')
		self.assertEqual(item.location, 'Greenley Library')

	def test_users_cannot_edit_or_delete_another_users_report(self):
		user = self.create_user()
		other_user = User.objects.create_user(
			username='another-reporter',
			email='another-reporter@example.com',
			password=self.password,
		)
		other_item = self.create_found_item(other_user, 'Private report')
		self.client.force_login(user)

		edit_response = self.client.post(
			reverse('edit_found_item', args=(other_item.pk,)),
			{
				'item_name': 'Changed by another user',
				'category': 'Keys',
				'location': 'Greenley Library',
				'date_found': '2026-11-11',
				'time_found': '15:45',
			},
		)
		delete_response = self.client.post(
			reverse('delete_found_item', args=(other_item.pk,)),
		)

		self.assertEqual(edit_response.status_code, 404)
		self.assertEqual(delete_response.status_code, 404)
		other_item.refresh_from_db()
		self.assertEqual(other_item.reporter, other_user)
		self.assertEqual(other_item.item_name, 'Private report')

	def test_user_can_delete_only_with_post(self):
		user = self.create_user()
		item = self.create_found_item(user, 'Report to delete')
		self.client.force_login(user)
		delete_url = reverse('delete_found_item', args=(item.pk,))

		get_response = self.client.get(delete_url)

		self.assertEqual(get_response.status_code, 405)
		self.assertTrue(FoundItem.objects.filter(pk=item.pk).exists())
		response = self.client.post(delete_url)

		self.assertRedirects(
			response,
			reverse('user_dashboard'),
			fetch_redirect_response=False,
		)
		self.assertFalse(FoundItem.objects.filter(pk=item.pk).exists())
		self.assertContains(self.client.get(reverse('user_dashboard')), 'Your found item report was deleted.')
