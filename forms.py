from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Optional, Email, Length

SS_CHOICES = [(1, "Abstract"),
              (2, "Animals/Wildlife"),
              (3, "Arts"),
              (4, "Backgrounds/Textures"),
              (5, "Beauty/Fashion"),
              (6, "Buildings/Landmarks"),
              (7, "Business/Finance"),
              (8, "Celebrities"),
              (9, "Education"),
              (10, "Food and Drink"),
              (11, "Healthcare/Medical"),
              (12, "Holidays"),
              (13, "Industrial"),
              (14, "Interiors"),
              (15, "Miscellaneous"),
              (16, "Nature"),
              (17, "Objects"),
              (18, "Parks/Outdoor"),
              (19, "People"),
              (20, "Religion"),
              (21, "Science"),
              (22, "Signs/Symbols"),
              (23, "Sports/Recreation"),
              (24, "Technology"),
              (25, "Transportation"),
              (26, "Vintage")]


class ShutterStockForm(FlaskForm):
    """Form for Shutterstock CSV template."""

    filename = StringField("Filename", validators=[InputRequired()])
    description = TextAreaField(
        "Description", validators=[InputRequired(), Length(max=200, message="Description must be less than 200 characters")])
    keywords = TextAreaField("Keywords")
    category1 = SelectField(
        "Category 1", choices=SS_CHOICES, validators=[InputRequired()])
    category2 = SelectField("Category 2(Optional)",
                            choices=SS_CHOICES, validators=[Optional()])
    editorial = BooleanField("Editorial", validators=[Optional()])
    r_rated = BooleanField("R-Rated", validators=[Optional()])
    location = StringField("Location(Optional)", validators=[Optional()])
