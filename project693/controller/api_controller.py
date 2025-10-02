from flask import request, render_template, redirect, url_for, session, flash, jsonify
from project693.controller import app
from project693.utils.session_manager import SessionManager
from project693.dao.plant_dao import PlantDAO
from project693.dao.survey_dao import SurveyDAO
from project693.dao.analysis_dao import AnalysisDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer
import uuid
from datetime import datetime
from project693.core.analysis_calculation import save_survey_cycle_analysis_data
from flask import send_file
from io import BytesIO, StringIO
import csv
import zipfile
from openai import OpenAI
import os
import html


analysis_dao = AnalysisDAO()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@app.route("/api/current-survey-data", methods=["POST"])
def get_survey_data():
    # page = int(request.args.get("page", 1))
    # limit = int(request.args.get("limit", 10))
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))

    offset = (page - 1) * limit

    total = analysis_dao.get_current_total_survey_results()
    rows = analysis_dao.list_current_survey_results_with_plant_name_paginated(
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
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
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


@app.route("/api/current-beta-vs-win-percentage", methods=["POST"])
def get_current_beta_vs_win_percentage_data():
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))

    offset = (page - 1) * limit

    total = analysis_dao.get_current_total_survey_results()
    rows = analysis_dao.list_current_survey_results_with_plant_name_paginated(
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


@app.route("/api/survey-cycle-data", methods=["POST"])
def get_survey_cycle_data():
    req = request.get_json()
    page = int(req.get("page", 1))
    limit = int(req.get("limit", 10))

    offset = (page - 1) * limit

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


@app.route("/api/close-survey", methods=["POST"])
def close_survey():

    survey_dao = SurveyDAO()

    active_survey_result = survey_dao.active_survey_result_existed()

    if not active_survey_result:
        return jsonify({
            'success': False,
            'message': 'No survey results in this cycle.\nPlease fill out some surveys.'
        }), 404

    # save analysis data for current survey cycle
    save_survey_cycle_analysis_data()

    survey_dao.start_survey_cyle()

    return jsonify({
        'success': True,
        'message': 'Survey cycle closed successfully.\nA new suvey cycle is started.'
    })


@app.route("/api/beta-score-by-invasive-type-histogram-by-cycle-id", methods=["POST"])
def get_beta_score_by_invasive_type_histogram_by_cycle_id():
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
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
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
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
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
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
    req = request.get_json()
    cycle_id = int(req.get("cycle_id", 1))
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


@app.route("/survey/plant-info")
def plant_info():
    plant_name = request.args.get("name")

    prompt = f"Provide a short, informative description of the plant '{plant_name}' including whether it is invasive, within 2-3 paragraphs. Use **bold** for important words."

    # Use the Responses API
    response = client.responses.create(
        # model="gpt-5-nano",
        model="gpt-4.1-nano",
        input=[
            {"role": "system", "content": "You are a helpful botanist assistant."},
            {"role": "user", "content": prompt}
        ],
        text={
            "format": {
                "type": "text"
            }
        },
        max_output_tokens=5000
    )

    description = response.output_text or "No description available from this model."
    
    description = html.unescape(description)

    return jsonify({"description": description})


@app.route("/api/survey-cycle-detail", methods=["POST"])
def survey_cycle_detail_by_cycle_id():
    req = request.get_json()
    cycle_id = int(req.get("cycle_id"))
    
    survey_dao = SurveyDAO()
    
    datatable = survey_dao.list_survey_cycle_detail_data(cycle_id)
    
    return jsonify({ "datatable": datatable })


@app.route("/api/delete-survey-choice-by-id", methods=['POST'])
def delete_survey_choice_by_id():
    req = request.get_json()
    survey_id = int(req.get("id"))
    
    survey_dao = SurveyDAO()
    survey_dao.delete_survey_choice_by_id(survey_id)
    
    return jsonify({ "success": True }), 200


@app.route("/api/delete-survey-cycle-by-id", methods=['POST'])
def delete_survey_cycle_by_id():
    req = request.get_json()
    cycle_id = int(req.get("cycle_id"))
    
    survey_dao = SurveyDAO()
    survey_dao.delete_survey_cycle_by_id(cycle_id)
    
    return jsonify({ "success": True }), 200
