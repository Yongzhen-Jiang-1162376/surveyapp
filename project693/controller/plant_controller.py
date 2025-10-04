from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.utils.session_manager import SessionManager
import os, uuid, json


app.config["UPLOAD_FOLDER"] = os.path.abspath(
    os.path.join(app.root_path, "..", "static", "img")
)
app.config["ALLOWED_EXTENSIONS"] = {"jpg", "jpeg", "png", "gif"}

plant_dao = PlantDAO()

# Ensure upload folder exists
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/siteadmin/list_plants", methods=["GET"])
def list_plants():
    keyword = request.args.get("search", "")
    plants = plant_dao.search_plants(keyword)
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.LISTPLANTS.value
    )

    return render_template(
        "admin/plant_list.html", plants=plants
    )


@app.route("/siteadmin/add_plants", methods=["GET", "POST"])
def add_plant():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.ADDPLANT.value
    )

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        invasiveness = request.form.get("invasiveness")
        file = request.files.get("image")
        # image_filename = "default.png"
        
        if not name:
            flash("Please input a name for this plant", "error")
            return render_template("admin/add_plant.html")
        
        if not description:
            flash("Please input a description for this plant", "error")
            return render_template("admin/add_plant.html")

        if not invasiveness:
            flash("Please select an invasiveness for this plant", "error")
            return render_template("admin/add_plant.html")
        
        if not file or file.filename == "":
            flash("Please select an image for this plant", "error")
            return render_template("admin/add_plant.html")
        
        if not allowed_file(file.filename):
            flash("Image format only supports jpg/jpeg/png/gif", "error")
            return render_template("admin/add_plant.html")
        
        ext = os.path.splitext(file.filename)[1]
        image_filename = f"{uuid.uuid4()}{ext}"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        file.save(image_path)
        
        plant_dao.add_plant(name, description, image_filename, invasiveness)
        flash("New Plant added successfully!", "success")
        return redirect(url_for("list_plants"))
    return render_template("admin/add_plant.html")


@app.route("/siteadmin/edit_plant/<int:id>", methods=["GET", "POST"])
def edit_plant(id):
    
    plant = plant_dao.get_plant_by_id(id)
    
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]     
        invasiveness = request.form["invasiveness"]
        file = request.files.get("image")
        
        if not name:
            flash("Please input a name for this plant", "error")
            return render_template("admin/edit_plant.html", plant=plant)
        
        if not description:
            flash("Please input a description for this plant", "error")
            return render_template("admin/edit_plant.html", plant=plant)

        if not invasiveness:
            flash("Please select an invasiveness for this plant", "error")
            return render_template("admin/edit_plant.html", plant=plant)
        
        # if not file or file.filename == "":
        #     flash("Please select an image for this plant", "error")
        #     return render_template("admin/add_plant.html")
        
        if file and file.filename != "":
            
            if not allowed_file(file.filename):
                flash("Image format only supports jpg/jpeg/png/gif", "error")
                return render_template("admin/edit_plant.html", plant=plant)
            
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            file = filename
        else:
            file = plant.image
            
        plant_dao.edit_plant(id, name, invasiveness, description, file)
        flash("Plant edited successfully!", "success")
        return redirect(url_for("list_plants"))
    
    return render_template("admin/edit_plant.html", plant=plant)


@app.route("/siteadmin/delete_plants/<int:id>", methods=["POST"])
def delete_plant(id):
    
    plant = plant_dao.get_plant_by_id(id)
    if not plant:
        flash("Plant not found.", "error")
        return redirect(url_for("list_plants"))
    
    if plant.image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], plant.image)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                flash(f"Could not delete image file: {e}", "warning")
        
    
    plant_dao.delete_plant(id)
    flash("Plant deleted successfully!", "success")
    return redirect(url_for("list_plants"))
