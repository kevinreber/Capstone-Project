# Python standard libraries
import json
import io
import os
import requests
import sys

# Third-party libraries
from imagekitio import ImageKit
from flask import Flask, request, render_template, redirect, flash, jsonify, send_file, make_response, url_for, session, g, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

# Internal imports
from forms import UserForm
from models import db, connect_db, User
from config import DevelopmentConfig
from bp_auth.views import CURR_USER_KEY, TEMP_USER_IMAGES, do_logout

# Import Blueprints
from api.api import api
from bp_auth.views import bp_auth
from bp_upload.views import bp_upload
from bp_images.views import bp_images

# load environment variables
load_dotenv()

# Image Kit API
imagekit = ImageKit(
    private_key=os.getenv('IMG_KIT_PRIVATE_KEY'),
    public_key=os.getenv('IMG_KIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMG_KIT_URL_ENDPOINT'))

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(bp_auth)
app.register_blueprint(bp_upload)
app.register_blueprint(bp_images, url_prefix='/images')

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

##################################################################
#   USER ROUTES     ---------------------------------------------#
##################################################################


@app.route("/users/edit", methods=["GET", "POST"])
def user_profile():
    """User can edit their information"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect(url_for("home"))

    user = g.user
    form = UserForm(obj=user)

    if form.validate_on_submit():

        user.username = form.username.data
        user.email = form.email.data

        db.session.commit()
        flash("User updated!", "success")
        return redirect(url_for("user_profile"))

    return render_template("info.html", form=form)

##################################################################
#   IMAGE ROUTES   ----------------------------------------------#
##################################################################


# @app.route("/images", methods=["GET"])
# def get_images():
#     """Displays a list of all images"""
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     images = Image.query.filter(Image.user_id == g.user.id).all()

#     return render_template("footage/images.html", images=images)


# @app.route("/images/edit", methods=["GET"])
# def edit_images():
#     """Displays a form for each image so user can prepare CSV file"""

#     form = ShutterStockForm()

#     # Ensures users can only see images they've uploaded if they are logged in
#     # Users who are not logged in will have their images removed when they visit demo upload page
#     if not g.user:
#         images = session.get(TEMP_USER_IMAGES, None)
#     else:
#         images = Image.query.filter(Image.user_id == g.user.id).order_by(
#             Image.created_at.desc()).all()

#     return render_template("footage/edit-images.html", form=form, images=images)


if __name__ == '__main__':
    app.run()
