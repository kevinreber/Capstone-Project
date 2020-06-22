# Google Cloud Vision
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import vision_v1
from google.cloud.vision_v1 import enums

# Python standard libraries
import json
import io
import os
import requests
import base64

# Third-party libraries
from flask import Flask, request
from imagekitio import ImageKit

# Internal imports
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
BASE_URL = os.environ.get('BASE_URL')
UPLOADED_PHOTOS_DEST = os.getcwd() + '/static/uploads'

# # Image Kit API
imagekit = ImageKit(
    private_key=os.getenv('IMG_KIT_PRIVATE_KEY'),
    public_key=os.getenv('IMG_KIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMG_KIT_URL_ENDPOINT'))

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
        resp = requests.post(BASE_URL, files=data, params=params, auth=(
            CLIENT_ID, CLIENT_SECRET)).json()

    # store response keywords
    keywords = [key["keyword"] for key in resp["keywords"]]

    return keywords

##################################################################
#   UPLOAD PAGE HELPER FUNCTIONS  -------------------------------#
##################################################################


def save_file(file, filename):
    """Saves file to uploads folder"""

    file.save(os.path.join(
        UPLOADED_PHOTOS_DEST, filename))
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
