import os
import io
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from ..models import Image
from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


class ImageTests(TestCase):
    """Testear el modelo de imagenes"""

    def createTempImage(self):
        """Create a temporary file"""
        # Create a black image
        width, height = 100, 100
        color = (0, 0, 0)  # Black color in RGB
        image = PILImage.new("RGB", (width, height), color)

        # Save the image to a BytesIO object
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)

        # Create a SimpleUploadedFile from the BytesIO object
        temp_image = SimpleUploadedFile("temp_test.png", image_io.read(), content_type="image/png")
        return temp_image

    def createImage(self):
        """Crear una imagen"""
        name = f"test{Image.objects.count() + 1}.png"
        image_path = os.path.join(settings.MEDIA_ROOT, "images/", name)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        PILImage.new("RGB", (100, 100), color="red").save(image_path)
        return Image.objects.create(image=image_path)

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

        self.inactive_admin_user = get_user_model().objects.create_superuser(
            email="leo@tec.mx", password="MyStrongPass123!!!", is_active=False
        )

        # Create a sample image
        self.image = self.createImage()

        self.user_count = get_user_model().objects.count()
        self.image_count = Image.objects.count()

    def test_images_api_read_list_success(self):
        # Test: List all images with an authenticated admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            "/rental/images/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), self.image_count)

    def test_images_api_read_list_fail(self):
        # Test: List all images without an authenticated user
        response = self.client.get("/rental/images/")
        self.assertEqual(response.status_code, 401)

        # Test: List all images with an non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            "/rental/images/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: List all images with an inactive authenticated user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            "/rental/images/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_images_api_read_detail_success(self):
        # Test: Read an image with an authenticated admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.get(
            f"/rental/images/{self.image.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["id"], self.image.pk)
        self.assertRegex(response["image"], "mocked_public_url")

    def test_images_api_read_detail_fail(self):
        # Test: Read an image without an authenticated user
        response = self.client.get(f"/rental/images/{self.image.pk}/")
        self.assertEqual(response.status_code, 401)

        # Test: Read an image with an non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.get(
            f"/rental/images/{self.image.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Read an image with an inactive authenticated user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.get(
            f"/rental/images/{self.image.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_images_api_create_success(self):
        # Test: Create an image with an authenticated admin user
        access_token = AccessToken.for_user(self.admin_user)
        image = self.createTempImage()
        response = self.client.post(
            "/rental/images/",
            {"image": image},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Image.objects.count(), self.image_count + 1)
        
    def test_images_api_create_fail(self):
        # Test: Try to create an image without authentication
        image = self.createTempImage()
        response = self.client.post("/rental/images/", {"image": image})
        self.assertEqual(response.status_code, 401)
        
        # Test: Try to create an image with an non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.post(
            "/rental/images/",
            {"image": image},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Try to create an image with an inactive admin user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.post(
            "/rental/images/",
            {"image": image},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)

    def test_images_api_update_fail(self):
        # Test: Update an image with an authenticated admin user
        access_token = AccessToken.for_user(self.admin_user)
        image = self.createTempImage()
        response = self.client.put(
            f"/rental/images/{self.image.pk}/",
            {"image": image},
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Image.objects.count(), self.image_count)

    def test_images_api_delete_success(self):
        # Test: Delete an image with an authenticated admin user
        access_token = AccessToken.for_user(self.admin_user)
        response = self.client.delete(
            f"/rental/images/{self.image.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Image.objects.count(), self.image_count - 1)

    def test_images_api_delete_fail(self):
        # Test: Delete an image without an authenticated user
        response = self.client.delete(f"/rental/images/{self.image.pk}/")
        self.assertEqual(response.status_code, 401)

        # Test: Delete an image with an non-admin user
        access_token = AccessToken.for_user(self.user)
        response = self.client.delete(
            f"/rental/images/{self.image.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 403)

        # Test: Delete an image with an inactive authenticated user
        access_token = AccessToken.for_user(self.inactive_admin_user)
        response = self.client.delete(
            f"/rental/images/{self.image.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        self.assertEqual(response.status_code, 401)
