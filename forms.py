from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextField, BooleanField, FileField
from wtforms.validators import InputRequired, Optional, Email, Length, Regexp
from form_choices import SS_CHOICES, SS_CHOICES_DICT


class ShutterStockForm(FlaskForm):
    """Form for Shutterstock CSV template."""

    filename = StringField("Filename", validators=[InputRequired()])
    description = TextField(
        "Description", validators=[InputRequired(), Length(max=200, message="Description must be less than 200 characters")])
    keywords = TextField("Keywords", validators=[Length(
        max=50, message="You can have no more than 50 tags"), Optional()])
    category1 = SelectField(
        "Category 1", choices=SS_CHOICES_DICT, validators=[InputRequired()])
    category2 = SelectField("Category 2(Optional)",
                            choices=SS_CHOICES_DICT, validators=[Optional()])
    editorial = BooleanField("Editorial", validators=[Optional()])
    r_rated = BooleanField("R-Rated", validators=[Optional()])
    location = StringField("Location(Optional)", validators=[Optional()])
