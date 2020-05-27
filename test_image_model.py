"""Image model tests."""

# run these tests like:
#
#    python -m unittest test_image_model.py

from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Image

os.environ['DATABASE_URL'] = "postgresql:///automator-test"

# Now we can import app

db.create_all()


class ImageModelTestCase(TestCase):
    """Test Image Model."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid = 12345
        u = User.signup("test", "test@test.com", "password")

        u.id = self.uid
        db.session.add(u)
        db.session.commit()

        self.u = User.query.get(self.uid)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def add_images(self):
        """Adds image to users DB"""

        img1 = Image(
            id=1,
            filename="test1.jpg",
            url="http://www.test1.com",
            thumbnail_url="http://www.test1-thumb.com",
            keywords="python,flask,postgres",
            description="Test 1",
            category1="Abstract",
            user_id=self.uid)

        img2 = Image(
            id=2,
            filename="test2.jpg",
            url="http://www.test2.com",
            thumbnail_url="http://www.test2-thumb.com",
            keywords="html,css,javascript",
            description="Test 2",
            category1="Abstract",
            user_id=self.uid)

        db.session.add_all([img1, img2])
        db.session.commit()

    def test_user_model(self):
        """Does basic user model work?"""

        # User should have no images on start
        self.assertEqual(len(self.u.images), 0)

    def test_zero_images(self):
        """Does image model work"""

        images = Image.query.all()
        self.assertEqual(len(images), 0)

    def test_adding_images(self):
        """Does adding images work"""

        self.add_images()
        images = Image.query.all()
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0].filename, "test1.jpg")
        self.assertEqual(images[1].filename, "test2.jpg")

    def test_image_user_relationship_model(self):
        """Does relationship between images and user work?"""

        self.add_images()

        # User should have two images
        self.assertEqual(len(self.u.images), 2)
        self.assertEqual(self.u.images[0].filename, "test1.jpg")
        self.assertEqual(self.u.images[1].filename, "test2.jpg")
