from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.dao.analysis_dao import AnalysisDAO
from project693.utils.session_manager import SessionManager
from project693.core.analysis_calculation import (
    beta_vs_win_percentage,
    beta_vs_win_percentage_datatable,
    beta_scores_by_image,
    beta_score_by_plant_datatable,
    beta_scores_by_plant_type,
    win_loss_by_image,
    beta_scores_heat_map,
    beta_scores_ranking
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

analysis_dao = AnalysisDAO()


@app.route("/dashboard/bradley-terry-model", methods=["GET"])
def bradley_terry_model():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )
    
    # 1. win percentage vs beta scatter plot
    win_percentage_beta_plot_uw = beta_vs_win_percentage(weighted=0)
    win_percentage_beta_plot_w = beta_vs_win_percentage(weighted=1)
    
    win_percentage_beta_uw_script, win_percentage_beta_uw_div = components(win_percentage_beta_plot_uw)
    win_percentage_beta_w_script, win_percentage_beta_w_div = components(win_percentage_beta_plot_w)
    
    win_percentage_beta_datatable = beta_vs_win_percentage_datatable()
    
    # 2. histogram of beta scores by each image
    beta_scores_by_image_uw = beta_scores_by_image(weighted=0)
    beta_scores_by_image_w = beta_scores_by_image(weighted=1)
    
    beta_scores_by_image_uw_script, beta_scores_by_image_uw_div = components(beta_scores_by_image_uw)
    beta_scores_by_image_w_script, beta_scores_by_image_w_div = components(beta_scores_by_image_w)
    
    beta_scores_by_plant_datatable = beta_score_by_plant_datatable()
    
    # 3. histogram of beta scores by plant type
    beta_scores_by_plant_type_uw = beta_scores_by_plant_type(weighted=0)
    beta_scores_by_plant_type_w = beta_scores_by_plant_type(weighted=1)
    
    beta_scores_by_plant_type_uw_script, beta_scores_by_plant_type_uw_div = components(beta_scores_by_plant_type_uw)
    beta_scores_by_plant_type_w_script, beta_scores_by_plant_type_w_div = components(beta_scores_by_plant_type_w)
    
    # 4. wins/Losses bar chart
    win_loss_by_image_uw = win_loss_by_image(weighted=0)
    win_loss_by_image_w = win_loss_by_image(weighted=1)
    
    win_loss_by_image_uw_script, win_loss_by_image_uw_div = components(win_loss_by_image_uw)
    win_loss_by_image_w_script, win_loss_by_image_w_div = components(win_loss_by_image_w)
    
    # 5. heat map of beta scores
    beta_scores_heat_map_uw = beta_scores_heat_map(weighted=0)
    beta_scores_heat_map_w = beta_scores_heat_map(weighted=1)
    beta_scores_heat_map_by_image_uw_script, beta_scores_heat_map_by_image_uw_div = components(beta_scores_heat_map_uw)
    beta_scores_heat_map_by_image_w_script, beta_scores_heat_map_by_image_w_div = components(beta_scores_heat_map_w)
    
    # 6. beta scores ranking
    beta_scores_ranking_uw = beta_scores_ranking(weighted=0)
    beta_scores_ranking_w = beta_scores_ranking(weighted=1)
    beta_scores_ranking_uw_script, beta_scores_ranking_uw_div = components(beta_scores_ranking_uw)
    beta_scores_ranking_w_script, beta_scores_ranking_w_div = components(beta_scores_ranking_w)
    
    beta_scores_ranking_datatable = beta_score_by_plant_datatable()
    beta_scores_ranking_datatable = sorted(beta_scores_ranking_datatable, key=lambda r: r['bt_beta_score'], reverse=True)
    
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
        'win_percentage_beta_datatable': win_percentage_beta_datatable,
        'beta_score_by_plant_datatable': beta_scores_by_plant_datatable,
        'beta_scores_ranking_datatable': beta_scores_ranking_datatable
    }
    
    return render_template(
        "dashboard/dashboard_bradley_terry_model.html",
        current_page="bt_model",
        plots=plots,
        data=data
    )
