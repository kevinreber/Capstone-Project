import os
import requests
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, flash
from forms import ShutterStockForm, ImageUploadForm
from form_choices import SS_CHOICES_DICT
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
                filename = secure_filename(image.filename)

                # save image to 'upload' folder
                image.save(os.path.join(
                    app.config['IMAGE_UPLOADS'], filename))
                flash("Image saved", "success")
                return redirect(f"/file/{filename}")

    else:
        return render_template("upload.html", form=form)


@app.route(f"/file/<image_name>", methods=["GET", "POST"])
def file_data(image_name):
    """User can input data to be exported out to CSV file"""

    form = ShutterStockForm()

    if form.validate_on_submit():

        df = build_data_frame(form)
        print("#################################")
        print("#################################")
        print(df)
        # TODO: format csv filename or make dynamic
        # Save data frame to user's downloads
        df.to_csv(f"{DOWNLOAD_FOLDER}/test.csv", index=False)
        flash("Downloaded CSV", "success")
        return redirect("/")

    # Get keywords from response
    """Use test keywords to avoid exceeding ratelimit of 100 per day"""
    # keywords = get_keywords(image_name)

    keywords = ["Cool", "Interesting", "Amazing",
                "Pythonic", "Flasky", "Eye Dropping", "tags", "new", "html", "css", "max", "sunset", "sunrise", "landscape scenic", "scenic", "sun", "sun chasing", "clouds", "cloudscape"]

    form.filename.data = image_name

    image_path = f"/static/uploads/{image_name}"

    # lower case keywords
    lc_keywords = [keyword.lower() for keyword in keywords]

    # join keywords with "," so they separate as tags
    keyword_tags = ",".join(lc_keywords)
    form.keywords.data = keyword_tags
    flash("Keywords Added", "success")
    return render_template("prepare_export.html", keywords=keywords, form=form, image_path=image_path)


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

    keywords = [key["keyword"] for key in resp["keywords"]]

    return keywords


def build_data_frame(form):
    """Build data frame from form data for CSV export"""
    print("starting data frame...")
    # TODO: handle keywords
    filename = form.filename.data
    desc = form.description.data
    keywords = form.keywords.data
    cat_1 = form.category1.data
    cat_2 = form.category2.data
    editorial = form.editorial.data
    r_rated = form.r_rated.data
    location = form.location.data

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
