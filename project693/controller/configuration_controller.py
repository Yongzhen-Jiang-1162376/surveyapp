from flask import request, render_template, redirect, url_for, session, flash
from project693.controller import app
from project693.utils.session_manager import SessionManager
from project693.dao.configuration_dao import ConfigurationDAO
from project693.dao.survey_dao import SurveyDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer
import uuid
from datetime import datetime


@app.route("/siteadmin/configuration", methods=["GET", "POST"])
def configuration():
    """
    Controller to update site configuration settings
    """
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.CONFIGURATION.value
    )
    
    configuration_dao = ConfigurationDAO()
    
    if request.method == "POST":
        num_pairs = int(request.form.get("number_of_image_pairs"))
        
        if num_pairs < 1:
            flash("Number of image pairs must greater than zero.", "error")
            return redirect(url_for("configuration"))
        
        configuration_dao.update_configurtion(num_pairs)
        flash("Configuration updated successfully!", "success")
        return redirect(url_for("configuration"))
    
    config = configuration_dao.get_configuration()
    number_of_image_pairs = config.number_of_image_pairs if config else 10
    return render_template("admin/configuration.html", number_of_image_pairs=number_of_image_pairs)
