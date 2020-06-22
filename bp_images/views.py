# Third-party libraries
from flask import Flask, request, redirect, render_template, flash, g, session, Blueprint

# Internal imports
from forms import ShutterStockForm
from models import db, Image
from bp_auth.views import TEMP_USER_IMAGES

bp_images = Blueprint("bp_images", __name__, template_folder="templates")

##################################################################
#   IMAGE ROUTES   ----------------------------------------------#
##################################################################


@bp_images.route("/", methods=["GET"])
def get_images():
    """Displays a list of all images"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    images = Image.query.filter(Image.user_id == g.user.id).all()

    return render_template("images.html", images=images)


@bp_images.route("/edit", methods=["GET"])
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

    return render_template("edit-images.html", form=form, images=images)
