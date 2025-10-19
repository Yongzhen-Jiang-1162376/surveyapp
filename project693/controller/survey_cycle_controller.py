from flask import request, render_template, redirect, url_for, session, flash
from project693.controller import app
from project693.utils.session_manager import SessionManager
from project693.dao.plant_dao import PlantDAO
from project693.dao.survey_dao import SurveyDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer
import uuid
from datetime import datetime


@app.route("/siteadmin/survey_cycle", methods=["GET"])
def survey_cycle():
    """
    Controller to display survey cycle
    """
    return render_template("admin/survey_cycle.html")
