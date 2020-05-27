import os
from dotenv import load_dotenv
load_dotenv()


class BaseConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # DEBUG TOOLBAR
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # KEYWORDS API
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    BASE_URL = os.environ.get('BASE_URL')

    # SQL ALCHEMY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # GOOGLE RECAPTCHA
    RECAPTCHA_PUBLIC_KEY = os.environ.get('GOOGLE_RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = os.environ.get(
        'GOOGLE_RECAPTCHA_PRIVATE_KEY')

    # FILES
    UPLOADED_PHOTOS_DEST = os.getcwd() + '/static/uploads'
    ALLOWED_IMAGE_EXTENSIONS = ["PNG", "JPG", "JPEG"]


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql:///automator')
    DEBUG_TB_ENABLED = True


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_TEST_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_TEST_URI')
    DEBUG_TB_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    pass
