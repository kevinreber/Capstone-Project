from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextField, BooleanField, PasswordField
from wtforms.validators import InputRequired, DataRequired, Optional, Email, Length, Regexp
from form_choices import SS_CHOICES


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class ShutterStockForm(FlaskForm):
    """Form for Shutterstock CSV template."""

    filename = StringField("Filename", validators=[InputRequired()])
    description = TextField(
        "Description", validators=[InputRequired(), Length(max=200, message="Description must be less than 200 characters")])
    keywords = TextField("Keywords", validators=[Length(
        max=50, message="You can have no more than 50 tags"), Optional()])
    category1 = SelectField(
        "Category 1", choices=SS_CHOICES, validators=[InputRequired()])
    category2 = SelectField("Category 2(Optional)",
                            choices=SS_CHOICES, validators=[Optional()])
    editorial = BooleanField("Editorial", validators=[Optional()])
    r_rated = BooleanField("R-Rated", validators=[Optional()])
    location = StringField("Location(Optional)", validators=[Optional()])
