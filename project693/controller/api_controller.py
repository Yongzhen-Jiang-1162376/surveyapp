from flask import request, render_template, redirect, url_for, session, flash, jsonify
from project693.controller import app
from project693.utils.session_manager import SessionManager
from project693.dao.plant_dao import PlantDAO
from project693.dao.survey_dao import SurveyDAO
from project693.dao.analysis_dao import AnalysisDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer
import uuid
from datetime import datetime


analysis_dao = AnalysisDAO()


@app.route("/api/current-survey-data", methods=["POST"])
def get_survey_data():
    # page = int(request.args.get("page", 1))
    # limit = int(request.args.get("limit", 10))
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))
    
    offset = (page - 1) * limit
    
    total = analysis_dao.get_current_total_survey_results()
    rows = analysis_dao.list_current_survey_results_with_plant_name_paginated(limit, offset)
    
    columns = [
        'session_id',
        'question_seq',
        'submission_time',
        'response_time',
        'invasive_plant_id',
        'invasive_plant_name',
        'non_invasive_plant_id',
        'non_invasive_plant_name',
        'selected_plant_id',
        'selected_plant_name',
        'has_garden',
        'age_group',
        'reasoning',
        'invasive_win'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]
    
    return jsonify({
        "datatable": datatable,
        "total": total
    })


@app.route("/api/all-current-survey-data", methods=["POST"])
def get_all_survey_data():
    
    rows = analysis_dao.list_all_current_survey_results_with_plant_name()
    
    columns = [
        'session_id',
        'question_seq',
        'submission_time',
        'response_time',
        'invasive_plant_id',
        'invasive_plant_name',
        'non_invasive_plant_id',
        'non_invasive_plant_name',
        'selected_plant_id',
        'selected_plant_name',
        'has_garden',
        'age_group',
        'reasoning',
        'invasive_win'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]
    
    return jsonify({
        "datatable": datatable
    })


@app.route("/api/current-beta-vs-win-percentage", methods=["POST"])
def get_current_beta_vs_win_percentage_data():
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))
    
    offset = (page - 1) * limit
    
    total = analysis_dao.get_current_total_survey_results()
    rows = analysis_dao.list_current_survey_results_with_plant_name_paginated(limit, offset)
    
    columns = [
        'session_id',
        'question_seq',
        'submission_time',
        'response_time',
        'invasive_plant_id',
        'invasive_plant_name',
        'non_invasive_plant_id',
        'non_invasive_plant_name',
        'selected_plant_id',
        'selected_plant_name',
        'has_garden',
        'age_group',
        'reasoning',
        'invasive_win'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]
    
    return jsonify({
        "datatable": datatable,
        "total": total
    })