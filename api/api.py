# Python standard libraries
import json
import io
import os

# Third-party libraries
from flask import Flask, request, redirect, jsonify, flash, url_for, g, session, Blueprint
from imagekitio import ImageKit

# Internal imports
from models import db, User, Image
from bp_auth.views import do_logout

api = Blueprint("api", __name__)

# # Image Kit API
imagekit = ImageKit(
    private_key=os.getenv('IMG_KIT_PRIVATE_KEY'),
    public_key=os.getenv('IMG_KIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMG_KIT_URL_ENDPOINT'))

##################################################################
#   API ROUTES   ------------------------------------------------#
##################################################################


@api.route("/users/delete", methods=["DELETE"])
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


@api.route("/delete/all", methods=["DELETE"])
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

    db.session.commit()

    flash("Removed all images", "success")
    print("Removed all images", delete)
    return jsonify(message="Deleted all images")


@api.route("/delete/<file_id>", methods=["DELETE"])
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


@api.route("/update", methods=["PATCH"])
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
