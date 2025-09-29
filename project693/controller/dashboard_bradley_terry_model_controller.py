from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.dao.analysis_dao import AnalysisDAO
from project693.dao.survey_dao import SurveyDAO
from project693.utils.session_manager import SessionManager
from project693.core.analysis_calculation import (
    beta_vs_win_percentage,
    beta_vs_win_percentage_V2,
    beta_vs_win_percentage_datatable,
    beta_scores_by_image,
    beta_scores_by_image_V2,
    beta_score_by_plant_datatable,
    beta_scores_by_plant_type,
    beta_scores_by_plant_type_V2,
    beta_scores_by_plant_type_datatable,
    win_loss_by_image,
    win_loss_by_image_V2,
    win_loss_by_plant_datatable,
    beta_scores_heat_map,
    beta_scores_heat_map_V2,
    beta_score_heat_map_datatable,
    beta_scores_ranking,
    beta_scores_ranking_V2,
    initialize
)
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select, NumeralTickFormatter, LabelSet, Span
from bokeh.transform import dodge
from bokeh.resources import CDN
from scipy.optimize import minimize
import numpy as np
import pandas as pd

import random
from project693.data.mockdata import invasive_plants, non_invasive_plants, data, invasive_map




@app.route("/dashboard/bradley-terry-model", methods=["GET"])
def bradley_terry_model():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )
    
    # analysis_dao = AnalysisDAO()
    initialize()
    
    survey_dao = SurveyDAO()
    analysis_dao = AnalysisDAO()
    cycle_id = survey_dao.get_active_survey_cycle_id()
    
    
    # 1. win percentage vs beta scatter plot
    db_rows = analysis_dao.list_beta_score_win_percentage_by_cycle_id(cycle_id)
    win_percentage_beta_plot_uw = beta_vs_win_percentage_V2(db_rows, weighted=0)
    win_percentage_beta_plot_w = beta_vs_win_percentage_V2(db_rows, weighted=1)
    
    win_percentage_beta_uw_script, win_percentage_beta_uw_div = components(win_percentage_beta_plot_uw)
    win_percentage_beta_w_script, win_percentage_beta_w_div = components(win_percentage_beta_plot_w)
    
    rows = [
        {
            'plant_id': r[1],
            'plant': r[2],
            'invasiveness': r[3],
            'win_percentage_value': r[4],
            'win_percentage': str(round(r[4] * 100, 2)) + '%',
            'bt_beta_score': round(r[5], 4),
            'bt_beta_score_weighted': round(r[6], 4)
        }
        for r in db_rows
    ]
    
    # rows = beta_vs_win_percentage_datatable()
    beta_vs_win_percentage_dt = {
        'columns': list(rows[0].keys()),
        'rows': rows
    }
    
    # 2. barchart of beta scores by each image
    beta_scores_by_image_uw = beta_scores_by_image_V2(db_rows, weighted=0)
    beta_scores_by_image_w = beta_scores_by_image_V2(db_rows, weighted=1)
    
    beta_scores_by_image_uw_script, beta_scores_by_image_uw_div = components(beta_scores_by_image_uw)
    beta_scores_by_image_w_script, beta_scores_by_image_w_div = components(beta_scores_by_image_w)
    
    # rows = beta_score_by_plant_datatable()
    
    rows = [
        {
            'plant': r[2],
            'invasiveness': r[3],
            'bt_beta_score': round(r[5], 4),
            'bt_beta_score_weighted': round(r[6], 4)
        }
        for r in db_rows
    ]

    # datatable for downloading
    beta_score_by_plant_dt = {
        'columns': list(rows[0].keys()),
        'rows': rows
    }
    
    # 3. histogram of beta scores by plant type
    beta_scores_by_plant_type_uw = beta_scores_by_plant_type_V2(db_rows, weighted=0)
    beta_scores_by_plant_type_w = beta_scores_by_plant_type_V2(db_rows, weighted=1)
    
    beta_scores_by_plant_type_uw_script, beta_scores_by_plant_type_uw_div = components(beta_scores_by_plant_type_uw)
    beta_scores_by_plant_type_w_script, beta_scores_by_plant_type_w_div = components(beta_scores_by_plant_type_w)
    
    rows = beta_scores_by_plant_type_datatable()
    beta_scores_by_plant_type_dt = {
        'columns': list(rows[0].keys()),
        'rows': rows
    }
    
    
    # 4. wins/Losses bar chart
    win_loss_rows = analysis_dao.list_win_loss_by_plant_by_cycle_id(cycle_id)
    win_loss_by_image_uw = win_loss_by_image_V2(win_loss_rows, weighted=0)
    win_loss_by_image_w = win_loss_by_image_V2(win_loss_rows, weighted=1)
    
    win_loss_by_image_uw_script, win_loss_by_image_uw_div = components(win_loss_by_image_uw)
    win_loss_by_image_w_script, win_loss_by_image_w_div = components(win_loss_by_image_w)
    
    rows = win_loss_by_plant_datatable()
    
    win_loss_by_plant_dt = {
        'columns': list(rows[0].keys()),
        'rows': rows
    }
    
    # 5. heat map of beta scores
    beta_scores_heat_map_uw = beta_scores_heat_map_V2(db_rows, weighted=0)
    beta_scores_heat_map_w = beta_scores_heat_map_V2(db_rows, weighted=1)
    beta_scores_heat_map_by_image_uw_script, beta_scores_heat_map_by_image_uw_div = components(beta_scores_heat_map_uw)
    beta_scores_heat_map_by_image_w_script, beta_scores_heat_map_by_image_w_div = components(beta_scores_heat_map_w)
    
    rows = beta_score_heat_map_datatable()
    beta_score_heat_map_dt = {
        'columns': list(rows[0].keys()),
        'rows': rows
    }
    
    # 6. beta scores ranking
    beta_scores_ranking_uw = beta_scores_ranking_V2(db_rows, weighted=0)
    beta_scores_ranking_w = beta_scores_ranking_V2(db_rows, weighted=1)
    beta_scores_ranking_uw_script, beta_scores_ranking_uw_div = components(beta_scores_ranking_uw)
    beta_scores_ranking_w_script, beta_scores_ranking_w_div = components(beta_scores_ranking_w)
    
    # rows = beta_score_by_plant_datatable()
    
    rows = [
        {
            'plant': r[2],
            'invasiveness': r[3],
            'bt_beta_score': round(r[5], 4),
            'bt_beta_score_weighted': round(r[6], 4)
        }
        for r in db_rows
    ]
    
    rows = sorted(rows, key=lambda r: r['bt_beta_score'], reverse=True)
    beta_score_by_plant_ranking_dt = {
        'columns': list(rows[0].keys()),
        'rows': rows
    }
    
    plots = {
        'win_percentage_beta_uw_script': win_percentage_beta_uw_script,
        'win_percentage_beta_uw_div': win_percentage_beta_uw_div,
        'win_percentage_beta_w_script': win_percentage_beta_w_script,
        'win_percentage_beta_w_div': win_percentage_beta_w_div,
        
        'beta_scores_by_image_uw_script': beta_scores_by_image_uw_script,
        'beta_scores_by_image_uw_div': beta_scores_by_image_uw_div,
        'beta_scores_by_image_w_script': beta_scores_by_image_w_script,
        'beta_scores_by_image_w_div': beta_scores_by_image_w_div,
        
        'beta_scores_by_plant_type_uw_script': beta_scores_by_plant_type_uw_script,
        'beta_scores_by_plant_type_uw_div': beta_scores_by_plant_type_uw_div,
        'beta_scores_by_plant_type_w_script': beta_scores_by_plant_type_w_script,
        'beta_scores_by_plant_type_w_div': beta_scores_by_plant_type_w_div,
        
        'win_loss_by_image_uw_script': win_loss_by_image_uw_script,
        'win_loss_by_image_uw_div': win_loss_by_image_uw_div,
        'win_loss_by_image_w_script': win_loss_by_image_w_script,
        'win_loss_by_image_w_div': win_loss_by_image_w_div,
        
        'beta_scores_heat_map_by_image_uw_script': beta_scores_heat_map_by_image_uw_script,
        'beta_scores_heat_map_by_image_uw_div': beta_scores_heat_map_by_image_uw_div,
        'beta_scores_heat_map_by_image_w_script': beta_scores_heat_map_by_image_w_script,
        'beta_scores_heat_map_by_image_w_div': beta_scores_heat_map_by_image_w_div,
        
        'beta_scores_ranking_uw_script': beta_scores_ranking_uw_script,
        'beta_scores_ranking_uw_div': beta_scores_ranking_uw_div,
        'beta_scores_ranking_w_script': beta_scores_ranking_w_script,
        'beta_scores_ranking_w_div': beta_scores_ranking_w_div,
    }
    
    data = {
        'win_percentage_beta_datatable': beta_vs_win_percentage_dt,
        'beta_score_by_plant_datatable': beta_score_by_plant_dt,
        'beta_score_ranking_datatable': beta_score_by_plant_ranking_dt,
        'beta_score_by_plant_type_hist_datatable': beta_scores_by_plant_type_dt,
        'win_vs_loss_by_plant_datatable': win_loss_by_plant_dt,
        'beta_score_heat_map_datatable': beta_score_heat_map_dt
    }
    
    return render_template(
        "dashboard/dashboard_bradley_terry_model.html",
        current_page="bt_model",
        plots=plots,
        data=data
    )
