"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, User, Image
from bs4 import BeautifulSoup

# os.environ['DATABASE_URL'] = "postgresql:///automator-test"

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

        uid1 = 1111
        u1 = User.signup("test1", "test1@test.com", "password")
        u1.id = uid1

        db.session.add(u1)
        db.session.commit()

        self.u1 = User.query.get(uid1)

        self.client = app.test_client()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    ####
    #
    # Users views tests
    #
    ####
    def test_user_index(self):
        with self.client as c:
            resp = c.get("/")

            # If user doesn't log in, demo page should appear
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Demo", str(resp.data))
            self.assertIn("Create an account", str(resp.data))

    def test_users_edit_images(self):
        with self.client as c:
            resp = c.get("/images/edit")

            # should show images missing because no images have been uploaded
            self.assertEqual(resp.status_code, 200)
            self.assertIn("No images uploaded", str(resp.data))

    # def test_user_show(self):
    #     with self.client as c:
    #         resp = c.get(f"users/{self.testuser.id}")

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("@testuser", str(resp.data))

    # ####
    # #
    # # Users likes tests
    # #
    # ####
    # def setup_likes(self):
    #     """Adds messages to DB"""

    #     m1 = Message(text="trending warble", user_id=self.testuser_id)
    #     m2 = Message(text="Eating some lunch", user_id=self.testuser_id)
    #     m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
    #     db.session.add_all([m1, m2, m3])
    #     db.session.commit()

    #     l1 = Likes(user_id=self.testuser.id, message_id=9876)
    #     db.session.add(l1)
    #     db.session.commit()

    # def test_user_show_with_likes(self):
    #     self.setup_likes()

    #     with self.client as c:
    #         resp = c.get(f"/users/{self.testuser_id}")

    #         self.assertIn("@testuser", str(resp.data))

    #         # set up BeautifulSoup to compare html data
    #         soup = BeautifulSoup(str(resp.data), 'html.parser')

    #         # find html in soup
    #         found = soup.find_all("li", {"class": "stat"})

    #         self.assertEqual(len(found), 4)

    #         # test for a count of 2 messages
    #         self.assertIn("2", found[0].text)

    #         # Test for a count of 0 followers
    #         self.assertIn("0", found[1].text)

    #         # Test for a count of 0 following
    #         self.assertIn("0", found[2].text)

    #         # Test for a count of 1 like
    #         self.assertIn("1", found[3].text)

    # def test_add_like(self):
    #     m = Message(id=7777, text="Testing add like", user_id=self.u1.id)
    #     db.session.add(m)
    #     db.session.commit()

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             # add self.testuser into session
    #             sess[CURR_USER_KEY] = self.testuser_id

    #         resp = c.post("/messages/7777/like", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)

    #         likes = Likes.query.filter(Likes.message_id == 7777).all()
    #         self.assertEqual(len(likes), 1)
    #         self.assertEqual(likes[0].user_id, self.testuser_id)

    # def test_remove_like(self):
    #     self.setup_likes()

    #     m = Message.query.filter(Message.text == "likable warble").one()
    #     self.assertIsNotNone(m)

    #     # self.u1 should be m.user_id
    #     self.assertNotEqual(m.user_id, self.testuser_id)

    #     # get like of self.testuser: "likable warble"
    #     l = Likes.query.filter(
    #         Likes.user_id == self.testuser_id and Likes.message_id == m.id).one()

    #     # make sure self.testuser likes "likable warble"
    #     self.assertIsNotNone(l)

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             # add self.testuser into session
    #             sess[CURR_USER_KEY] = self.testuser_id

    #         # this request will unlike message because message is already liked
    #         resp = c.post(f"/messages/{m.id}/like", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)

    #         likes = Likes.query.filter(Likes.message_id == m.id).all()
    #         # like has been deleted
    #         self.assertEqual(len(likes), 0)

    # def test_unauthorized_like(self):
    #     """Test if user tries to like message while not logged in"""

    #     self.setup_likes()

    #     m = Message.query.filter(Message.text == "likable warble").one()
    #     self.assertIsNotNone(m)

    #     like_count = Likes.query.count()

    #     with self.client as c:
    #         resp = c.post(f"/messages/{m.id}/like", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)

    #         self.assertIn("Access unauthorized", str(resp.data))

    #         # Number of likes should not change during request
    #         self.assertEqual(like_count, Likes.query.count())

    # ####
    # #
    # # Users followers/following tests
    # #
    # ####
    # def setup_followers(self):
    #     """Set up followers for follower/following tests"""

    #     f1 = Follows(user_being_followed_id=self.u1_id,
    #                  user_following_id=self.testuser_id)
    #     f2 = Follows(user_being_followed_id=self.u2_id,
    #                  user_following_id=self.testuser_id)
    #     f3 = Follows(user_being_followed_id=self.testuser_id,
    #                  user_following_id=self.u1_id)

    #     db.session.add_all([f1, f2, f3])
    #     db.session.commit()

    # def test_show_user_show_with_follows(self):

    #     self.setup_followers()
    #     with self.client as c:
    #         resp = c.get(f"/users/{self.testuser_id}")

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("@testuser", str(resp.data))

    #         # set up BeautifulSoup to compare html data
    #         soup = BeautifulSoup(str(resp.data), 'html.parser')

    #         # find html in soup
    #         found = soup.find_all("li", {"class": "stat"})

    #         self.assertEqual(len(found), 4)

    #         # test for a count of 0 messages
    #         self.assertIn("0", found[0].text)

    #         # Test for a count of 2 following
    #         self.assertIn("2", found[1].text)

    #         # Test for a count of 1 follower
    #         self.assertIn("1", found[2].text)

    #         # Test for a count of 0 likes
    #         self.assertIn("0", found[3].text)

    # def test_show_following(self):

    #     self.setup_followers()
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser_id

    #         resp = c.get(f"/users/{self.testuser_id}/following")
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("@abc", str(resp.data))
    #         self.assertIn("@efg", str(resp.data))
    #         self.assertNotIn("@hij", str(resp.data))
    #         self.assertNotIn("@testing", str(resp.data))

    # def test_show_followers(self):

    #     self.setup_followers()
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser_id

    #         resp = c.get(f"/users/{self.testuser_id}/followers")

    #         self.assertIn("@abc", str(resp.data))
    #         self.assertNotIn("@efg", str(resp.data))
    #         self.assertNotIn("@hij", str(resp.data))
    #         self.assertNotIn("@testing", str(resp.data))

    # def test_unauthorized_following_page_access(self):
    #     """Test if user tries to view following while not logged in"""

    #     self.setup_followers()

    #     with self.client as c:
    #         resp = c.get(
    #             f"/users/{self.testuser_id}/following", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertNotIn("@abc", str(resp.data))
    #         self.assertIn("Access unauthorized", str(resp.data))

    # def test_unauthorized_followers_page_access(self):
    #     """Test if user tries to view followers while not logged in"""

    #     self.setup_followers()

    #     with self.client as c:
    #         resp = c.get(
    #             f"/users/{self.testuser_id}/followers", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)
    #         self.assertNotIn("@abc", str(resp.data))
    #         self.assertIn("Access unauthorized", str(resp.data))
