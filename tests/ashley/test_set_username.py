"""
Tests for the set username feature.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ashley.factories import UserFactory


class SetUsernameTestCase(TestCase):
    """Test the set username feature on a user profile"""

    def test_set_username_guest(self):
        """A non-authenticated user should not be able to use the set username feature"""

        response = self.client.get("/profile/username")
        self.assertEqual(302, response.status_code)
        self.assertIn(settings.LOGIN_URL, response.url)

        update_response = self.client.post(
            "/profile/username", data={"public_username": "Test"}
        )
        self.assertEqual(302, update_response.status_code)
        self.assertIn(settings.LOGIN_URL, update_response.url)

        delete_response = self.client.delete("/profile/username")
        self.assertEqual(302, delete_response.status_code)
        self.assertIn(settings.LOGIN_URL, delete_response.url)

        put_response = self.client.put(
            "/profile/username", data={"public_username": "Test"}
        )
        self.assertEqual(302, put_response.status_code)
        self.assertIn(settings.LOGIN_URL, put_response.url)

    def test_set_username_empty(self):
        """A user with an empty public_username should be able to set it"""

        user = UserFactory(public_username="")

        self.assertEqual("", user.public_username)
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/profile/username")
        self.assertEqual(200, response.status_code)

        update_response = self.client.post(
            "/profile/username", data={"public_username": "Test"}
        )
        self.assertEqual(302, update_response.status_code)
        self.assertEqual(reverse("forum:index"), update_response.url)
        self.assertEqual(
            get_user_model().objects.filter(public_username="Test").count(), 1
        )

        delete_response = self.client.delete("/profile/username")
        self.assertEqual(403, delete_response.status_code)

        put_response = self.client.put(
            "/profile/username", data={"public_username": "Test put"}
        )
        self.assertEqual(403, put_response.status_code)

    def test_set_username_non_empty(self):
        """A user with a non-empty public_username should not be able to change it"""

        user = UserFactory(public_username="test_username")

        self.assertEqual("test_username", user.public_username)
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/profile/username")
        self.assertEqual(403, response.status_code)

        update_response = self.client.post(
            "/profile/username", data={"public_username": "Test"}
        )
        self.assertEqual(403, update_response.status_code)

        delete_response = self.client.delete("/profile/username")
        self.assertEqual(403, delete_response.status_code)

        put_response = self.client.put(
            "/profile/username", data={"public_username": "Test put"}
        )
        self.assertEqual(403, put_response.status_code)
