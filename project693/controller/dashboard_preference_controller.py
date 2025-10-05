from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.analysis_dao import AnalysisDAO
from project693.dao.survey_dao import SurveyDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select, NumeralTickFormatter, FactorRange, LabelSet
from bokeh.resources import CDN
from bokeh.transform import factor_cmap, dodge
import pandas as pd


@app.route("/dashboard/analysis-preference/", methods=["GET"])
def choices_by_preference():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )
    
    survey_dao = SurveyDAO()
    
    r_sum = survey_dao.get_survey_preference_summary()
    r1_sum = survey_dao.get_survey_preference_statistics('Dominant Flower Colour')
    r2_sum = survey_dao.get_survey_preference_statistics('Contrasting Colours')
    r3_sum = survey_dao.get_survey_preference_statistics('Flower Shape')
    r4_sum = survey_dao.get_survey_preference_statistics('Familiarity')
    r5_sum = survey_dao.get_survey_preference_statistics('Different From Most Plant You Know')
    
    data = []
    
    r1 = {
        'preference': r1_sum[0],
        'overall': {
            'percent': round(r_sum[0] * 100, 2),
            'count': r_sum[1]
        },
        'age_18_29': {
            'percent': round(r1_sum[1] * 100, 2),
            'count': r1_sum[2]
        },
        'age_30_49': {
            'percent': round(r1_sum[3] * 100, 2),
            'count': r1_sum[4]
        },
        'age_50_64': {
            'percent': round(r1_sum[5] * 100, 2),
            'count': r1_sum[6]
        },
        'age_65_plus': {
            'percent': round(r1_sum[7] * 100, 2),
            'count': r1_sum[8]
        },
        'gardener': {
            'percent': round(r1_sum[9] * 100, 2),
            'count': r1_sum[10]
        },
        'non_gardener': {
            'percent': round(r1_sum[11] * 100, 2),
            'count': r1_sum[12]
        },
    }
    
    r2 = {
        'preference': r2_sum[0],
        'overall': {
            'percent': round(r_sum[2] * 100, 2),
            'count': r_sum[3]
        },
        'age_18_29': {
            'percent': round(r2_sum[1] * 100, 2),
            'count': r2_sum[2]
        },
        'age_30_49': {
            'percent': round(r2_sum[3] * 100, 2),
            'count': r2_sum[4]
        },
        'age_50_64': {
            'percent': round(r2_sum[5] * 100, 2),
            'count': r2_sum[6]
        },
        'age_65_plus': {
            'percent': round(r2_sum[7] * 100, 2),
            'count': r2_sum[8]
        },
        'gardener': {
            'percent': round(r2_sum[9] * 100, 2),
            'count': r2_sum[10]
        },
        'non_gardener': {
            'percent': round(r2_sum[11] * 100, 2),
            'count': r2_sum[12]
        },
    }
    
    r3 = {
        'preference': r3_sum[0],
        'overall': {
            'percent': round(r_sum[4] * 100, 2),
            'count': r_sum[5]
        },
        'age_18_29': {
            'percent': round(r3_sum[1] * 100, 2),
            'count': r3_sum[2]
        },
        'age_30_49': {
            'percent': round(r3_sum[3] * 100, 2),
            'count': r3_sum[4]
        },
        'age_50_64': {
            'percent': round(r3_sum[5] * 100, 2),
            'count': r3_sum[6]
        },
        'age_65_plus': {
            'percent': round(r3_sum[7] * 100, 2),
            'count': r3_sum[8]
        },
        'gardener': {
            'percent': round(r3_sum[9] * 100, 2),
            'count': r3_sum[10]
        },
        'non_gardener': {
            'percent': round(r3_sum[11] * 100, 2),
            'count': r3_sum[12]
        },
    }
    
    r4 = {
        'preference': r4_sum[0],
        'overall': {
            'percent': round(r_sum[6] * 100, 2),
            'count': r_sum[7]
        },
        'age_18_29': {
            'percent': round(r4_sum[1] * 100, 2),
            'count': r4_sum[2]
        },
        'age_30_49': {
            'percent': round(r4_sum[3] * 100, 2),
            'count': r4_sum[4]
        },
        'age_50_64': {
            'percent': round(r4_sum[5] * 100, 2),
            'count': r4_sum[6]
        },
        'age_65_plus': {
            'percent': round(r4_sum[7] * 100, 2),
            'count': r4_sum[8]
        },
        'gardener': {
            'percent': round(r4_sum[9] * 100, 2),
            'count': r4_sum[10]
        },
        'non_gardener': {
            'percent': round(r4_sum[11] * 100, 2),
            'count': r4_sum[12]
        },
    }
    
    r5 = {
        'preference': r5_sum[0],
        'overall': {
            'percent': round(r_sum[8] * 100, 2),
            'count': r_sum[9]
        },
        'age_18_29': {
            'percent': round(r5_sum[1] * 100, 2),
            'count': r5_sum[2]
        },
        'age_30_49': {
            'percent': round(r5_sum[3] * 100, 2),
            'count': r5_sum[4]
        },
        'age_50_64': {
            'percent': round(r5_sum[5] * 100, 2),
            'count': r5_sum[6]
        },
        'age_65_plus': {
            'percent': round(r5_sum[7] * 100, 2),
            'count': r5_sum[8]
        },
        'gardener': {
            'percent': round(r5_sum[9] * 100, 2),
            'count': r5_sum[10]
        },
        'non_gardener': {
            'percent': round(r5_sum[11] * 100, 2),
            'count': r5_sum[12]
        },
    }
    
    data.append(r1)
    data.append(r2)
    data.append(r3)
    data.append(r4)
    data.append(r5)
   
    return render_template("dashboard/dashboard_preference.html", data=data, current_page="preference")
