import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Users Model"""

    __tablename = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.now)
    images = db.relationship('Image', backref="user",
                             cascade="all, delete")

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @property
    def formated_date(self):
        """Reformat date"""
        """ex. Fri Apr 17 2020, 05:01 PM"""

        return self.created_at.strftime("%a %b %d %Y, %I:%M %p")


class Image(db.Model):
    """Images Model"""

    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, nullable=False, unique=True)
    source = db.Column(db.String, nullable=False, unique=True)
    keywords = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.now)

    @property
    def formated_date(self):
        """Reformat date"""
        """ex. Fri Apr 17 2020, 05:01 PM"""

        return self.created_at.strftime("%a %b %d %Y, %I:%M %p")

