import os
import requests
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, flash
from forms import ShutterStockForm, ImageUploadForm
from url import BASE_URL, IMG_URL, DOWNLOAD_FOLDER
from werkzeug.utils import secure_filename

# Load API keys from .env
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['IMAGE_UPLOADS'] = '/Users/kevinreber/Documents/Code/00-Projects/00-Capstone Project 1/static/uploads'
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["PNG", "JPG", "JPEG"]


def allowed_image(filename):
    """Checks if file uploaded is a valid image"""

    if not "." in filename:
        return False

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

            if not allowed_image(image.filename):
                flash("File must be JPG or PNG", "danger")
                return redirect("/")

            else:
                filename = secure_filename(image.filename)

                # save image to 'upload' folder
                image.save(os.path.join(
                    app.config['IMAGE_UPLOADS'], filename))
                flash("Image saved", "success")
                return redirect(f"/file/{filename}")

    else:
        return render_template("image_upload.html", form=form)


@app.route(f"/file/<image_name>", methods=["GET", "POST"])
def file_data(image_name):
    """User can input data to be exported out to CSV file"""

    form = ShutterStockForm()
    # TODO: Make num_of_keywords dynamic, default to 3 for now
    num_of_keywords = 3
    params = {"num_keywords": num_of_keywords}

    # path to image
    image_path = f"{IMG_URL}/{image_name}"

    if form.validate_on_submit():
        print("converting...")

        df = get_csv(form)

        print(df)
        df.to_csv(f"{DOWNLOAD_FOLDER}/test.csv", index=False)
        flash("Downloaded CSV", "success")
        return redirect("/")

    # open image and send request to API
    with open(image_path, "rb") as image:

        data = {"data": image}
        resp = requests.post(BASE_URL, files=data, params=params, auth=(
            CLIENT_ID, CLIENT_SECRET)).json()

    # Get keywords from response
    keywords = [key["keyword"] for key in resp["keywords"]]

    return render_template("prepare_export.html", keywords=keywords, form=form)


# @app.route("/export", methods=["POST"])
def get_csv(form):
    """Take form data and export into CSV file"""

    filename = form.filename.data
    desc = form.description.data
    keywords = form.keywords.data   # Need to parse keywords
    cat_1 = form.category1.data
    cat_2 = form.category2.data
    editorial = form.editorial.data
    r_rated = form.r_rated.data
    location = form.location.data

    csv_dict = {
        "Filename": [filename],
        "Description": [desc],
        "Keywords": [keywords],
        "Categories": [cat_1],  # join categories and seperate with ","
        "Editorial": [editorial],
        "r_rated": [r_rated],
        "location": [location]
    }

    df = pd.DataFrame(csv_dict)
    return df
