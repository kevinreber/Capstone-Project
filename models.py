import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Users Model"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)

    images = db.relationship('Image', backref="user",
                             cascade="all, delete-orphan")
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.now)

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
    tags = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.now)

    @property
    def formated_date(self):
        """Reformat date"""
        """ex. Fri Apr 17 2020, 05:01 PM"""

        return self.created_at.strftime("%a %b %d %Y, %I:%M %p")
