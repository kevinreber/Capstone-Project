import json
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
from werkzeug.utils import secure_filename
from models import db, connect_db, Image, User
from config import Config

# Image Kit API
imagekit = ImageKit(
    private_key=os.getenv('IMG_KIT_PRIVATE_KEY'),
    public_key=os.getenv('IMG_KIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMG_KIT_URL_ENDPOINT'))

app = Flask(__name__)

app.config.from_object("config.Config")

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
                save_file(image, filename)

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

                # Delete image from upload directory after saving image to DB
                clear_uploads(img_path)

                flash("Image saved", "success")
                print(u_resp)
                return redirect("/images")

    else:
        return render_template("upload.html", form=form)


def save_file(file, filename):
    """Saves file to uploads folder"""

    file.save(os.path.join(
        app.config['IMAGE_UPLOADS'], filename))
    print("File saved!")


def clear_uploads(file):
    """Removes uploaded file after being saved to DB"""

    if os.path.exists(file):
        os.remove(file)
        print("File removed!")

    else:
        print("The file does not exist")


def format_keywords(keywords):
    """formats keywords to store in DB"""

    # lower case all keywords
    l_keywords = [keyword.lower() for keyword in keywords]
    # join keywords into string to store in DB
    # tagify js will automatically separate keywords via ","
    s_keywords = ",".join(l_keywords)

    return s_keywords


# ! TODO: Look into creating private images
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

    images = Image.query.all()

    flash("Keywords Added", "success")
    return render_template("prepare_export.html", form=form, images=images)


def get_keywords(file_name):
    """Returns keywords from API request"""

    # path to image
    image_path = f"{app.config['IMG_URL']}/{file_name}"

    # TODO: Make num_of_keywords dynamic, default to 3 for now
    num_of_keywords = 3
    params = {"num_keywords": num_of_keywords}

    # open image and send request to API
    with open(image_path, "rb") as image:
        data = {"data": image}
        resp = requests.post(app.config["BASE_URL"], files=data, params=params, auth=(
            app.config["CLIENT_ID"], app.config["CLIENT_SECRET"])).json()

    # store response keywords
    keywords = [key["keyword"] for key in resp["keywords"]]

    return keywords


@app.route("/api/delete/<file_id>", methods=["DELETE"])
def delete_file(file_id):
    """Delete from from DB and ImageKit.io"""

    # Get image in DB via file_id
    file = Image.query.get_or_404(file_id)

    # Delete from ImageKit.io
    delete = imagekit.delete_file(file_id)

    # delete from DB
    db.session.delete(file)
    db.session.commit()

    flash("File Deleted", "success")
    print("Delete File-", delete)
    return jsonify(message="Deleted")

# ! TODO:
# ! loop file data into database
# ! save button first
# ! after database is updated
    # ! use database information to build CSV


@app.route("/api/csv", methods=["POST"])
def get_csv():
    """Convert file data to CSV format"""

    # Store json data passed in
    data = json.loads(request.json['jsonData'])
    file_ids = [file_id for file_id in data]

    # Build data frame with data passed in from form
    df = build_data_frame(data, file_ids)

    # ! TODO: format csv filename or make dynamic
    # Save data frame to user's downloads
    df.to_csv(f"{app.config['DOWNLOAD_FOLDER']}/test.csv", index=False)
    flash("Downloaded CSV", "success")

    # Serialize data and return JSON
    s_data = [serialize_data(data, file) for file in file_ids]
    img_json = jsonify(data=s_data)

    return (img_json, 201)


def build_data_frame(data, file_ids):
    """Build data frame from form data for CSV export"""

    # Formats data into CSV format
    filename = [data[img]["filename"] for img in file_ids]
    description = [data[img]["description"] for img in file_ids]
    keywords = [data[img]["keywords"] for img in file_ids]
    categories = [data[img]["categories"] for img in file_ids]
    editorial = [data[img]["editorial"] for img in file_ids]
    r_rated = [data[img]["r_rated"] for img in file_ids]
    location = [data[img]["location"] for img in file_ids]

    df_dict = {
        "Filename": filename,
        "Description": description,
        "Keywords": keywords,
        "Categories": categories,
        "Editorial": editorial,
        "r_rated": r_rated,
        "location": location
    }

    df = pd.DataFrame(df_dict)

    return df


def serialize_data(data, id):
    """Serializes JSON data"""

    return {
        id: {
            "filename": data[id]["filename"],
            "description": data[id]["description"],
            "keywords": data[id]["keywords"],
            "categories": data[id]["categories"],
            "editorial": data[id]["editorial"],
            "r_rated": data[id]["r_rated"],
            "location": data[id]["location"]
        }
    }
