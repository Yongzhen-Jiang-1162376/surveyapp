from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.utils.session_manager import SessionManager
import os, uuid, json
from project693.data.mockdata import dall_e_2_images_variations


@app.route("/misc/image_variations", methods=["GET"])
def list_image_variations():
    """
    Controller to list image variations
    Because AI-generated images are still not suitable for our project
    This function is using for testing only and not used for production
    """
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.LIST_IMAGE_VARIATIONS.value
    )

    return render_template(
        "misc/image_variations.html", images=dall_e_2_images_variations
    )
