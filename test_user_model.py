"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from app import app
import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Image
from config import TestingConfig

os.environ['DATABASE_URL'] = "postgresql:///automator-test"

# Now we can import app

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        uid1 = 1111
        u1 = User.signup("test1", "test1@test.com", "password")
        u1.id = uid1

        uid2 = 2222
        u2 = User.signup("test2", "test2@test.com", "password")
        u2.id = uid2

        db.session.add_all([u1, u2])
        db.session.commit()

        self.u1 = User.query.get(uid1)
        self.u2 = User.query.get(uid2)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    ####
    #
    # Images tests
    #
    ####

    # Add test images to user
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
            user_id=1111)

        img2 = Image(
            id=2,
            filename="test2.jpg",
            url="http://www.test2.com",
            thumbnail_url="http://www.test2-thumb.com",
            keywords="html,css,javascript",
            description="Test 2",
            category1="Abstract",
            user_id=2222)

        db.session.add_all([img1, img2])
        db.session.commit()

    def test_user_has_no_images(self):
        """Tests if users add image"""

        # test zero images
        self.assertEqual(len(self.u1.images), 0)
        self.assertEqual(len(self.u2.images), 0)

    def test_user_adds_image(self):
        """Adds images to users accounts"""

        self.add_images()

        self.assertEqual(len(self.u1.images), 1)
        self.assertEqual(len(self.u2.images), 1)

    ####
    #
    # Signup tests
    #
    ####
    def test_valid_signup(self):
        """Test when a new user signs up"""

        test_user = User.signup(
            "test_user",
            "test_user@test.com",
            "password"
        )

        test_user_id = 9999
        test_user.id = test_user_id
        db.session.add(test_user)
        db.session.commit()

        user = User.query.get(test_user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "test_user")
        self.assertEqual(user.email, "test_user@test.com")
        # Password should be hashed
        self.assertNotEqual(user.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """Invald username during sign up should return error"""

        invalid = User.signup(None, "test_user@test.com", "password")
        u_id = 9999
        invalid.id = u_id

        # Raises Integrity Error if submitted
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        """Invald email during sign up should return error"""

        invalid = User.signup("test_user", None, "password")
        u_id = 9999
        invalid.id = u_id

        # Raises Integrity Error if submitted
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        """Invald password during sign up should return error"""

        with self.assertRaises(ValueError) as context:
            invalid = User.signup("test_user", "test_user@test.com", "")

        with self.assertRaises(ValueError) as context:
            User.signup("test_user", "test_user@test.com", None)

    ####
    #
    # Authentication tests
    #
    ####

    def test_valid_authentication(self):
        """User data should be returned if User.authenticate"""
        user = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.u1.id)

    def test_invalid_username(self):
        """Should return False if incorrect username"""
        self.assertFalse(User.authenticate("wrong_username", "password"))

    def test_wrong_password(self):
        """Should return False if incorrect password"""
        self.assertFalse(User.authenticate(self.u1.username, "wrong_password"))
