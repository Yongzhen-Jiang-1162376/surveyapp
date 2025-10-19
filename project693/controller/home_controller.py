from flask import render_template
from datetime import datetime
import platform
from flask import session
from project693.controller import app
from project693.utils.session_manager import SessionManager
from project693.dao.survey_dao import SurveyDAO


def format_date(date_obj):
    return date_obj.strftime("%d %b %Y").lstrip("0")


@app.route("/home/", methods=["GET"])
def site_home():
    """
    Controller for home page
    """
    SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.SITEHOME.value)
    
    survey_dao = SurveyDAO()
    result = survey_dao.active_survey_cycle_existed()
    
    # if there is not current active survey cycle available, then start a new survey
    # fallback for a new start of our application when the database is empty
    if result[0][0] == 0:
        survey_dao.start_survey_cyle()
    
    return render_template("site_home.html")
