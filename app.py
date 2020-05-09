import os
from flask import Flask, request, render_template, redirect, flash
from forms import ShutterStockForm, ImageUploadForm
import requests
from secrets import CLIENT_ID, CLIENT_SECRET, BASE_URL
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['IMAGE_UPLOADS'] = '/Users/kevinreber/Documents/Code/00-Projects/00-Capstone Project 1/static/uploads'
app.config['ALLOWED_IMAGE_EXTENSIONS'] = ["PNG", "JPG", "JPEG"]

IMG_URL = '/Users/kevinreber/Documents/Code/00-Projects/00-Capstone Project 1/static/uploads'


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
                print("Image saved")
                return redirect(f"/img/{filename}")

    else:
        return render_template("image_upload.html", form=form)


@app.route(f'/img/<image_name>', methods=['GET', 'POST'])
def file_data(image_name):

    form = ShutterStockForm()

    # TODO: Make num_of_keywords dynamic, default to 5 for now
    num_of_keywords = 3

    params = {"num_keywords": num_of_keywords}

    # path to image
    image_path = f"{IMG_URL}/{image_name}"

    # open image and send request to API
    with open(image_path, "rb") as image:

        data = {"data": image}
        resp = requests.post(BASE_URL, files=data, params=params, auth=(
            CLIENT_ID, CLIENT_SECRET)).json()

    keywords = [key["keyword"] for key in resp["keywords"]]

    # if form.validate_on_submit():

    #     filename = images.save(form.image.data)
    #     return f'Filename: { filename }'

    return render_template("prepare_export.html", keywords=keywords, form=form)
