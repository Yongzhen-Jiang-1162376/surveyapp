from flask import request, render_template, redirect, url_for, flash, session
from project693.controller import app
from project693.dao.user_dao import UserDao
from project693.model import User
from werkzeug.utils import secure_filename
from project693.utils.hash_utils import get_password_hash, check_password_hash
from project693.utils.session_manager import SessionManager
from flask import jsonify
import os
import json


# Configure the file upload folder
app.config["UPLOAD_FOLDER"] = "project693/static/img/"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/siteadmin/profile/", methods=["GET", "POST"])
def profile():
    """
    function to display user profile page
    """
    user_id = session["user_id"]
    user_dao = UserDao()
    user = user_dao.get_full_user_info(user_id)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.USER_PROFILE.value
    )
    return render_template("user/profile.html", user=user)



@app.route("/siteadmin/update_profile_image/", methods=["POST"])
def update_profile_image():
    """
    function to update user profile image
    """
    user_id = session["user_id"]
    user_dao = UserDao()
    user = user_dao.find_by_id(user_id)
    file = request.files.get("profile_image")
    
    if file and file.filename != "" and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        user.avatar = filename
        user_dao.update_user(user)
        flash("Profile image updated successfully!", "success")
        return redirect(url_for("update_profile"))
    else:
        flash("No file selected or invalid file type.", "warning")
        return redirect(url_for("update_profile"))


@app.route("/siteadmin/update_profile/", methods=["GET", "POST"])
def update_profile():
    """
    function to dislay and update user profile
    """
    user_id = session["user_id"]
    user_dao = UserDao()
    user = user_dao.find_by_id(user_id)

    if request.method == "POST":
        # Handle profile image update
        if "profile_image" in request.files:
            file = request.files["profile_image"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                user.avatar = filename
                user_dao.update_user(user)
                flash("Profile image updated successfully!")
                return redirect(url_for("update_profile"))

        updated_email = request.form.get("email")
        updated_first_name = request.form.get("first_name")
        updated_last_name = request.form.get("last_name")
        updated_description = request.form.get("description")
        lat_value = request.form.get("lat")
        lon_value = request.form.get("lon")

        # Validate lat/lon
        if not user.location and (not lat_value or not lon_value):
            flash("Latitude and longitude values are required.", "warning")
            return redirect(url_for("update_profile"))
        
        if lat_value and lon_value:
            try:
                updated_lat = round(float(lat_value), 2)
                updated_lon = round(float(lon_value), 2)
                user.location = json.dumps({"lat": updated_lat, "lon": updated_lon})
            except ValueError:
                flash("Invalid latitude or longitude values. Please enter valid numbers.")
                return redirect(url_for("update_profile"))

        # Check and update email
        if updated_email:
            existing_user = user_dao.find_by_email(updated_email)
            if existing_user and existing_user.id != user_id:
                flash("Email already exists. Please use a different email.")
                return redirect(url_for("update_profile"))

        # Update the rest
        user.email = updated_email
        user.first_name = updated_first_name
        user.last_name = updated_last_name
        user.description = updated_description
        user_dao.update_user(user)

        flash("Profile updated successfully!")
        return redirect(url_for("profile"))

    return render_template("user/update_profile.html", user=user)