import os
import requests
import csv
import base64
import sys
from imagekitio import ImageKit
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, flash, jsonify, send_file
from forms import ShutterStockForm, ImageUploadForm
from form_choices import SS_CHOICES_DICT
from url import BASE_URL, IMG_URL, DOWNLOAD_FOLDER
from werkzeug.utils import secure_filename
from models import db, connect_db, Image, User

# Load API keys from .env
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Image Kit API
imagekit = ImageKit(
    private_key=os.getenv('IMG_KIT_PRIVATE_KEY'),
    public_key=os.getenv('IMG_KIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMG_KIT_URL_ENDPOINT'))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['IMAGE_UPLOADS'] = '/Users/kevinreber/Documents/Code/00-Projects/00-Capstone Project 1/static/uploads'
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["PNG", "JPG", "JPEG"]

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///automator'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


def check_if_image(filename):
    """Check if file uploaded is a valid image"""

    if not "." in filename:
        return False

    # Get filename extension
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return True
    else:
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    """Home Page"""

    form = ImageUploadForm()

    if form.validate_on_submit():

        if request.files:

            # get image from form
            image = request.files["image"]

            if image.filename == "":
                flash("Image must have a filename", "danger")
                return redirect("/")

            if not check_if_image(image.filename):
                flash("File must be JPG or PNG", "danger")
                return redirect("/")

            else:
                # secure filename
                filename = secure_filename(image.filename)

                # save image to 'upload' folder
                image.save(os.path.join(
                    app.config['IMAGE_UPLOADS'], filename))

                # Get image path to pass into uploads
                img_path = os.path.join(app.config['IMAGE_UPLOADS'], filename)

                u_resp = upload_file(img_path, filename)

                # Get keywords from response
                """Use test keywords to avoid exceeding ratelimit of 100 per day"""
                # keywords = get_keywords(filename)

                keywords = [u"Cool", u"Interesting", u"Amazing",
                            u"Pythonic", u"Flasky", u"Eye Dropping", u"tags", u"new", u"html", u"css", u"max", u"sunset", u"sunrise", u"landscape scenic", u"scenic", u"sun", "sun chasing", u"clouds", u"cloudscape"]

                f_keywords = format_keywords(keywords)

                new_file = Image(id=u_resp["fileId"],
                                 filename=u_resp["name"],
                                 url=u_resp["url"],
                                 thumbnail_url=u_resp["thumbnailUrl"],
                                 keywords=f_keywords)

                db.session.add(new_file)
                db.session.commit()

                flash("Image saved", "success")
                print(u_resp)
                return redirect("/images")

    else:
        return render_template("upload.html", form=form)


def format_keywords(keywords):
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


@app.route("/images", methods=["GET"])
def file_data():
    """Displays a form for each image so user can prepare CSV file"""

    form = ShutterStockForm()

    image = Image.query.first()

    flash("Keywords Added", "success")
    return render_template("prepare_export.html", form=form, image=image)


def get_keywords(file_name):
    """Returns keywords from API request"""

    # path to image
    image_path = f"{IMG_URL}/{file_name}"

    # TODO: Make num_of_keywords dynamic, default to 3 for now
    num_of_keywords = 3
    params = {"num_keywords": num_of_keywords}

    # open image and send request to API
    with open(image_path, "rb") as image:
        data = {"data": image}
        resp = requests.post(BASE_URL, files=data, params=params, auth=(
            CLIENT_ID, CLIENT_SECRET)).json()

    # store response keywords
    keywords = [key["keyword"] for key in resp["keywords"]]

    return keywords


@app.route("/api/csv", methods=["POST"])
def get_csv():
    """Convert file data to CSV format"""

    # Store json data passed in
    data = request.json
    # Build data frame with data passed in from form
    df = build_data_frame(data)
    print("#################################")
    print("#################################")
    print(df)

    # TODO: format csv filename or make dynamic
    # Save data frame to user's downloads
    df.to_csv(f"{DOWNLOAD_FOLDER}/test.csv", index=False)
    flash("Downloaded CSV", "success")

    # Serialize data and return JSON
    s_data = serialize_data(data)
    img_json = jsonify(image=s_data)
    return (img_json, 201)


@app.route("/api/delete/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    """Delete from from DB and ImageKit.io"""

    file = Image.query.get_or_404(file_id)

    # Delete from ImageKit.io
    delete = imagekit.delete_file(file_id)

    # delete from DB
    db.session.delete(file)
    db.session.commit()

    flash("File Deleted", "success")
    print("Delete File-", delete)
    return jsonify(message="Deleted")


def serialize_data(data):
    """Serializes JSON data"""

    return {
        "filename": data["filename"],
        "description": data["description"],
        "keywords": data["keywords"],
        "category1": data["category1"],
        "category2": data["category2"],
        "editorial": data["editorial"],
        "r_rated": data["r_rated"],
        "location": data["location"]
    }


def build_data_frame(data):
    """Build data frame from form data for CSV export"""
    print("starting data frame...")

    # ? remove quotes from strings with .translate
    filename = data["filename"]
    desc = data["description"]
    keywords = data["keywords"]
    cat_1 = int(data["category1"])
    cat_2 = int(data["category2"])
    editorial = data["editorial"]
    r_rated = data["r_rated"]
    location = data["location"]

    categories = ", ".join(
        [SS_CHOICES_DICT.get(cat_1), SS_CHOICES_DICT.get(cat_2)])

    df_dict = {
        "Filename": [filename],
        "Description": [desc],
        "Keywords": [keywords],
        "Categories": [categories],
        "Editorial": [editorial],
        "r_rated": [r_rated],
        "location": [location]
    }

    df = pd.DataFrame(df_dict)
    return df
