"""Test suite for the Forum admin"""
from django.test import TestCase
from machina.core.db.models import get_model

from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

LTIContext = get_model("ashley", "LTIContext")
Forum = get_model("forum", "Forum")


class TestForumAdmin(TestCase):
    """Test for the Forum admin"""

    def test_show_lti(self):
        """Control lti_id field is display"""
        user = UserFactory(is_superuser=True, is_staff=True)
        self.client.force_login(user)

        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        url = f"/admin/forum/forum/{forum.id}/change/"
        response = self.client.get(url)

        self.assertContains(
            response, f'<div class="readonly">{forum.lti_id}</div>', html=True
        )
