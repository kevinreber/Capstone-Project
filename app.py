# Python standard libraries
import json
import io
import os
import requests
import base64
import sys

# Third-party libraries
from imagekitio import ImageKit
from flask import Flask, request, render_template, redirect, flash, jsonify, send_file, make_response, url_for, session, g
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

# Internal imports
from forms import ShutterStockForm, UserAddForm, LoginForm, UserForm
from models import db, connect_db, Image, User
from config import DevelopmentConfig

# load environment variables
load_dotenv()

# Image Kit API
imagekit = ImageKit(
    private_key=os.getenv('IMG_KIT_PRIVATE_KEY'),
    public_key=os.getenv('IMG_KIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMG_KIT_URL_ENDPOINT'))

app = Flask(__name__)

app.config.from_object("config.DevelopmentConfig")
# debug = DebugToolbarExtension(app)

connect_db(app)

CURR_USER_KEY = "curr_user"
TEMP_USER_IMAGES = "temp_images"

##################################################################
#   User signup/login/logout   ----------------------------------#
##################################################################
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

##################################################################
#   USER ROUTES signup/login/logout    --------------------------#
##################################################################


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if request.method == "POST":
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username/E-mail already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('/users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if request.method == "POST":
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('home'))

        flash("Invalid credentials.", 'danger')

    return render_template('/users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    ("You have logged out successfully", "success")
    return redirect("/")


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

    return render_template("users/info.html", form=form)


@app.route('/api/users/delete', methods=["DELETE"])
def delete_user():
    """Delete user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for("home"))

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    flash("User deleted", "success")
    return jsonify(message="User deleted")

##################################################################
#   HOME PAGE   -------------------------------------------------#
##################################################################


@app.route("/", methods=["GET", "POST"])
def home():
    """Home Page"""

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
            file_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)

            # Upload file to image host
            u_resp = upload_file(file_path, filename)

            # Get keywords from response
            #  ! Use test keywords to avoid exceeding ratelimit of 100 per day
            # keywords = get_keywords(file_path, 50)

            keywords = [u"Cool", u"Interesting", u"Amazing",
                        u"Pythonic", u"Flasky", u"Eye Dropping", u"tags", u"new", u"html", u"css", u"max", u"sunset"]

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
#   HOME PAGE HELPER FUNCTIONS  ---------------------------------#
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

##################################################################
#   API ROUTES   ------------------------------------------------#
##################################################################


@app.route("/api/delete/all", methods=["DELETE"])
def delete_all_files():
    """Delete all images from DB and ImageKit.io"""

    if not g.user:
        images = Image.query.filter(Image.user_id == None).all()
        # Delete all from DB
        Image.query.filter(Image.user_id == None).delete()

    else:
        # Get image in DB via file_id
        images = Image.query.filter(Image.user_id == g.user.id).all()
        # Delete all from DB
        Image.query.filter(Image.user_id == g.user.id).delete()

    # Delete all images from ImageKit.io
    delete = [imagekit.delete_file(img.id) for img in images]

    # # Delete all from DB
    # Image.query.delete()
    db.session.commit()

    flash("Removed all images", "success")
    print("Removed all images", delete)
    return jsonify(message="Deleted all images")


@app.route("/api/delete/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    """Delete from from DB and ImageKit.io"""

    # Get image in DB via file_id
    file = Image.query.get_or_404(file_id)

    # If a logged in user attempts to access another user's files
    # the logged in user will be redirected
    if g.user:
        if file.user_id != g.user.id:
            flash("Access unauthorized.", "danger")
            return redirect("/")

    # Delete from ImageKit.io
    delete = imagekit.delete_file(file_id)

    # Delete from DB
    db.session.delete(file)
    db.session.commit()

    flash("File Deleted", "success")
    print("Delete File-", delete)
    return jsonify(message="Deleted")


@app.route("/api/update", methods=["PATCH"])
def update_db():
    """Updates changes to DB"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # Store json data passed in
    data = json.loads(request.json['jsonData'])
    file_ids = [file_id for file_id in data]

    # Add each image update to db.session
    for file_id in file_ids:
        update_file(file_id, data[file_id])

    # Serialize data and return JSON
    s_data = [serialize_data(data, file) for file in file_ids]
    img_json = jsonify(data=s_data)

    # Commit all changes made to DB
    db.session.commit()
    flash("Files Saved", "success")
    return (img_json, 201)

##################################################################
#   API HELPER FUNCTIONS   --------------------------------------#
##################################################################


def update_file(file_id, data):
    """Updates file data in DB"""

    img = Image.query.get_or_404(file_id)

    img.filename = data.get("filename", img.filename)
    img.description = data.get("description", img.description)
    img.keywords = data.get("keywords", img.keywords)
    img.category1 = data.get("category1", img.category1)
    img.category2 = data.get("category2", img.category2)
    img.location = data.get("location", img.location)
    img.editorial = data.get("editorial", img.editorial)
    img.r_rated = data.get("r_rated", img.r_rated)

    db.session.add(img)
    print(f"Updated {img.filename}")


def serialize_data(data, id):
    """Serializes JSON data"""

    return {
        id: {
            "filename": data[id]["filename"],
            "description": data[id]["description"],
            "keywords": data[id]["keywords"],
            "category1": data[id]["category1"],
            "category2": data[id]["category2"],
            "editorial": data[id]["editorial"],
            "r_rated": data[id]["r_rated"],
            "location": data[id]["location"]
        }
    }


if __name__ == '__main__':
    app.run()
