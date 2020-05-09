import os
from flask import Flask, request, render_template, redirect
from forms import ShutterStockForm, ImageUploadForm
import requests
from secrets import CLIENT_ID, CLIENT_SECRET, BASE_URL

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'
app.config['IMAGE_UPLOADS'] = '/Users/kevinreber/Documents/Code/00-Projects/00-Capstone Project 1/static/uploads'


@app.route("/", methods=["GET", "POST"])
def home():
    """Home Page"""

    form = ImageUploadForm()

    if form.validate_on_submit():
        form = ShutterStockForm()

        if request.files:

            # get image from form
            image = request.files["image"]

            # save image to 'upload' folder
            image.save(os.path.join(
                app.config['IMAGE_UPLOADS'], image.filename))

            # path to image
            image_path = f"/Users/kevinreber/Documents/Code/00-Projects/00-Capstone Project 1/static/uploads/{image.filename}"

            # TODO: Make num_of_keywords dynamic, default to 5 for now
            num_of_keywords = 5

            params = {"num_keywords": num_of_keywords}

            # open image and send request to API
            with open(image_path, "rb") as request_image:
                data = {"data": request_image}

                resp = requests.post(BASE_URL,
                                     files=data, params=params, auth=(CLIENT_ID, CLIENT_SECRET)).json()

            keywords = [key["keyword"] for key in resp["keywords"]]

            print("#######################################")
            print("#######################################")
            print(keywords)
            print(f"{image} saved")
            print("#######################################")

            return render_template("prepare_export.html", keywords=keywords, form=form)

    else:
        return render_template("image_upload.html", form=form)


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = ImageUploadForm()

#     if form.validate_on_submit():

#         filename = images.save(form.image.data)
#         return f'Filename: { filename }'

#     return render_template('index.html', form=form)
