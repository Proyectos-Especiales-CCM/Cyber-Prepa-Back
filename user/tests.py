from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import AccessToken
import json


class UserTests(TestCase):
    def setUp(self):
        # Initialize client and sample data

        self.client = Client()

        self.user = get_user_model().objects.create_user(
            email="A01656583@tec.mx",
            password="Mypass123!",
        )

        self.admin_user = get_user_model().objects.create_superuser(
            email="diegoDev@tec.mx",
            password="MyStrongPass123!!!",
        )

    def test_user_created(self):
        # Test: Check if users were correctly created
        admin_group = Group.objects.get(name="admin")
        self.assertEqual(self.user.email, "A01656583@tec.mx")
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.check_password("Mypass123!"))
        self.assertFalse(admin_group.user_set.filter(pk=self.user.pk).exists())

        self.assertEqual(self.admin_user.email, "diegoDev@tec.mx")
        self.assertTrue(self.admin_user.is_staff)
        self.assertTrue(self.admin_user.is_active)
        self.assertTrue(self.admin_user.is_superuser)
        self.assertTrue(self.admin_user.check_password("MyStrongPass123!!!"))
        self.assertTrue(admin_group.user_set.filter(pk=self.admin_user.pk).exists())

    def test_user_tokens(self):
        # Test: Get the access and refresh tokens for a user
        response = self.client.post(
            "/token/", {"email": "A01656583@tec.mx", "password": "Mypass123!"}
        )
        refresh_token = response.json()["refresh"]
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/token/refresh/", {"refresh": refresh_token})
        self.assertTrue("access" in response.json())
        self.assertEqual(response.status_code, 200)

    def test_users_api_read_list_success(self):
        # Test: List users via an admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/users/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_users_api_read_list_fail(self):
        # Test: List users via a non-authenticated user
        response = self.client.get(
            "/users/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: List users via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/users/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_users_api_create_success(self):
        access_token = AccessToken.for_user(self.admin_user)

        # Test: Create an admin user
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "email": "A01656580@tec.mx",
                    "password": "Mypass123!",
                    "is_admin": True,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["email"], "A01656580@tec.mx")
        self.assertTrue(
            Group.objects.get(name="admin").user_set.filter(pk=response["id"]).exists()
        )

        # Test: Create a non-admin user with is_admin
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "email": "A01656581@tec.mx",
                    "password": "Mypass123!",
                    "is_admin": False,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["email"], "A01656581@tec.mx")
        self.assertFalse(
            Group.objects.get(name="admin").user_set.filter(pk=response["id"]).exists()
        )

        # Test: Create a non-admin user without is_admin
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "email": "A01656582@tec.mx",
                    "password": "Mypass123!",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response["email"], "A01656582@tec.mx")
        self.assertFalse(
            Group.objects.get(name="admin").user_set.filter(pk=response["id"]).exists()
        )

        self.assertEqual(get_user_model().objects.count(), 5)

    def test_users_api_create_fail(self):
        # Test: Create a user without authentication
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "password": "Mypass123!",
                    "is_admin": True,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        access_token = AccessToken.for_user(self.admin_user)

        # Test: Create a user without email
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "password": "Mypass123!",
                    "is_admin": True,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Create a user without password
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "email": "A01656580@tec.mx",
                    "is_admin": True,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Create a user with invalid passwords
        # Valid passwords should be at least 8 characters long, contain at least 1 digit, 2 letters, 1 uppercase letter, 1 lowercase letter, and 1 special character
        invalid_passwords = [
            "",
            "123" "!" "password",
            "password123",
            "Password",
            "Password123",
            "password!",
            "password123!",
            "Password!",
        ]
        for i, password in enumerate(invalid_passwords):
            response = self.client.post(
                "/users/",
                {
                    "password": password,
                    "email": f"A0165659{i+10}@tec.mx",
                },
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {access_token}",
            )
            self.assertEqual(response.status_code, 400)

        # Test: Create a user with invalid emails
        invalid_emails = [
            "A01656610@gmail.com",
            "test",
            "test@",
            "@gmail.com",
            "@tec.mx",
        ]
        for email in invalid_emails:
            response = self.client.post(
                "/users/",
                json.dumps(
                    {
                        "password": "Mypass123!",
                        "email": email,
                    }
                ),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {access_token}",
            )
            self.assertEqual(response.status_code, 400)

        # Test: Create a user with an already existing email
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "password": "Mypass123!",
                    "email": "A01656583@tec.mx",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Create a user via a non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/users/",
            json.dumps(
                {
                    "password": "Mypass123!",
                    "email": "A01656700@tec.mx",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        self.assertEqual(get_user_model().objects.count(), 2)

    def test_users_api_read_detail_success(self):
        # Test: Read another user's details as admin
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            f"/users/{self.user.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["email"], self.user.email)
        self.assertEqual(response["id"], self.user.id)
        self.assertFalse(response["is_admin"])

        # Test: Read own details as non-admin
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            f"/users/{self.user.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["email"], self.user.email)
        self.assertEqual(response["id"], self.user.id)
        self.assertFalse(response["is_admin"])

    def test_users_api_read_detail_fail(self):
        # Test: Read any user's details as non-authenticated
        response = self.client.get(
            f"/users/{self.user.id}/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Read non-existing user's details as admin
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            f"/users/999/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)

        # Test: Read another user's details as non-admin
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            f"/users/{self.admin_user.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_users_api_update_success(self):
        # Test: Update own data
        access_token = AccessToken.for_user(self.user)
        response = self.client.patch(
            f"/users/{self.user.pk}/",
            json.dumps(
                {
                    "password": "MyNewpass123*",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password("MyNewpass123*"))
        access_token = AccessToken.for_user(self.admin_user)

        # Test: Update a user's complete data
        response = self.client.put(
            f"/users/{self.user.pk}/",
            json.dumps(
                {
                    "email": "A01656593@tec.mx",
                    "password": "MyOtherpass123*",
                    "is_admin": True,
                    "is_active": False,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(pk=self.user.pk)
        self.assertEqual(user.email, "A01656593@tec.mx")
        self.assertTrue(user.check_password("MyOtherpass123*"))
        self.assertTrue(
            Group.objects.get(name="admin").user_set.filter(pk=user.pk).exists()
        )
        self.assertFalse(user.is_active)

    def test_users_api_update_fail(self):
        # Test: Update a user's data without authentication
        response = self.client.put(
            f"/users/{self.user.pk}/",
            json.dumps(
                {
                    "email": "A01656593@tec.mx",
                    "password": "MyOtherpass123*",
                    "is_admin": True,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Test: Update a non-existing user's data
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.patch(
            f"/users/999/",
            json.dumps({"password": "Mypass123*"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 404)

        # Test: Update a user's data as non-admin
        access_token = AccessToken.for_user(self.user)
        response = self.client.patch(
            f"/users/{self.admin_user.pk}/",
            json.dumps({"password": "Mypass123*"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Update own user's data with invalid passwords
        response = self.client.patch(
            f"/users/{self.user.pk}/",
            json.dumps({"password": "pass"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Update own user's data with invalid emails
        response = self.client.patch(
            f"/users/{self.user.pk}/",
            json.dumps({"email": "test@gmail.com"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Update own user's data with an already existing email
        response = self.client.patch(
            f"/users/{self.user.pk}/",
            json.dumps({"email": "diegoDev@tec.mx"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 400)

        # Test: Update own user's is_admin data as non-admin
        response = self.client.patch(
            f"/users/{self.user.pk}/",
            json.dumps({"is_admin": True}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Update own user's is_active data as non-admin
        response = self.client.patch(
            f"/users/{self.user.pk}/",
            json.dumps({"is_active": False}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Update own user's is_staff data as non-admin
        response = self.client.patch(
            f"/users/{self.user.pk}/",
            json.dumps({"is_staff": True}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

    def test_users_api_me_success(self):
        # Test that users can read their own user details
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/users/me/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["id"], self.user.id)
        self.assertEqual(response["email"], self.user.email)
        self.assertFalse(response["is_admin"])
        self.assertEqual(response["theme"], "light")
        self.assertTrue(response["is_active"])

    def test_users_api_me_fail(self):
        # Test that users cannot read their own user details without authentication
        response = self.client.get("/users/me/")
        self.assertEqual(response.status_code, 401)
