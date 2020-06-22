# Python standard libraries
import io
import os

# Third-party libraries
from flask import Flask, redirect, send_file, url_for, session, g, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv

# Internal imports
from models import db, connect_db, User
from config import DevelopmentConfig
from bp_auth.views import CURR_USER_KEY

# Import Blueprints
from api.api import api
from bp_auth.views import bp_auth
from bp_upload.views import bp_upload
from bp_images.views import bp_images
from bp_users.views import bp_users

# load environment variables
load_dotenv()

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(bp_auth)
app.register_blueprint(bp_upload)
app.register_blueprint(bp_images, url_prefix='/images')
app.register_blueprint(bp_users, url_prefix='/users')

app.config.from_object("config.DevelopmentConfig")
# debug = DebugToolbarExtension(app)

connect_db(app)

##################################################################
#   Check session if user logged in   ---------------------------#
##################################################################


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

##################################################################
#   HOME ROUTE      ---------------------------------------------#
##################################################################


@app.route("/")
def home():
    """Home Page"""

    return redirect(url_for("bp_upload.upload"))


if __name__ == '__main__':
    app.run()
