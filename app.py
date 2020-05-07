from flask import Flask, request, render_template, redirect
import requests
from secrets import client_id, client_secret

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'


@app.route("/", methods=["GET", "POST"])
def home():
    """Home Page"""
    if request.method == "POST":

        image = request.form["image"]

        params = {'url': image, 'num_keywords': 50}

        data = requests.get('https://api.everypixel.com/v1/keywords',
                            params=params, auth=(client_id, client_secret)).json()

        keywords = [key['keyword'] for key in data["keywords"]]

        return render_template("results.html", keywords=keywords)

    else:
        return render_template("index.html")
