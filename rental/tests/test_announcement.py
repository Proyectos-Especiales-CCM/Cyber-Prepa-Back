import json
from datetime import timedelta
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from rental.models import Announcement


class AnnouncementTests(TestCase):
    """
    An announcement is a message that is displayed to all users of the platform
        Things to consider:
    - Announcements are created by the admin users
    - Announcements can be accessed by any visitor, like unauthenticated users
    - Announcements require a title, a
    """

    def setUp(self):
        # Initialize client and sample data
        """
        The created objects are:
        3 Users: 1 admin, 1 inactive admin, 1 non-admin
        2 Announcements: 1 visible, 1 not visible
        """

        self.client = Client()

        self.user = get_user_model().objects.create_user(
            email="A01656583@tec.mx",
            password="Mypass123!",
        )

        self.admin_user = get_user_model().objects.create_superuser(
            email="diegoDev@tec.mx",
            password="MyStrongPass123!!!",
        )

        self.inactive_admin_user = get_user_model().objects.create_superuser(
            email="leo@tec.mx", password="MyStrongPass123!!!", is_active=False
        )

        self.visible_announcement = Announcement.objects.create(
            title="Visible Announcement",
            content="This is a visible announcement",
            start_at=timezone.now() - timedelta(minutes=1),
            end_at=timezone.now() + timedelta(minutes=1),
        )

        self.not_visible_announcement = Announcement.objects.create(
            title="Not Visible Announcement",
            content="This is a not visible announcement",
            start_at=timezone.now() - timedelta(minutes=2),
            end_at=timezone.now() - timedelta(minutes=1),
        )

    def test_announcement_api_read_success(self):
        # Function to validate the read of announcements
        def validate_announcement_read(response, announcement, count):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), count)
            if count == 1:
                self.assertEqual(response.json()[0]["title"], announcement.title)
                self.assertEqual(response.json()[0]["content"], announcement.content)

        # Test: Read via unauthenticated user all announcements
        response = self.client.get("/rental/announcements/")
        validate_announcement_read(response, self.visible_announcement, 2)

        ### From now it will be tested to verify the only-active parameter
        # Test: Read via unauthenticated user
        response = self.client.get("/rental/announcements/?only-active=True")
        validate_announcement_read(response, self.visible_announcement, 1)

        # Test: Read via admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/rental/announcements/?only-active=True",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        validate_announcement_read(response, self.visible_announcement, 1)

        # Test: Read via non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/rental/announcements/?only-active=True",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        validate_announcement_read(response, self.visible_announcement, 1)

    def test_announcement_api_read_failure(self):
        # Test: Read via inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            "/rental/announcements/?only-active=True",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_announcement_api_create_success(self):
        # Test: Create via admin user
        access_token = AccessToken.for_user(self.admin_user)
        start_at = timezone.now().replace(tzinfo=None, microsecond=0) - timedelta(
            minutes=1
        )
        end_at = timezone.now().replace(tzinfo=None, microsecond=0) + timedelta(
            minutes=1
        )
        response = self.client.post(
            "/rental/announcements/",
            json.dumps(
                {
                    "title": "Updated Announcement",
                    "content": "This is an updated announcement",
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Announcement.objects.count(), 3)

    def test_announcement_api_create_failure(self):
        # Test: Create via unauthenticated user
        response = self.client.post(
            "/rental/announcements/",
            {
                "title": "New Announcement",
                "content": "This is a new announcement",
                "start_at": timezone.now() - timedelta(minutes=1),
                "end_at": timezone.now() + timedelta(minutes=1),
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Announcement.objects.count(), 2)

        # Test: Create via non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/announcements/",
            {
                "title": "New Announcement",
                "content": "This is a new announcement",
                "start_at": timezone.now() - timedelta(minutes=1),
                "end_at": timezone.now() + timedelta(minutes=1),
            },
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Announcement.objects.count(), 2)

    def test_announcement_api_update_success(self):
        # Test: Update via admin user
        access_token = AccessToken.for_user(self.admin_user)
        start_at = timezone.now().replace(tzinfo=None, microsecond=0) - timedelta(
            minutes=1
        )
        end_at = timezone.now().replace(tzinfo=None, microsecond=0) + timedelta(
            minutes=1
        )
        response = self.client.put(
            f"/rental/announcements/{self.visible_announcement.pk}/",
            json.dumps(
                {
                    "title": "Updated Announcement",
                    "content": "This is an updated announcement",
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.visible_announcement.refresh_from_db()
        self.assertEqual(self.visible_announcement.title, "Updated Announcement")
        self.assertEqual(
            self.visible_announcement.content, "This is an updated announcement"
        )

    def test_announcement_api_update_failure(self):
        # Test: Update via unauthenticated user
        start_at = timezone.now().replace(tzinfo=None, microsecond=0) - timedelta(
            minutes=1
        )
        end_at = timezone.now().replace(tzinfo=None, microsecond=0) + timedelta(
            minutes=1
        )
        response = self.client.put(
            f"/rental/announcements/{self.visible_announcement.pk}/",
            json.dumps(
                {
                    "title": "Updated Announcement",
                    "content": "This is an updated announcement",
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Update via inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.patch(
            f"/rental/announcements/{self.visible_announcement.pk}/",
            {
                "title": "Updated Announcement",
                "content": "This is an updated announcement",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        # Test: Update via non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.patch(
            f"/rental/announcements/{self.visible_announcement.pk}/",
            {
                "title": "Updated Announcement",
                "content": "This is an updated announcement",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_announcement_api_delete_success(self):
        # Test: Delete via admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/announcements/{self.visible_announcement.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Announcement.objects.count(), 1)

    def test_announcement_api_delete_failure(self):
        # Test: Delete via unauthenticated user
        response = self.client.delete(f"/rental/announcements/{self.visible_announcement.pk}/")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Announcement.objects.count(), 2)

        # Test: Delete via inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.delete(
            f"/rental/announcements/{self.visible_announcement.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Delete via non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.delete(
            f"/rental/announcements/{self.visible_announcement.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)
