# Utils Functions
from bp_upload.utils import detect_labels, get_keywords, save_file, clear_uploads, parse_keywords, upload_file

# Python standard libraries
import os

# Third-party libraries
from flask import Flask, request, render_template, flash, g, session, Blueprint
from imagekitio import ImageKit
from werkzeug.utils import secure_filename

# Internal imports
from models import db, Image
from bp_auth.views import TEMP_USER_IMAGES
UPLOADED_PHOTOS_DEST = os.getcwd() + '/static/uploads'

# # Image Kit API
imagekit = ImageKit(
    private_key=os.getenv('IMG_KIT_PRIVATE_KEY'),
    public_key=os.getenv('IMG_KIT_PUBLIC_KEY'),
    url_endpoint=os.getenv('IMG_KIT_URL_ENDPOINT'))

bp_upload = Blueprint("bp_upload", __name__)

##################################################################
#   UPLOAD PAGE   -----------------------------------------------#
##################################################################


@bp_upload.route("/upload", methods=["GET", "POST"])
def upload():
    """Upload Page"""

    # Make sure to clear any images already existing in session
    if TEMP_USER_IMAGES in session and len(session[TEMP_USER_IMAGES]) != 0:
        del_img = session[TEMP_USER_IMAGES][0]

        # Delete from ImageKit.io
        delete = imagekit.delete_file(del_img["id"])
        print("Image removed", delete)

    session[TEMP_USER_IMAGES] = []

    # list to hold our uploaded image urls
    temp_urls = session[TEMP_USER_IMAGES]

    if request.method == "POST":
        """File will be returned as a FileStorage"""

        if request.files:
            file = request.files["file"]

            # secure filename
            filename = secure_filename(file.filename)

            # save file to 'upload' folder
            save_file(file, filename)

            # Get file path
            file_path = os.path.join(UPLOADED_PHOTOS_DEST, filename)

            # Upload file to image host
            u_resp = upload_file(file_path, filename)

            # Get keywords from response
            #  ! Use test keywords to avoid exceeding ratelimit of 100 per day
            # Google keywords
            g_keywords = detect_labels(file_path)
            # Everypixel keywords
            e_keywords = get_keywords(file_path, 5)
            keywords = g_keywords + e_keywords

            # Test keywords below
            # keywords = [u"Cool", u"Interesting", u"Amazing",
            #             u"Pythonic", u"Flasky", u"Eye Dropping", u"tags", u"new", u"html", u"css", u"max", u"sunset"]

            parsed_keywords = parse_keywords(keywords)

            if not g.user:

                image = {
                    "id": u_resp["fileId"],
                    "filename": u_resp["name"],
                    "thumbnail_url": u_resp["thumbnailUrl"],
                    "keywords": parsed_keywords,
                    "description": "",
                    "category1": "",
                    "category2": "",
                    "location": "",
                    "editorial": False,
                    "r_rated": False
                }

                temp_urls.append(image)
                session[TEMP_USER_IMAGES] = temp_urls

            else:
                new_file = Image(id=u_resp["fileId"],
                                 user_id=g.user.id,
                                 filename=u_resp["name"],
                                 url=u_resp["url"],
                                 thumbnail_url=u_resp["thumbnailUrl"],
                                 keywords=parsed_keywords)

                db.session.add(new_file)
                db.session.commit()

        # Delete image from upload directory after saving image to DB
        clear_uploads(file_path)

        flash("Images saved", "success")
        flash("Keywords Added", "success")
        print(u_resp)
        return "uploading..."

    else:
        return render_template("upload.html")
