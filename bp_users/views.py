# Third-party libraries
from flask import Flask, redirect, render_template, flash, g, url_for, session, Blueprint

# Internal imports
from forms import UserForm
from models import db

bp_users = Blueprint("bp_users", __name__)

##################################################################
#   USER ROUTES     ---------------------------------------------#
##################################################################


@bp_users.route("/edit", methods=["GET", "POST"])
def user_profile():
    """User can edit their information"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect(url_for("home"))

    user = g.user
    form = UserForm(obj=user)

    if form.validate_on_submit():

        user.username = form.username.data
        user.email = form.email.data

        db.session.commit()
        flash("User updated!", "success")
        return redirect(url_for("bp_users.user_profile"))

    return render_template("info.html", form=form)
