# Third-party libraries
from flask import Flask, request, render_template, redirect, flash, url_for, session, Blueprint
from sqlalchemy.exc import IntegrityError

# Internal imports
from forms import UserAddForm, LoginForm
from models import db, User
# from utils import do_logout, do_login

CURR_USER_KEY = "curr_user"
TEMP_USER_IMAGES = "temp_user_images"

bp_auth = Blueprint("bp_auth", __name__, template_folder="templates")

##################################################################
#   User signup/login/logout   ----------------------------------#
##################################################################


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

##################################################################
#   USER ROUTES signup/login/logout    --------------------------#
##################################################################


@bp_auth.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if request.method == "POST":
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username/E-mail already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@bp_auth.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if request.method == "POST":
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(url_for('home'))

        flash("Invalid credentials", 'danger')

    return render_template('login.html', form=form)


@bp_auth.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("You have logged out successfully", "success")
    return redirect(url_for('home'))
