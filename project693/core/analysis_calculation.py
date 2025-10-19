from project693.dao.analysis_dao import AnalysisDAO
from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.dao.survey_dao import SurveyDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, LabelSet, Span, ColorBar, LinearColorMapper, BasicTicker, PrintfTickFormatter
from bokeh.transform import dodge, transform
from bokeh.resources import CDN
from scipy.optimize import minimize
import numpy as np
import pandas as pd
from collections import OrderedDict

# Sample Config dict
# config = {
#     'id_to_idx': None,
#     'idx_to_id': None,
#     'data': None,
#     'all_plants': None,
#     'betas_init': None,
#     'invasive_map': {},
#     'num_images': None,
#     'all_plants_invasiveness': None,
#     'weighted_betas': None,
#     'unweighted_betas': None,
#     'weighted_beta_normalized': None,
#     'unweighted_beta_normalized': None,
#     'num_images': None,
#     'image_ids': None
# }

# initialize for Bradley-Terry model calculation
# data are fetched from database and saved into a pandas data framework for calculation
def initialize(cycle_id=None):
    
    config = {
        'id_to_idx': None,
        'idx_to_id': None,
        'data': None,
        'all_plants': None,
        'betas_init': None,
        'invasive_map': {},
        'num_images': None,
        'all_plants_invasiveness': None,
        'weighted_betas': None,
        'unweighted_betas': None,
        'weighted_beta_normalized': None,
        'unweighted_beta_normalized': None,
        'num_images': None,
        'image_ids': None
    }
    
    analysis_dao = AnalysisDAO()

    all_plants_from_db = analysis_dao.list_survey_plants(cycle_id)
    all_plants_invasiveness_from_db = analysis_dao.list_survey_plants_invasiveness(cycle_id)
    
    all_survey_results = analysis_dao.list_survey_results(cycle_id)
    
    config['data'] = pd.DataFrame(all_survey_results, columns=[
        'winner',
        'loser',
        'RT',   # response time
        'invasive_winner',
        'invasive_loser'
    ])

    # clear invasive_map dict
    config['invasive_map'] = {}

    for index, row in config['data'].iterrows():
        winner = int(row['winner'])
        loser = int(row['loser'])
        invasive_winner = int(row['invasive_winner'])
        config['invasive_map'].update({
            winner: 1 if invasive_winner else 0
        })
        config['invasive_map'].update({
            loser: 1 if not invasive_winner else 0
        })

    config['image_ids'] = sorted(set(config['data']['winner']).union(set(config['data']['loser'])))
    config['id_to_idx'] = {img_id: idx for idx, img_id in enumerate(config['image_ids'])}
    config['idx_to_id'] = {idx: img_id for img_id, idx in config['id_to_idx'].items()}
    config['all_plants'] = dict(all_plants_from_db)
    config['all_plants_invasiveness'] = dict(all_plants_invasiveness_from_db)
    config['num_images'] = len(config['image_ids'])
    config['betas_init'] = np.zeros(config['num_images'])
    
    config['weighted_betas'] = calc_weighted_beta_estimates(config)
    config['unweighted_betas'] = calc_unweighted_beta_estimates(config)
    
    config['weighted_beta_normalized'] = calc_normalized_betas(config['weighted_betas'])
    config['unweighted_beta_normalized'] = calc_normalized_betas(config['unweighted_betas'])
    
    return config


# weighted log likelihood function to calculate bradley-terry model beta scores
def weighted_log_likelihood(betas, config):
    ll = 0.0
    
    for _, row in config['data'].iterrows():
        i= config['id_to_idx'][row['winner']]
        j = config['id_to_idx'][row['loser']]
        beta_i, beta_j = betas[i], betas[j]

        weight = 1 / (row['RT'] + 1e-9) # inversed weighting
        
        p = np.exp(beta_i) / (np.exp(beta_i) + np.exp(beta_j))
        ll += weight * np.log(p + 1e-9)
    return -ll


# unweighted log likelihood function to calculate bradley-terry model beta scores
def unweighted_log_likelihood(betas, config):
    ll = 0.0
    for _, row in config['data'].iterrows():
        # mapping image id to index
        i= config['id_to_idx'][row['winner']]
        j = config['id_to_idx'][row['loser']]
        beta_i, beta_j = betas[i], betas[j]
        weight = 1      # un-weighted
        p = np.exp(beta_i) / (np.exp(beta_i) + np.exp(beta_j))
        ll += weight * np.log(p + 1e-9)
    return -ll


# constraint function to calculate beta scores
def constraint(betas):
    return betas[-1]


# function to calculate weighted beta scores
# use scipy.minimize function
def calc_weighted_beta_estimates(config):
    if config['data'] is None or len(config['data']) == 0:
        return np.array(config['betas_init'])
    
    result = minimize(
        fun=weighted_log_likelihood,
        x0=config['betas_init'],
        args=(config,),
        constraints={'type': 'eq', 'fun': constraint},
        method='SLSQP'
    )
    return result.x

# function to calculate unweighted beta scores
# use scipy.minimize function
def calc_unweighted_beta_estimates(config):
    if config['data'] is None or len(config['data']) == 0:
        return np.array(config['betas_init'])
    
    result = minimize(
        fun=unweighted_log_likelihood,
        x0=config['betas_init'],
        args=(config,),
        constraints={'type': 'eq', 'fun': constraint},
        method='SLSQP'
    )
    return result.x


# normalize beta scores
def calc_normalized_betas(betas):
    betas = np.array(betas)
    
    if betas.size == 0:
        return np.array([])
    
    beta_min = betas.min()
    beta_max = betas.max()
    
    if beta_max == beta_min:
        return np.zeros_like(betas, dtype=float)
    
    beta_scale_0_1 = (betas - beta_min) / (beta_max - beta_min)
    beta_normalized = beta_scale_0_1 * 2 - 1
    
    return beta_normalized


# calculate probability matrix used in heat map
def probability_matrix(betas):
    n = len(betas)
    prob_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                prob_matrix[i, j] = np.exp(betas[i]) / (np.exp(betas[i]) + np.exp(betas[j]))
            else:
                prob_matrix[i, j] = np.nan
    return prob_matrix


# 1. scatter chart beta vs win percentage 
def beta_vs_win_percentage_V2(db_rows, weighted=1):
    
    plot_data = {
        'plant': [r[2] for r in db_rows],
        'win_percentage': [r[4] for r in db_rows],
        'bradley_terry_beta': [r[6] if weighted else r[5] for r in db_rows],
        'label_color': ['#FFC000' if r[3] == 'invasive' else '#00B050' for r in db_rows]
    }
       
    source = ColumnDataSource(data=plot_data)
    
    x_min = min(plot_data['win_percentage']) - 0.1
    x_max = max(plot_data['win_percentage']) + 0.3

    title = "Bradley-Terry beta vs. Win % (weighted)" if weighted else "Bradley-Terry beta vs. Win%"

    plot = figure(
        x_range=(x_min, x_max),
        title=title,
        x_axis_label="Win percentage",
        y_axis_label="Bradley-Terry beta",
        height=600,
        sizing_mode="stretch_width"
    )

    plot.scatter("win_percentage", "bradley_terry_beta", size=8, marker="circle", source=source, color="navy", alpha=0.6)

    labels = LabelSet(x="win_percentage", y="bradley_terry_beta", text="plant", level="glyph",
                    x_offset=5, y_offset=5, source=source, text_font_size="9pt", text_color="label_color")
    plot.add_layout(labels)
    
    return plot


# 1-1 datatable for beta vs win percentage
def beta_vs_win_percentage_datatable(config):
    rows = []
    
    # percentage calculation
    wins = config['data']['winner'].value_counts()
    appearances = pd.concat([config['data']['winner'], config['data']['loser']]).value_counts()
    win_percentages = (wins / appearances).fillna(0)
    win_percentages_dict = win_percentages.to_dict()
    
    for idx in range(config['num_images']):
        plant_id = config['idx_to_id'][idx]
        plant_name = config['all_plants'][config['idx_to_id'][idx]]
        invasive = config['all_plants_invasiveness'][config['idx_to_id'][idx]]
        win_percentage = win_percentages_dict[config['idx_to_id'][idx]]
        bt_beta = float(config['unweighted_beta_normalized'][idx])
        bt_beta_weighted = float(config['weighted_beta_normalized'][idx])
        
        rows.append({
            'plant_id': plant_id,
            'plant': plant_name,
            'invasiveness': invasive,
            'win_percentage_value': win_percentage,
            'win_percentage': str(round(win_percentage * 100, 2)) + '%',
            'bt_beta_score': round(bt_beta, 4),
            'bt_beta_score_weighted': round(bt_beta_weighted, 4)
        })
    
    rows = sorted(rows, key=lambda r: r['win_percentage_value'], reverse=True)
    
    return rows


# generate plot data for beat scores by plant image
def beta_scores_by_image_V2(db_rows, weighted=1):
   
    plot_data = {
        'names': [r[2] for r in db_rows],
        'score': [r[6] if weighted else r[5] for r in db_rows],
        'color': ['#FFC000' if r[3] == 'invasive' else '#00B050' for r in db_rows]
    }

    source = ColumnDataSource(data=plot_data)
    
    title = "Normalized Attractiveness Score per Plant (weighted)" if weighted else "Normalized Attractiveness Score per Plant"
    
    plot = figure(
        x_range=plot_data['names'], height=600, sizing_mode="stretch_width",
        title=title,
        x_axis_label="Plant Name", y_axis_label="Score [-1, +1]"
    )

    plot.vbar(x="names", top="score", width=0.6, color="color", source=source)

    plot.xaxis.major_label_orientation = 0.785
    
    return plot


# generate plot data for beta scores by plant type for histogram chart
def beta_scores_by_plant_type_V2(db_rows, weighted=1):
    
    beta_normalized = [r[6] if weighted else r[5] for r in db_rows]

    # generate 10 bins for histogram
    bins = np.linspace(min(beta_normalized), max(beta_normalized), 11)
    
    normalized_invasive_betas = [r[6] if weighted else r[5] for r in db_rows if r[3] == 'invasive']
    normalized_non_invasive_betas = [r[6] if weighted else r[5] for r in db_rows if r[3] != 'invasive']
    
    hist_invasive, edges_invasive = np.histogram(normalized_invasive_betas, bins=bins)
    hist_non_invasive, edges_non_invasive = np.histogram(normalized_non_invasive_betas, bins=bins)
    
    title = "Histogram of Normalized Attractiveness Scores (weighted)" if weighted else "Histogram of Normalized Attractiveness Scores"
    
    plot = figure(height=600, sizing_mode="stretch_width",
            title=title,
            x_axis_label="Normalized Score", y_axis_label="Count")

    plot.quad(top=hist_invasive, bottom=0,
                        left=edges_invasive[:-1], right=edges_invasive[1:],
                        fill_color="#FFC000", line_color="white", alpha=1,
                        legend_label="Invasive")

    plot.quad(top=hist_non_invasive, bottom=0,
                        left=edges_non_invasive[:-1], right=edges_non_invasive[1:],
                        fill_color="#00B050", line_color="white", alpha=1,
                        legend_label="Non-Invasive")

    mean_invasive = np.mean(normalized_invasive_betas)
    mean_non_invasive = np.mean(normalized_non_invasive_betas)

    span_invasive = Span(location=mean_invasive, dimension="height", line_color="#FFC000",
                        line_width=2, line_dash="dashed")
    span_non_invasive = Span(location=mean_non_invasive, dimension="height", line_color="#00B050",
                            line_width=2, line_dash="dashed")

    plot.add_layout(span_invasive)
    plot.add_layout(span_non_invasive)

    plot.legend.location = "top_left"
    plot.legend.click_policy = "hide"
    
    return plot

# 3-1 beta score by plant type
def beta_scores_by_plant_type_datatable(config):
    rows = []
    
    beta_normalized = config['unweighted_beta_normalized']
    beta_normalized_weighted = config['weighted_beta_normalized']

    # generate 10 bins for histogram
    bins = np.linspace(min(beta_normalized), max(beta_normalized), 11)
    bins_weighted = np.linspace(min(beta_normalized_weighted), max(beta_normalized_weighted), 11)
    
    normalized_invasive_betas = [beta_normalized[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 1]
    normalized_non_invasive_betas = [beta_normalized[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 0]
    
    normalized_invasive_betas_weighted = [beta_normalized_weighted[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 1]
    normalized_non_invasive_betas_weighted = [beta_normalized_weighted[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 0]
    
    hist_invasive, edges_invasive = np.histogram(normalized_invasive_betas, bins=bins)
    hist_non_invasive, edges_non_invasive = np.histogram(normalized_non_invasive_betas, bins=bins)
    
    hist_invasive_weighted, edges_invasive_weighted = np.histogram(normalized_invasive_betas_weighted, bins=bins_weighted)
    hist_non_invasive_weighted, edges_non_invasive_weighted = np.histogram(normalized_non_invasive_betas_weighted, bins=bins_weighted)
    
    for k in range(10):
        row = {
            'Bin_Number': k+1,
            'Bin_Left': round(float(bins[k]), 2),
            'Bin_Right': round(float(bins[k+1]), 2),
            'Invasive_Count': int(hist_invasive[k]),
            'Non_Invasive_Count': int(hist_non_invasive[k]),
            'Bin_Number_Weighted': k+1,
            'Bin_Left_Weighted': round(float(bins_weighted[k]), 2),
            'Bin_Right_Weighted': round(float(bins_weighted[k+1]), 2),
            'Invasive_Count_Weighted': int(hist_invasive_weighted[k]),
            'Non_Invasive_Count_Weighted': int(hist_non_invasive_weighted[k])
        }
        rows.append(row)

    return rows

# generate plot data for win/loss chart by plant image
def win_loss_by_image_V2(db_rows, weighted=1):
    
    plot_data = {
        'images': [r[2] for r in db_rows],
        'wins': [r[4] for r in db_rows],
        'losses': [r[5] for r in db_rows]
    }
    
    source = ColumnDataSource(data=plot_data)
    
    title = "Wins/Losses per Image (weighted)" if weighted else "Wins/Losses per Image"
    
    plot = figure(x_range=plot_data['images'], height=600, sizing_mode="stretch_width", title=title)

    plot.vbar(x=dodge("images", -0.15, range=plot.x_range), top="wins", width=0.3, source=source,
        color="#FFC000", legend_label="Wins")
    plot.vbar(x=dodge("images", 0.15, range=plot.x_range), top="losses", width=0.3, source=source,
        color="#00B050", legend_label="Losses")
    
    # Styling
    plot.x_range.range_padding = 0.05
    plot.xgrid.grid_line_color = None
    plot.y_range.start = 0
    plot.yaxis.axis_label = "Count"
    plot.legend.location = "top_left"
    plot.legend.orientation = "horizontal"

    plot.xaxis.major_label_orientation = 0.785
    
    return plot


# 4-1 Win/Loss by plant datatable
def win_loss_by_plant_datatable(config):
    rows = []
    
    images = [config['all_plants'][id] for id in config['image_ids']]
    
    wins = [int((config['data']['winner'] == id).sum()) for id in config['image_ids']]
    losses = [int((config['data']['loser'] == id).sum()) for id in config['image_ids']]
    
    for idx in range(config['num_images']):
        plant_id = config['idx_to_id'][idx]
        plant_name = images[idx]
        invasive = config['all_plants_invasiveness'][config['idx_to_id'][idx]]
        win = wins[idx]
        loss = losses[idx]
        
        rows.append({
            'plant_id': plant_id,
            'plant': plant_name,
            'invasiveness': invasive,
            'win': win,
            'loss': loss
        })
    
    return rows


# generate plot data for beta scores by heat map
def beta_scores_heat_map_V2(db_rows, weighted=1):
    
    betas = [r[6] if weighted else r[5] for r in db_rows]
    plant_names = [r[2] for r in db_rows]
    
    matrix = probability_matrix(betas)
    
    # mapper = LinearColorMapper(palette="Viridis256", low=0, high=1)
    mapper = LinearColorMapper(palette="RdBu11", low=0, high=1)
    
    n = len(plant_names)
    xname, yname, value = [], [], []
    
    for i in range(n):
        for j in range(n):
            if not np.isnan(matrix[i, j]):
                xname.append(plant_names[j])
                yname.append(plant_names[i])
                value.append(matrix[i, j])
    
    title = "Attractiveness Score Heat Map (weighted)" if weighted else "Attractiveness Score Heat Map"
    
    plot = figure(title=title, x_range=plant_names, y_range=list(reversed(plant_names)),
                  x_axis_location="below", height=700, sizing_mode="stretch_width")
    
    plot.rect(x="x", y="y", width=1, height=1, source=dict(x=xname, y=yname, value=value),
              fill_color=transform('value', mapper), line_color=None)
    
    color_bar = ColorBar(color_mapper=mapper, ticker=BasicTicker(desired_num_ticks=10),
                         formatter=PrintfTickFormatter(format="%.2f"),
                         label_standoff=12, border_line_color=None, location=(0, 0))
    plot.add_layout(color_bar, "right")
    
    # plot.xaxis.major_label_orientation = np.pi/4
    plot.xaxis.major_label_orientation = "vertical"
    
    
    colors = ["#FFC000" if r[3] == 'invasive' else "#00B050" for r in db_rows]
    
    x_source = ColumnDataSource(dict(
        x=plant_names,
        y=[plant_names[0]] * len(plant_names),
        name=plant_names,
        color=colors
    ))
    x_labels = LabelSet(
        x="x", y=0, text="name", text_color="color",
        source=x_source, y_offset=-5, text_align="center", text_baseline="top"
    )
    plot.add_layout(x_labels)
    
    y_source = ColumnDataSource(dict(
        x=[plant_names[0]] * len(plant_names),
        y=list(reversed(plant_names)),
        name=list(reversed(plant_names)),
        color=list(reversed(colors))
    ))
    y_labels = LabelSet(
        x=0, y="y", text="name", text_color="color",
        source=y_source, x_offset=-5, text_align="right", text_baseline="middle"
    )
    
    return plot


# 5-1 beta score heat map datatable
def beta_score_heat_map_datatable(config):
    rows = []
    betas = config['unweighted_beta_normalized']
    betas_weighted = config['weighted_beta_normalized']
    plant_names = [config['all_plants'][config['idx_to_id'][idx]] for idx in range(len(betas))]
    plant_ids = [config['idx_to_id'][idx] for idx in range(len(betas))]
    
    matrix = probability_matrix(betas)
    matrix_weighted = probability_matrix(betas_weighted)
    
    n = len(plant_names)
    
    for i in range(n):
        for j in range(n):
            row = {
                'Plant_A_Id': plant_ids[i],
                'Plant_A': plant_names[i],
                'Plant_B_Id': plant_ids[j],
                'Plant_B': plant_names[j],
                'A_Beats_B': 'NA' if np.isnan(matrix[i, j]) else round(float(matrix[i, j]), 5),
                'A_Beats_B_Weighted': 'NA' if np.isnan(matrix_weighted[i, j]) else round(float(matrix_weighted[i, j]), 5),
            }
            rows.append(row)

    return rows

# generate plot data for beta score ranking
def beta_scores_ranking_V2(db_rows, weighted=1):
    
    betas = [r[6] if weighted else r[5] for r in db_rows]
    plant_names = [r[2] for r in db_rows]
    colors = ['#FFC000' if r[3] == 'invasive' else '#00B050' for r in db_rows]
    
    df = pd.DataFrame({
        "plant": plant_names,
        "beta": betas,
        "color": colors
    })
    df["rank"] = df["beta"].rank(ascending=False, method="min").astype(int)
    
    df = df.sort_values("beta", ascending=True)
    
    source = ColumnDataSource(df)
    
    title = "Plant Attractiveness Ranking (weighted)" if weighted else "Plant Attractiveness Ranking"
    
    plot = figure(
        y_range=list(df["plant"]),
        x_axis_label="Normalized Beta Score",
        y_axis_label="Plant",
        height=600,
        sizing_mode="stretch_width",
        title=title
    )
    
    plot.hbar(
        y="plant",
        right="beta",
        height=0.6,
        color="color",
        source=source
    )
    
    labels = LabelSet(
        x="beta",
        y="plant",
        text="rank",
        x_offset=5,
        y_offset=-8,
        text_font_size="10pt",
        text_color="black"
    )
    
    plot.add_layout(labels)
    
    return plot

# save survey analysis data for current active survey cycle
def save_survey_cycle_analysis_data():
    config = initialize()
    
    analysis_dao = AnalysisDAO()
    survey_dao = SurveyDAO()
    cycle_id = survey_dao.get_active_survey_cycle_id()
    
    # heat map data
    rows = beta_score_heat_map_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_heat_map_by_plant(cycle_id)
    # save data
    analysis_dao.save_beta_score_heat_map_by_plant(rows, cycle_id)
    
    # win/loss data
    rows = win_loss_by_plant_datatable(config)
    # clear data first
    analysis_dao.delete_win_loss_by_plant(cycle_id)
    # save data
    analysis_dao.save_win_loss_by_plant(rows, cycle_id)

    # beta score by plant type histogram
    rows = beta_scores_by_plant_type_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_by_invasive_type_histogram(cycle_id)
    # save data
    analysis_dao.save_beta_score_by_invasive_type_histogram(rows, cycle_id)
    
    # beta score by plant vs win percentage
    rows = beta_vs_win_percentage_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_win_percentage(cycle_id)
    # save data
    analysis_dao.save_beta_score_win_percentage(rows, cycle_id)


# recalcuate analysis data for cycle by cycle id
def refresh_survey_cycle_analysis_data_by_cycle_id(cycle_id):
    
    # if all survey data in this cycle has been deleted, then no need to refresh
    survey_dao = SurveyDAO()
    result = survey_dao.survey_results_available_for_cycle(cycle_id)
    if not result:
        return
    
    analysis_dao = AnalysisDAO()
    config = initialize(cycle_id)
    
    # heat map data
    rows = beta_score_heat_map_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_heat_map_by_plant(cycle_id)
    # save data
    analysis_dao.save_beta_score_heat_map_by_plant(rows, cycle_id)
    
    # win/loss data
    rows = win_loss_by_plant_datatable(config)
    # clear data first
    analysis_dao.delete_win_loss_by_plant(cycle_id)
    # save data
    analysis_dao.save_win_loss_by_plant(rows, cycle_id)

    # beta score by plant type histogram
    rows = beta_scores_by_plant_type_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_by_invasive_type_histogram(cycle_id)
    # save data
    analysis_dao.save_beta_score_by_invasive_type_histogram(rows, cycle_id)
    
    # beta score by plant vs win percentage
    rows = beta_vs_win_percentage_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_win_percentage(cycle_id)
    # save data
    analysis_dao.save_beta_score_win_percentage(rows, cycle_id)


# save analysis data for all survey results
def save_overall_survey_cycle_analysis_data():
    
    # if all survey data is deleted, then no need to recalculate the result
    survey_dao = SurveyDAO()
    result = survey_dao.survey_results_available()
    if not result:
        return
    
    # cycle_id = 0 for all survey results
    config = initialize(cycle_id=0)
    
    analysis_dao = AnalysisDAO()
    
    # cycle_id = 0 for all survey results
    cycle_id = 0
    
    # heat map data
    rows = beta_score_heat_map_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_heat_map_by_plant(cycle_id)
    # save data
    analysis_dao.save_beta_score_heat_map_by_plant(rows, cycle_id)
    
    # win/loss data
    rows = win_loss_by_plant_datatable(config)
    # clear data first
    analysis_dao.delete_win_loss_by_plant(cycle_id)
    # save data
    analysis_dao.save_win_loss_by_plant(rows, cycle_id)

    # beta score by plant type histogram
    rows = beta_scores_by_plant_type_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_by_invasive_type_histogram(cycle_id)
    # save data
    analysis_dao.save_beta_score_by_invasive_type_histogram(rows, cycle_id)
    
    # beta score by plant vs win percentage
    rows = beta_vs_win_percentage_datatable(config)
    # clear data first
    analysis_dao.delete_beta_score_win_percentage(cycle_id)
    # save data
    analysis_dao.save_beta_score_win_percentage(rows, cycle_id)
