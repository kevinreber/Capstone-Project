"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

from app import app
import os
from unittest import TestCase
from models import db, connect_db, User, Image
from bs4 import BeautifulSoup

CURR_USER_KEY = "curr_user"
TEMP_USER_IMAGES = "temp_user_images"

os.environ['DATABASE_URL'] = "postgresql:///automator-test"

# Now we can import app

db.create_all()

# Disable WTForms CSRF
app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user_id = 1111
        user = User.signup("Testing", "test1@test.com", "password")
        user.id = user_id

        db.session.add(user)
        db.session.commit()

        self.user = User.query.get(user_id)

        self.client = app.test_client()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    ####
    #
    # Users views upload page
    #
    ####
    def test_sess_user_upload(self):
        """When user doesn't log in, demo page shows"""

        with self.client as c:
            resp = c.get("/", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Demo", str(resp.data))
            self.assertIn("Want to upload more?", str(resp.data))

    def test_user_login_upload(self):
        """When user logs in, they should have more options"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.get("/", follow_redirects=True)
            # If user doesn't log in, demo page should appear
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Upload Media Files", str(resp.data))
            self.assertIn("Remove All", str(resp.data))
            self.assertIn(self.user.username, str(resp.data))
            self.assertIn("Log out", str(resp.data))
            self.assertIn("Footage", str(resp.data))

    ####
    #
    # Users views images page
    #
    ####

    def build_temp_image(self):
        """Adds image to users DB"""

        img = {
            "id": 1,
            "filename": "test1.jpg",
            "url": "http://www.test1.com",
            "thumbnail_url": "http://www.test1-thumb.com",
            "keywords": "python,flask,postgres",
            "description": "Test 1",
            "category1": "Abstract"
        }

        return img

    def build_image(self, u_id):
        """Adds image to users DB"""

        img = Image(
            id=1,
            filename="test1.jpg",
            url="http://www.test1.com",
            thumbnail_url="http://www.test1-thumb.com",
            keywords="python,flask,postgres",
            description="Test 1",
            category1="Abstract",
            user_id=u_id)

        return img

    def test_sess_users_no_uploads(self):
        """should show images missing if no images have been uploaded"""

        with self.client as c:
            resp = c.get("/images/edit")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("No images uploaded", str(resp.data))

    def test_users_no_uploads(self):
        """Should show images missing if no images have been uploaded."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.get("/images/edit")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("No images uploaded", str(resp.data))

    def test_sess_users_edit_images(self):
        """Should show image stored in flask session."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[TEMP_USER_IMAGES] = []
                temp_urls = sess[TEMP_USER_IMAGES]
                temp_urls.append(self.build_temp_image())
                sess[TEMP_USER_IMAGES] = temp_urls

            resp = c.get("/images/edit")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1.jpg", str(resp.data))

    def test_users_edit_images(self):
        """Should show image stored in DB."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            img = self.build_image(self.user.id)
            db.session.add(img)
            db.session.commit()

            resp = c.get("/images/edit")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1.jpg", str(resp.data))

    ####
    #
    # Users views footage list page
    #
    ####

    def test_unauthorized_access(self):
        """User should be redirected to demo page."""

        with self.client as c:
            resp = c.get("/images", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", str(resp.data))
            self.assertIn("Demo", str(resp.data))

    def test_users_no_footage_list(self):
        """Should show empty list."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            resp = c.get("/images", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Filename", str(resp.data))
            self.assertIn("No images uploaded", str(resp.data))

    def test_users_footage_list(self):
        """Should show footage list stored in DB."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id

            img = self.build_image(self.user.id)
            db.session.add(img)
            db.session.commit()

            resp = c.get("/images", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Filename", str(resp.data))
            self.assertIn("test1.jpg", str(resp.data))
