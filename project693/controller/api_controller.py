from flask import request, render_template, redirect, url_for, session, flash, jsonify
from project693.controller import app
from project693.utils.session_manager import SessionManager
from project693.dao.plant_dao import PlantDAO
from project693.dao.survey_dao import SurveyDAO
from project693.dao.analysis_dao import AnalysisDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer
import uuid
from datetime import datetime
from project693.core.analysis_calculation import (
    save_survey_cycle_analysis_data, 
    refresh_survey_cycle_analysis_data_by_cycle_id,
    save_overall_survey_cycle_analysis_data
)
from flask import send_file
from io import BytesIO, StringIO
import csv
import zipfile
from openai import OpenAI
import os
import html
from project693.utils.openai_utils import fetch_plant_info_from_openai


# analysis_dao = AnalysisDAO()
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@app.route("/api/all-survey-data", methods=["POST"])
def get_survey_data():
    """
    API controller to get all survey data
    """
    # page = int(request.args.get("page", 1))
    # limit = int(request.args.get("limit", 10))
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))

    offset = (page - 1) * limit
    
    analysis_dao = AnalysisDAO()

    total = analysis_dao.get_all_total_survey_results()
    rows = analysis_dao.list_all_survey_results_with_plant_name_paginated(
        limit, offset)

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
    """
    API controller to all current survey data
    """
    analysis_dao = AnalysisDAO()
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


@app.route("/api/all-survey-data-by-cycle-id", methods=["POST"])
def get_all_survey_data_by_cycle_id():
    """
    API controller to get survey data by cycle id
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
    
    analysis_dao = AnalysisDAO()
    rows = analysis_dao.list_all_survey_results_with_plant_name_by_cycle_id(
        cycle_id)

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


@app.route("/api/survey-meta-data-paginated", methods=["POST"])
def get_survey_meta_data_paginated():
    """
    API controller to get paginated survey meta data
    """
    # page = int(request.args.get("page", 1))
    # limit = int(request.args.get("limit", 10))
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))

    offset = (page - 1) * limit
    
    # analysis_dao = AnalysisDAO()
    survey_dao = SurveyDAO()

    total = survey_dao.get_all_survey_meta_data_count()
    rows = survey_dao.list_all_survey_meta_data_paginated(limit, offset)

    columns = [
        'session_id',
        'submission_time',
        'has_garden',
        'age_group',
        'preference'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable,
        "total": total
    })


@app.route("/api/all-survey-meta-data", methods=["POST"])
def get_all_survey_meta_data():
    """
    API controller to get all survey meta data
    """
    survey_dao = SurveyDAO()
    rows = survey_dao.list_all_survey_meta_data()

    columns = [
        'session_id',
        'submission_time',
        'has_garden',
        'age_group',
        'preference'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable
    })


@app.route("/api/survey-cycle-data", methods=["POST"])
def get_survey_cycle_data():
    """
    API controller to get all survey cycle data
    """
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))

    offset = (page - 1) * limit

    # analysis_dao = AnalysisDAO()
    survey_dao = SurveyDAO()
    total = survey_dao.get_total_survey_cycles()
    rows = survey_dao.list_survey_cycle_paginated(limit, offset)

    columns = [
        'cycle_id',
        'start_time',
        'end_time',
        'survey_participants',
        'total_choices',
        'status',
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable,
        "total": total
    })


@app.route("/api/survey-all-data", methods=["POST"])
def get_survey_all_data():
    """
    API controller to get all survey data
    """
    # req = request.get_json()
    # page = int(req.get("page", 1))
    # limit = int(req.get("limit", 10))

    # offset = (page - 1) * limit

    # analysis_dao = AnalysisDAO()
    survey_dao = SurveyDAO()
    # total = survey_dao.get_total_survey_cycles()
    rows = survey_dao.list_all_survey_summary()

    columns = [
        'survey_participants',
        'total_choices'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable
    })


@app.route("/api/close-survey", methods=["POST"])
def close_survey():
    """
    API controller to close survey
    """
    survey_dao = SurveyDAO()

    active_survey_result = survey_dao.active_survey_result_existed()

    if not active_survey_result:
        return jsonify({
            'success': False,
            'message': 'No survey results in this cycle.\nPlease fill out some surveys.'
        })

    # save analysis data for current survey cycle
    save_survey_cycle_analysis_data()

    survey_dao.start_survey_cyle()

    return jsonify({
        'success': True,
        'message': 'Survey cycle closed successfully.\nA new suvey cycle is started.'
    })


@app.route("/api/beta-score-by-invasive-type-histogram-by-cycle-id", methods=["POST"])
def get_beta_score_by_invasive_type_histogram_by_cycle_id():
    """
    API controller to get beta score by invasive type for histogram chart
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
    
    analysis_dao = AnalysisDAO()
    rows = analysis_dao.list_beta_score_by_invasive_type_histogram_by_cycle_id(
        cycle_id)

    columns = [
        'cycle_id',
        'bin_no',
        'bin_left',
        'bin_right',
        'invasive_count',
        'non_invasive_count',
        'bin_left_weighted',
        'bin_right_weighted',
        'invasive_count_weighted',
        'non_invasive_count_weighted'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable
    })


@app.route("/api/win-loss-by-plant-by-cycle-id", methods=["POST"])
def get_win_loss_by_plant_by_cycle_id():
    """
    API controller to get win loss by plant by cycle id
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
    
    analysis_dao = AnalysisDAO()
    rows = analysis_dao.list_win_loss_by_plant_by_cycle_id(cycle_id)

    columns = [
        'cycle_id',
        'plant_id',
        'plant_name',
        'invasiveness',
        'win',
        'loss'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable
    })


@app.route("/api/beta-score-heat-map-by-plant-by-cycle-id", methods=["POST"])
def get_beta_score_heat_map_by_plant_by_cycle_id():
    """
    API controller to get beta score heat map data by plant by cycle id
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
    
    analysis_dao = AnalysisDAO()
    rows = analysis_dao.list_beta_score_heat_map_by_plant_by_cycle_id(cycle_id)

    columns = [
        'cycle_id',
        'plant_a_id',
        'plant_a_name',
        'plant_b_id',
        'plant_b_name',
        'plant_a_beats_b',
        'plant_a_beats_b_weighted'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable
    })


@app.route("/api/beta-score-win-percentage-by-cycle-id", methods=["POST"])
def get_beta_score_win_percentage_by_cycle_id():
    """
    API controller to get beta score vs win percentage by cycle id
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
    
    analysis_dao = AnalysisDAO()
    rows = analysis_dao.list_beta_score_win_percentage_by_cycle_id(cycle_id)

    columns = [
        'cycle_id',
        'plant_id',
        'plant_name',
        'invasiveness',
        'win_percentage',
        'bt_beta_score',
        'bt_beta_score_weighted'
    ]
    datatable = [dict(zip(columns, row)) for row in rows]

    return jsonify({
        "datatable": datatable
    })


@app.route("/api/download-survey-cycle-data-by-cycle-id", methods=["POST"])
def download_survey_cycle_data_by_cycle_id():
    """
    API controller to download survey cycle data by cycle id
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))

    csv_data = {}

    def rows_to_csv(columns, rows):
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(zip(columns, row)))
        return output.getvalue()

    analysis_dao = AnalysisDAO()
    rows = analysis_dao.list_all_survey_results_with_plant_name_by_cycle_id(
        cycle_id)
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
    csv_data['survey_raw_data.csv'] = rows_to_csv(columns, rows)

    rows = analysis_dao.list_beta_score_by_invasive_type_histogram_by_cycle_id(
        cycle_id)
    columns = [
        'cycle_id',
        'bin_no',
        'bin_left',
        'bin_right',
        'invasive_count',
        'non_invasive_count',
        'bin_left_weighted',
        'bin_right_weighted',
        'invasive_count_weighted',
        'non_invasive_count_weighted'
    ]
    csv_data['beta_score_by_invasive_type_histogram.csv'] = rows_to_csv(
        columns, rows)

    rows = analysis_dao.list_beta_score_win_percentage_by_cycle_id(cycle_id)
    columns = [
        'cycle_id',
        'plant_id',
        'plant_name',
        'invasiveness',
        'win_percentage',
        'bt_beta_score',
        'bt_beta_score_weighted'
    ]
    csv_data['beta_score_with_win_percentage_by_plant.csv'] = rows_to_csv(
        columns, rows)

    rows = analysis_dao.list_beta_score_heat_map_by_plant_by_cycle_id(cycle_id)
    columns = [
        'cycle_id',
        'plant_a_id',
        'plant_a_name',
        'plant_b_id',
        'plant_b_name',
        'plant_a_beats_b',
        'plant_a_beats_b_weighted'
    ]
    csv_data['beta_score_heat_map_by_plant.csv'] = rows_to_csv(columns, rows)

    rows = analysis_dao.list_win_loss_by_plant_by_cycle_id(cycle_id)
    columns = [
        'cycle_id',
        'plant_id',
        'plant_name',
        'invasiveness',
        'win',
        'loss'
    ]
    csv_data['win_loss_by_plant.csv'] = rows_to_csv(columns, rows)

    # create ZIP in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in csv_data.items():
            zip_file.writestr(filename, content)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='survey_data.zip'
    )



@app.route("/api/download-all-survey-data", methods=["POST"])
def download_all_survey_data():
    """
    API controller to download all survey data
    """
    # req = request.get_json()
    # cycle_id = int(req.get("cycle_id", 1))

    csv_data = {}

    def rows_to_csv(columns, rows):
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(zip(columns, row)))
        return output.getvalue()

    analysis_dao = AnalysisDAO()
    rows = analysis_dao.list_all_survey_results_with_plant_name_by_cycle_id()
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
    csv_data['survey_raw_data.csv'] = rows_to_csv(columns, rows)

    rows = analysis_dao.list_beta_score_by_invasive_type_histogram_by_cycle_id(0)
    columns = [
        'cycle_id',
        'bin_no',
        'bin_left',
        'bin_right',
        'invasive_count',
        'non_invasive_count',
        'bin_left_weighted',
        'bin_right_weighted',
        'invasive_count_weighted',
        'non_invasive_count_weighted'
    ]
    csv_data['beta_score_by_invasive_type_histogram.csv'] = rows_to_csv(
        columns, rows)

    rows = analysis_dao.list_beta_score_win_percentage_by_cycle_id(0)
    columns = [
        'cycle_id',
        'plant_id',
        'plant_name',
        'invasiveness',
        'win_percentage',
        'bt_beta_score',
        'bt_beta_score_weighted'
    ]
    csv_data['beta_score_with_win_percentage_by_plant.csv'] = rows_to_csv(
        columns, rows)

    rows = analysis_dao.list_beta_score_heat_map_by_plant_by_cycle_id(0)
    columns = [
        'cycle_id',
        'plant_a_id',
        'plant_a_name',
        'plant_b_id',
        'plant_b_name',
        'plant_a_beats_b',
        'plant_a_beats_b_weighted'
    ]
    csv_data['beta_score_heat_map_by_plant.csv'] = rows_to_csv(columns, rows)

    rows = analysis_dao.list_win_loss_by_plant_by_cycle_id(0)
    columns = [
        'cycle_id',
        'plant_id',
        'plant_name',
        'invasiveness',
        'win',
        'loss'
    ]
    csv_data['win_loss_by_plant.csv'] = rows_to_csv(columns, rows)

    # create ZIP in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in csv_data.items():
            zip_file.writestr(filename, content)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='all_survey_data.zip'
    )


@app.route("/survey/plant-info")
def plant_info():
    """
    API controller to get plant description
    """
    plant_id = int(request.args.get("id"))
    
    plant_dao = PlantDAO()
    description = plant_dao.get_ai_intro_by_id(plant_id)
    
    if not description:
        description = "No description available for this plant"
    
    description = html.unescape(description)

    return jsonify({"description": description})


@app.route("/api/survey-cycle-detail", methods=["POST"])
def survey_cycle_detail_by_cycle_id():
    """
    API controller to get survey cycle detail
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id"))
    
    survey_dao = SurveyDAO()
    
    datatable = survey_dao.list_survey_cycle_detail_data(cycle_id)
    
    return jsonify({ "datatable": datatable })


@app.route("/api/delete-survey-choice-by-id", methods=['POST'])
def delete_survey_choice_by_id():
    """
    API controller to delete survey record by id
    """
    req = request.get_json()
    survey_id = int(req.get("id"))
    
    survey_dao = SurveyDAO()
    survey_dao.delete_survey_choice_by_id(survey_id)
    
    return jsonify({ "success": True }), 200


@app.route("/api/delete-survey-cycle-by-id", methods=['POST'])
def delete_survey_cycle_by_id():
    """
    API controller to delete survey cycle by cycle id
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id"))
    
    survey_dao = SurveyDAO()
    survey_dao.delete_survey_cycle_by_id(cycle_id)
    
    return jsonify({ "success": True }), 200


@app.route("/api/refresh-survey-cycle-by-id", methods=['POST'])
def refresh_survey_cycle_by_id():
    """
    API controller to recalculate survey cycle data
    """
    req = request.get_json()
    cycle_id = int(req.get("cycle_id"))
    
    refresh_survey_cycle_analysis_data_by_cycle_id(cycle_id)
    
    return jsonify({ "success": True }), 200

@app.route("/api/refresh-all-survey-data", methods=['POST'])
def refresh_all_survey_data():
    """
    API controller to recalculate all survey data
    """
    # req = request.get_json()
    # cycle_id = int(req.get("cycle_id"))
    
    save_overall_survey_cycle_analysis_data()
    
    return jsonify({ "success": True }), 200
