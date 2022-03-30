"""Tests to upload image API."""
import datetime
import json
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from machina.core.db.models import get_model
from PIL import Image

from ashley.factories import ForumFactory, UploadImageFactory, UserFactory

User = get_user_model()
UploadImage = get_model("ashley", "UploadImage")


class ImageUploadApiTest(TestCase):
    """Test the API to upload image."""

    def test_access_anonymous_api_upload_images_list(self):
        """Anonymous users should not be allowed to retrieve list of images"""
        response = self.client.get("/api/v1.0/images/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_anonymous_api_upload_images_item(self):
        """Anonymous users should not be allowed to retrieve image detail"""
        # At first, no image exists
        self.assertEqual(UploadImage.objects.count(), 0)
        image = UploadImageFactory()
        # Shows image has been created
        self.assertEqual(UploadImage.objects.count(), 1)
        response = self.client.get(f"/api/v1.0/images/{image.id}/")
        self.assertEqual(response.status_code, 404)

    def test_access_anonymous_api_create_upload_image(self):
        """An anonymous should not be able to create an image."""
        response = self.client.post("/api/v1.0/images/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_authenticated_api_upload_images_list(self):
        """Authenticated users should not be allowed to retrieve list of images"""
        user = UserFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/api/v1.0/images/")
        self.assertEqual(response.status_code, 405)
        content = json.loads(response.content)
        self.assertEqual(content, {"detail": 'Method "GET" not allowed.'})

    def test_access_authenticated_api_upload_images_item(self):
        """Authenticated users should not be allowed to retrieve image detail"""
        user = UserFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        image = UploadImageFactory()
        response = self.client.get(f"/api/v1.0/images/{image.id}/")
        self.assertEqual(response.status_code, 404)

    def test_access_authenticated_api_create_upload_image(self):
        """Authenticated users should be able to create an image but request
        needs to be completed."""
        user = UserFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.post("/api/v1.0/images/")
        # Request uncomplete so it returns a 400 but not a 403 anymore
        self.assertEqual(response.status_code, 400)

    def _generate_image(self, filename):
        """Generates image of 1 px"""
        image_file = BytesIO()
        image = Image.new("RGBA", size=(1, 1), color=(256, 256, 256))
        image.save(image_file, "png")
        image_file.seek(0)
        return ContentFile(image_file.read(), filename)

    def test_api_create_upload_image(self):
        """Verify that image gets created and uploaded"""
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        filename = f"test-{datetime.datetime.now().strftime('%f')}.png"
        data = {
            "file": self._generate_image(filename),
            "forum": forum.id,
            "poster": user.id,
        }
        # At first, no image exists
        self.assertEqual(UploadImage.objects.count(), 0)
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 201)

        # Gets last id generated
        image_db = UploadImage.objects.last()

        # Image should have be added with right values
        self.assertEqual(UploadImage.objects.count(), 1)
        self.assertEqual(image_db.forum.id, forum.id)
        self.assertEqual(image_db.poster.id, user.id)

        # Controls image's path is respected on server
        self.assertIn(f"image_uploads/{forum.id}/{user.id}/", image_db.file.name)

        # Controls file has been uploaded
        uploaded_file = image_db.file.open()
        self.assertGreater(uploaded_file.size, 0)
        self.assertIsNotNone(uploaded_file.read())

    def test_api_create_upload_image_same_filename(self):
        """
        If a user try to upload an image with the same filename, we make sure that two images gets
        uploaded with a different filename
        """
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        filename = "image.png"
        data = {
            "file": self._generate_image(filename),
            "forum": forum.id,
            "poster": user.id,
        }
        # At first, no image exists
        self.assertEqual(UploadImage.objects.count(), 0)
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 201)

        # Gets last id generated
        self.assertEqual(UploadImage.objects.count(), 1)
        image_db = UploadImage.objects.last()
        # Controls image's path is respected on server
        self.assertIn(f"image_uploads/{forum.id}/{user.id}/", image_db.file.name)
        # Controls file has been uploaded
        uploaded_file = image_db.file.open()
        self.assertGreater(uploaded_file.size, 0)
        self.assertIsNotNone(uploaded_file.read())

        # Upload an image with the same name
        data = {
            "file": self._generate_image(filename),
            "forum": forum.id,
            "poster": user.id,
        }
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 201)

        # A new image has been uploaded
        self.assertEqual(UploadImage.objects.count(), 2)
        image_db2 = UploadImage.objects.last()

        # Name of the file is different for the two images
        self.assertNotEqual(image_db.file.name, image_db2.file.name)
        # Controls image's path is respected on server
        self.assertIn(f"image_uploads/{forum.id}/{user.id}/", image_db2.file.name)
        # Controls file has been uploaded
        uploaded_file = image_db2.file.open()
        self.assertGreater(uploaded_file.size, 0)
        self.assertIsNotNone(uploaded_file.read())

    def test_api_cant_update_image(self):
        """Controls user doesn't have the right to update a record"""
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        filename = "image.png"
        data = {
            "file": self._generate_image(filename),
            "forum": forum.id,
            "poster": user.id,
        }
        # At first, no image exists
        self.assertEqual(UploadImage.objects.count(), 0)
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 201)

        # Gets last id generated
        self.assertEqual(UploadImage.objects.count(), 1)
        image_db = UploadImage.objects.last()
        # Controls image's path is respected on server
        self.assertIn(f"image_uploads/{forum.id}/{user.id}/", image_db.file.name)

        # Specify the id of the image for the update
        data = {
            "id": image_db.id,
            "file": self._generate_image(filename),
            "forum": forum.id,
            "poster": user.id,
        }
        response = self.client.put("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 405)
        content = json.loads(response.content)
        self.assertEqual(content, {"detail": 'Method "PUT" not allowed.'})

    def test_api_cant_delete_image(self):
        """Controls user doesn't have the right to delete a record"""
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        filename = "image.png"
        data = {
            "file": self._generate_image(filename),
            "forum": forum.id,
            "poster": user.id,
        }
        # At first, no image exists
        self.assertEqual(UploadImage.objects.count(), 0)
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 201)

        # Gets last id generated
        self.assertEqual(UploadImage.objects.count(), 1)
        image_db = UploadImage.objects.last()
        # Controls image's path is respected on server
        self.assertIn(f"image_uploads/{forum.id}/{user.id}/", image_db.file.name)

        # Specify the id of the image for the update
        data = {
            "id": image_db.id,
            "file": self._generate_image(filename),
            "forum": forum.id,
            "poster": user.id,
        }
        response = self.client.delete("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 405)
        content = json.loads(response.content)
        self.assertEqual(content, {"detail": 'Method "DELETE" not allowed.'})

    def test_api_create_upload_image_wrong_user_id(self):
        """Verify that if user id is wrong we get a 400 code"""
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        data = {
            "file": self._generate_image("test.png"),
            "forum": forum.id,
            "poster": user.id + 10,
        }
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_api_create_upload_image_no_user_id(self):
        """Verify that if user id is not send it's setup automatically to
        current user id"""
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        data = {
            "file": self._generate_image("test.png"),
            "forum": forum.id,
        }
        # At first, no image exists
        self.assertEqual(UploadImage.objects.count(), 0)
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 201)

        # Poster id should be the current user id logged in
        self.assertEqual(UploadImage.objects.count(), 1)

    def test_api_create_upload_bad_extension(self):
        """Make sure we can't upload a file with an unauthorized extension"""
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        video = SimpleUploadedFile(
            "file.mp4", b"file_content", content_type="video/mp4"
        )

        data = {
            "file": video,
            "forum": forum.id,
            "poster": user.id,
        }
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["file"],
            [
                (
                    "Upload a valid image. The file you uploaded was either "
                    + "not an image or a corrupted image."
                )
            ],
        )

    @override_settings(MAX_UPLOAD_FILE_MB=0)
    def test_api_create_upload_max_size(self):
        """Make sure we can't upload file over limit size"""
        user = UserFactory()
        forum = ForumFactory()
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")

        data = {
            "file": self._generate_image("test.png"),
            "forum": forum.id,
            "poster": user.id,
        }
        # Upload image
        response = self.client.post("/api/v1.0/images/", data, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["file"],
            ["The maximum file size that can be uploaded is 0 MB"],
        )
