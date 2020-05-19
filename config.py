import os
from dotenv import load_dotenv
load_dotenv()


class BaseConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # DEBUG TOOLBAR
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    IMAGE_UPLOADS = os.environ.get('IMAGE_UPLOADS')
    ALLOWED_IMAGE_EXTENSIONS = ["PNG", "JPG", "JPEG"]

    BASE_URL = os.environ.get('BASE_URL')
    IMG_URL = os.environ.get('IMG_URL')
    DOWNLOAD_FOLDER = os.path.expanduser("~")+"/Downloads/"


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    DEBUG_TB_ENABLED = True


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    DEBUG_TB_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    pass
