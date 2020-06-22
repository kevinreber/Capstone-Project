# Python standard libraries
import json
import io
import os
import requests
import base64
import sys

# Third-party libraries
from imagekitio import ImageKit
from flask import Flask, request, render_template, redirect, flash, jsonify, send_file, make_response, url_for, session, g, Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

# Google Cloud Vision
from google.cloud.vision_v1 import enums
from google.cloud import vision_v1
from google.cloud.vision import types
from google.cloud import vision

# Internal imports
from forms import ShutterStockForm, UserForm
from models import db, connect_db, Image, User
from config import DevelopmentConfig
from bp_auth.auth import CURR_USER_KEY, TEMP_USER_IMAGES, do_logout

# Import Blueprints
from api.api import api
from bp_auth.auth import bp_auth

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

    return redirect(url_for("upload"))

##################################################################
#   UPLOAD PAGE   -----------------------------------------------#
##################################################################


@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload Page"""

    # Make sure to clear any images already existing in session
    if TEMP_USER_IMAGES in session and len(session[TEMP_USER_IMAGES]) != 0:
        del_img = session[TEMP_USER_IMAGES][0]

        # Delete from ImageKit.io
        delete = imagekit.delete_file(del_img["id"])
        print("Image removed", delete)

    session[TEMP_USER_IMAGES] = []

    # list to hold our uploaded image urls
    temp_urls = session[TEMP_USER_IMAGES]

    if request.method == "POST":
        """File will be returned as a FileStorage"""

        if request.files:
            file = request.files["file"]

            # secure filename
            filename = secure_filename(file.filename)

            # save file to 'upload' folder
            save_file(file, filename)

            # Get file path
            file_path = os.path.join(
                app.config['UPLOADED_PHOTOS_DEST'], filename)

            # Upload file to image host
            u_resp = upload_file(file_path, filename)

            # Get keywords from response
            #  ! Use test keywords to avoid exceeding ratelimit of 100 per day
            # Google keywords
            g_keywords = detect_labels(file_path)
            # Everypixel keywords
            e_keywords = get_keywords(file_path, 5)
            keywords = g_keywords + e_keywords

            # Test keywords below
            # keywords = [u"Cool", u"Interesting", u"Amazing",
            #             u"Pythonic", u"Flasky", u"Eye Dropping", u"tags", u"new", u"html", u"css", u"max", u"sunset"]

            parsed_keywords = parse_keywords(keywords)

            if not g.user:

                image = {
                    "id": u_resp["fileId"],
                    "filename": u_resp["name"],
                    "thumbnail_url": u_resp["thumbnailUrl"],
                    "keywords": parsed_keywords,
                    "description": "",
                    "category1": "",
                    "category2": "",
                    "location": "",
                    "editorial": False,
                    "r_rated": False
                }

                temp_urls.append(image)
                session[TEMP_USER_IMAGES] = temp_urls

            else:
                new_file = Image(id=u_resp["fileId"],
                                 user_id=g.user.id,
                                 filename=u_resp["name"],
                                 url=u_resp["url"],
                                 thumbnail_url=u_resp["thumbnailUrl"],
                                 keywords=parsed_keywords)

                db.session.add(new_file)
                db.session.commit()

        # Delete image from upload directory after saving image to DB
        clear_uploads(file_path)

        flash("Images saved", "success")
        flash("Keywords Added", "success")
        print(u_resp)
        return "uploading..."

    else:
        return render_template("upload.html")

##################################################################
#   UPLOAD PAGE HELPER FUNCTIONS  -------------------------------#
##################################################################


def save_file(file, filename):
    """Saves file to uploads folder"""

    file.save(os.path.join(
        app.config['UPLOADED_PHOTOS_DEST'], filename))
    print("File saved")


def clear_uploads(file):
    """Removes uploaded file after being saved to DB"""

    if os.path.exists(file):
        os.remove(file)
        print("File removed")

    else:
        print("The file does not exist")


def parse_keywords(keywords):
    """formats keywords to store in DB"""

    # lower case all keywords
    l_keywords = [keyword.lower() for keyword in keywords]
    # join keywords into string to store in DB
    # tagify js will automatically separate keywords via ","
    s_keywords = ",".join(l_keywords)

    return s_keywords


def upload_file(img, filename):
    """Uploads image to ImageKit.io and returns response"""

    with open(img, mode="rb") as img:
        imgstr = base64.b64encode(img.read())

    resp = imagekit.upload(
        file=imgstr,
        file_name=filename,
        options={
            "response_fields": ["is_private_file"],
        })
    return resp["response"]

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


@app.route("/images", methods=["GET"])
def get_images():
    """Displays a list of all images"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    images = Image.query.filter(Image.user_id == g.user.id).all()

    return render_template("footage/images.html", images=images)


@app.route("/images/edit", methods=["GET"])
def edit_images():
    """Displays a form for each image so user can prepare CSV file"""

    form = ShutterStockForm()

    # Ensures users can only see images they've uploaded if they are logged in
    # Users who are not logged in will have their images removed when they visit demo upload page
    if not g.user:
        images = session.get(TEMP_USER_IMAGES, None)
    else:
        images = Image.query.filter(Image.user_id == g.user.id).order_by(
            Image.created_at.desc()).all()

    return render_template("footage/edit-images.html", form=form, images=images)


##################################################################
#   IMAGE HELPER FUNCTIONS   ------------------------------------#
##################################################################

def detect_labels(img_path):
    """Returns keywords from Google Vision's API request"""

    client = vision.ImageAnnotatorClient()

    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.label_detection(image=image)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    labels = response.label_annotations

    # store response keywords
    keywords = [label.description for label in labels]

    return keywords


def get_keywords(img_path, max_keywords):
    """Returns keywords from API request"""

    # total keyword results should equal 50
    params = {"num_keywords": max_keywords}

    # open image and send request to API
    with open(img_path, "rb") as image:
        data = {"data": image}
        resp = requests.post(app.config["BASE_URL"], files=data, params=params, auth=(
            app.config["CLIENT_ID"], app.config["CLIENT_SECRET"])).json()

    # store response keywords
    keywords = [key["keyword"] for key in resp["keywords"]]

    return keywords


if __name__ == '__main__':
    app.run()
