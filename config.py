import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    IMAGE_UPLOADS = os.environ.get('IMAGE_UPLOADS')
    ALLOWED_IMAGE_EXTENSIONS = ["PNG", "JPG", "JPEG"]

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
