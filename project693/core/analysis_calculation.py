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
    
    # print('---------------------- initialize ---------------------------')
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
    
    # print(config)
    
    config['weighted_betas'] = calc_weighted_beta_estimates(config)
    config['unweighted_betas'] = calc_unweighted_beta_estimates(config)
    
    # print('config weighted beta:')
    # print(config['weighted_betas'])
    # print('config unweighted beta:')
    # print(config['unweighted_betas'])
    
    config['weighted_beta_normalized'] = calc_normalized_betas(config['weighted_betas'])
    config['unweighted_beta_normalized'] = calc_normalized_betas(config['unweighted_betas'])
    
    # print('config weighted beta norm:')
    # print(config['weighted_beta_normalized'])
    # print('config unweighted beta norm:')
    # print(config['unweighted_beta_normalized'])

    # print(config['data']['RT'])
    return config


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

def constraint(betas):
    return betas[-1]


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

# weighted_betas = calc_weighted_beta_estimates()
# unweighted_betas = calc_unweighted_beta_estimates()

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

# weighted_beta_normalized = calc_normalized_betas(weighted_betas)
# unweighted_beta_normalized = calc_normalized_betas(unweighted_betas)

# calculate probability matrix
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
# def beta_vs_win_percentage(weighted=1):
    
#     beta_normalized = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
    
#     # percentage calculation
#     wins = config['data']['winner'].value_counts()
#     appearances = pd.concat([config['data']['winner'], config['data']['loser']]).value_counts()
#     win_percentages = (wins / appearances).fillna(0)
#     win_percentages_dict = win_percentages.to_dict()
    
#     plot_data = {
#         'plant': [],
#         'win_percentage': [],
#         'bradley_terry_beta': [],
#         'label_color': []
#     }
    
#     for idx in range(config['num_images']):
#         plant_name = config['all_plants'][config['idx_to_id'][idx]]
#         win_percentages = win_percentages_dict[config['idx_to_id'][idx]]
#         bradley_terry_beta = float(beta_normalized[idx])
#         color = '#FFC000' if config['invasive_map'][config['idx_to_id'][idx]] == 1 else '#00B050'
        
#         plot_data['plant'].append(plant_name)
#         plot_data['win_percentage'].append(win_percentages)
#         plot_data['bradley_terry_beta'].append(bradley_terry_beta)
#         plot_data['label_color'].append(color)

    
#     source = ColumnDataSource(data=plot_data)
    
#     x_min = min(plot_data['win_percentage']) - 0.1
#     x_max = max(plot_data['win_percentage']) + 0.3

#     title = "Bradley-Terry beta vs. Win % (weighted)" if weighted else "Bradley-Terry beta vs. Win%"

#     plot = figure(
#         x_range=(x_min, x_max),
#         title=title,
#         x_axis_label="Win percentage",
#         y_axis_label="Bradley-Terry beta",
#         height=600,
#         sizing_mode="stretch_width"
#     )

#     plot.scatter("win_percentage", "bradley_terry_beta", size=8, marker="circle", source=source, color="navy", alpha=0.6)

#     labels = LabelSet(x="win_percentage", y="bradley_terry_beta", text="plant", level="glyph",
#                     x_offset=5, y_offset=5, source=source, text_font_size="9pt", text_color="label_color")
#     plot.add_layout(labels)
    
#     return plot


# 1. scatter chart beta vs win percentage 
def beta_vs_win_percentage_V2(db_rows, weighted=1):
    
    # analysis_dao = AnalysisDAO()
    # rows = analysis_dao.list_beta_score_win_percentage_by_cycle_id(cycle_id)
    
    # row data returned from db
    # cycle_id, plant_id, plant_name, invasiveness, win_percentage, bt_beta_score, bt_beta_score_weighted
    
    plot_data = {
        'plant': [r[2] for r in db_rows],
        'win_percentage': [r[4] for r in db_rows],
        'bradley_terry_beta': [r[6] if weighted else r[5] for r in db_rows],
        'label_color': ['#FFC000' if r[3] == 'invasive' else '#00B050' for r in db_rows]
    }
    
    # beta_normalized = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
    
    # # percentage calculation
    # wins = config['data']['winner'].value_counts()
    # appearances = pd.concat([config['data']['winner'], config['data']['loser']]).value_counts()
    # win_percentages = (wins / appearances).fillna(0)
    # win_percentages_dict = win_percentages.to_dict()
    
    # plot_data = {
    #     'plant': [],
    #     'win_percentage': [],
    #     'bradley_terry_beta': [],
    #     'label_color': []
    # }
    
    # for idx in range(config['num_images']):
    #     plant_name = config['all_plants'][config['idx_to_id'][idx]]
    #     win_percentages = win_percentages_dict[config['idx_to_id'][idx]]
    #     bradley_terry_beta = float(beta_normalized[idx])
    #     color = '#FFC000' if config['invasive_map'][config['idx_to_id'][idx]] == 1 else '#00B050'
        
    #     plot_data['plant'].append(plant_name)
    #     plot_data['win_percentage'].append(win_percentages)
    #     plot_data['bradley_terry_beta'].append(bradley_terry_beta)
    #     plot_data['label_color'].append(color)

    
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
    
    # delete 'win_percentage_origin' column, to keep consistent when downloading data
    # for row in rows:
    #     del row['win_percentage_origin']
    
    return rows





# 2. Attractiveness scores by each image
# def beta_scores_by_image(weighted=1):
#     beta_normalized = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
    
#     image_names = [config['all_plants'][config['idx_to_id'][idx]] for idx in range(len(beta_normalized))]
#     scores = beta_normalized
    
#     colors = [
#         "#FFC000" if config['invasive_map'][config['idx_to_id'][idx]] == 1 else "#00B050"
#         for idx in range(len(beta_normalized))
#     ]

#     source = ColumnDataSource(data=dict(
#         names=image_names,
#         score=scores,
#         color=colors
#     ))
    
#     title = "Normalized Attractiveness Score per Plant (weighted)" if weighted else "Normalized Attractiveness Score per Plant"
    
#     plot = figure(
#         x_range=image_names, height=600, sizing_mode="stretch_width",
#         title=title,
#         x_axis_label="Plant Name", y_axis_label="Score [-1, +1]"
#     )

#     plot.vbar(x="names", top="score", width=0.6, color="color", source=source)

#     plot.xaxis.major_label_orientation = 0.785
    
#     return plot


def beta_scores_by_image_V2(db_rows, weighted=1):
    # beta_normalized = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
    
    # image_names = [config['all_plants'][config['idx_to_id'][idx]] for idx in range(len(beta_normalized))]
    # scores = beta_normalized
    
    # colors = [
    #     "#FFC000" if config['invasive_map'][config['idx_to_id'][idx]] == 1 else "#00B050"
    #     for idx in range(len(beta_normalized))
    # ]
    
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

# 2-1 datatable for attractiveness beta by each plant
# def beta_score_by_plant_datatable():
#     rows = []
    
#     for idx in range(config['num_images']):
#         plant_name = config['all_plants'][config['idx_to_id'][idx]]
#         invasive = config['all_plants_invasiveness'][config['idx_to_id'][idx]]
#         bt_beta = float(config['unweighted_beta_normalized'][idx])
#         bt_beta_weighted = float(config['weighted_beta_normalized'][idx])
        
#         rows.append({
#             'plant': plant_name,
#             'invasiveness': invasive,
#             'bt_beta_score': round(bt_beta, 4),
#             'bt_beta_score_weighted': round(bt_beta_weighted, 4)
#         })
    
#     # rows = sorted(rows, key=lambda r: r['bt_beta_score'], reverse=True)
    
#     return rows

    

# 3. Histogram of attractiveness scores by plant type
# def beta_scores_by_plant_type(weighted=1):
#     beta_normalized = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']

#     # generate 10 bins for histogram
#     bins = np.linspace(min(beta_normalized), max(beta_normalized), 11)
    
#     # print(bins)
    
#     normalized_invasive_betas = [beta_normalized[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 1]
#     normalized_non_invasive_betas = [beta_normalized[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 0]
    
#     hist_invasive, edges_invasive = np.histogram(normalized_invasive_betas, bins=bins)
#     hist_non_invasive, edges_non_invasive = np.histogram(normalized_non_invasive_betas, bins=bins)
    
#     # print(hist_invasive, edges_invasive)
#     # print(hist_non_invasive, edges_non_invasive)
    
#     title = "Histogram of Normalized Attractiveness Scores (weighted)" if weighted else "Histogram of Normalized Attractiveness Scores"
    
#     plot = figure(height=600, sizing_mode="stretch_width",
#             title=title,
#             x_axis_label="Normalized Score", y_axis_label="Count")

#     plot.quad(top=hist_invasive, bottom=0,
#                         left=edges_invasive[:-1], right=edges_invasive[1:],
#                         fill_color="#FFC000", line_color="white", alpha=1,
#                         legend_label="Invasive")

#     plot.quad(top=hist_non_invasive, bottom=0,
#                         left=edges_non_invasive[:-1], right=edges_non_invasive[1:],
#                         fill_color="#00B050", line_color="white", alpha=1,
#                         legend_label="Non-Invasive")

#     mean_invasive = np.mean(normalized_invasive_betas)
#     mean_non_invasive = np.mean(normalized_non_invasive_betas)

#     span_invasive = Span(location=mean_invasive, dimension="height", line_color="#FFC000",
#                         line_width=2, line_dash="dashed")
#     span_non_invasive = Span(location=mean_non_invasive, dimension="height", line_color="#00B050",
#                             line_width=2, line_dash="dashed")

#     plot.add_layout(span_invasive)
#     plot.add_layout(span_non_invasive)

#     plot.legend.location = "top_left"
#     plot.legend.click_policy = "hide"
    
#     return plot


def beta_scores_by_plant_type_V2(db_rows, weighted=1):
    # plot_data = {
    #     'names': [r[2] for r in db_rows],
    #     'score': [r[6] if weighted else r[5] for r in db_rows],
    #     'color': ['#FFC000' if r[3] == 'invasive' else '#00B050' for r in db_rows]
    # }
    
    beta_normalized = [r[6] if weighted else r[5] for r in db_rows]
    # print(beta_normalized)
    
    # beta_normalized = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
    # print(beta_normalized)
    # generate 10 bins for histogram
    bins = np.linspace(min(beta_normalized), max(beta_normalized), 11)
    
    # print(bins)
    
    normalized_invasive_betas = [r[6] if weighted else r[5] for r in db_rows if r[3] == 'invasive']
    normalized_non_invasive_betas = [r[6] if weighted else r[5] for r in db_rows if r[3] != 'invasive']
    
    # print(normalized_invasive_betas)
    # print(normalized_non_invasive_betas)
    
    # normalized_invasive_betas = [beta_normalized[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 1]
    # normalized_non_invasive_betas = [beta_normalized[config['id_to_idx'][key]] for key, value in config['invasive_map'].items() if value == 0]
    
    # print(normalized_invasive_betas)
    # print(normalized_non_invasive_betas)
    
    hist_invasive, edges_invasive = np.histogram(normalized_invasive_betas, bins=bins)
    hist_non_invasive, edges_non_invasive = np.histogram(normalized_non_invasive_betas, bins=bins)
    
    # print(hist_invasive, edges_invasive)
    # print(hist_non_invasive, edges_non_invasive)
    
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
    
    # print('checking...')
    # print(beta_normalized)
    # print(config['invasive_map'])
    # print(config['invasive_map'].items())
    # print(config['id_to_idx'])
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


# 4. Wins/Losses bar chart
# def win_loss_by_image(weighted=1):
#     images = [config['all_plants'][id] for id in config['image_ids']]
    
#     wins = [int((config['data']['winner'] == id).sum()) for id in config['image_ids']]
#     losses = [int((config['data']['loser'] == id).sum()) for id in config['image_ids']]

#     source = ColumnDataSource(data=dict(
#         images=images,
#         wins=wins,
#         losses=losses
#     ))
    
#     title = "Wins/Losses per Image (weighted)" if weighted else "Wins/Losses per Image"
    
#     plot = figure(x_range=images, height=600, sizing_mode="stretch_width", title=title)

#     plot.vbar(x=dodge("images", -0.15, range=plot.x_range), top="wins", width=0.3, source=source,
#         color="#FFC000", legend_label="Wins")
#     plot.vbar(x=dodge("images", 0.15, range=plot.x_range), top="losses", width=0.3, source=source,
#         color="#00B050", legend_label="Losses")
    
#     # Styling
#     plot.x_range.range_padding = 0.05
#     plot.xgrid.grid_line_color = None
#     plot.y_range.start = 0
#     plot.yaxis.axis_label = "Count"
#     plot.legend.location = "top_left"
#     plot.legend.orientation = "horizontal"

#     plot.xaxis.major_label_orientation = 0.785
    
#     return plot


def win_loss_by_image_V2(db_rows, weighted=1):
    
    plot_data = {
        'images': [r[2] for r in db_rows],
        'wins': [r[4] for r in db_rows],
        'losses': [r[5] for r in db_rows]
    }
    
    # images = [config['all_plants'][id] for id in config['image_ids']]
    
    # wins = [int((config['data']['winner'] == id).sum()) for id in config['image_ids']]
    # losses = [int((config['data']['loser'] == id).sum()) for id in config['image_ids']]

    # source = ColumnDataSource(data=dict(
    #     images=images,
    #     wins=wins,
    #     losses=losses
    # ))
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


# 5. Attractive beta score heat map
# def beta_scores_heat_map(weighted=1):
#     betas = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
#     plant_names = [config['all_plants'][config['idx_to_id'][idx]] for idx in range(len(betas))]
    
#     matrix = probability_matrix(betas)
    
#     # mapper = LinearColorMapper(palette="Viridis256", low=0, high=1)
#     mapper = LinearColorMapper(palette="RdBu11", low=0, high=1)
    
#     n = len(plant_names)
#     xname, yname, value = [], [], []
    
#     for i in range(n):
#         for j in range(n):
#             if not np.isnan(matrix[i, j]):
#                 xname.append(plant_names[j])
#                 yname.append(plant_names[i])
#                 value.append(matrix[i, j])
    
#     title = "Attractiveness Score Heat Map (weighted)" if weighted else "Attractiveness Score Heat Map"
    
#     plot = figure(title=title, x_range=plant_names, y_range=list(reversed(plant_names)),
#                   x_axis_location="below", height=700, sizing_mode="stretch_width")
    
#     plot.rect(x="x", y="y", width=1, height=1, source=dict(x=xname, y=yname, value=value),
#               fill_color=transform('value', mapper), line_color=None)
    
#     color_bar = ColorBar(color_mapper=mapper, ticker=BasicTicker(desired_num_ticks=10),
#                          formatter=PrintfTickFormatter(format="%.2f"),
#                          label_standoff=12, border_line_color=None, location=(0, 0))
#     plot.add_layout(color_bar, "right")
    
#     # plot.xaxis.major_label_orientation = np.pi/4
#     plot.xaxis.major_label_orientation = "vertical"
    
    
#     # plot.xaxis.visible = False
#     # plot.yaxis.visible = False
    
#     colors = [
#         "#FFC000" if config['invasive_map'][config['idx_to_id'][idx]] == 1 else "#00B050"
#         for idx in range(len(betas))
#     ]
    
#     x_source = ColumnDataSource(dict(
#         x=plant_names,
#         y=[plant_names[0]] * len(plant_names),
#         name=plant_names,
#         color=colors
#     ))
#     x_labels = LabelSet(
#         x="x", y=0, text="name", text_color="color",
#         source=x_source, y_offset=-5, text_align="center", text_baseline="top"
#     )
#     plot.add_layout(x_labels)
    
#     y_source = ColumnDataSource(dict(
#         x=[plant_names[0]] * len(plant_names),
#         y=list(reversed(plant_names)),
#         name=list(reversed(plant_names)),
#         color=list(reversed(colors))
#     ))
#     y_labels = LabelSet(
#         x=0, y="y", text="name", text_color="color",
#         source=y_source, x_offset=-5, text_align="right", text_baseline="middle"
#     )
    
#     return plot


def beta_scores_heat_map_V2(db_rows, weighted=1):
    
    betas = [r[6] if weighted else r[5] for r in db_rows]
    plant_names = [r[2] for r in db_rows]
    # print('db rows betas:')
    # print(betas)
    # print('plant names:')
    # print(plant_names)
    
    # betas = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
    # plant_names = [config['all_plants'][config['idx_to_id'][idx]] for idx in range(len(betas))]
    # print('config betas:')
    # print(betas)
    # print('plant names:')
    # print(plant_names)
    
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
    
    
    # plot.xaxis.visible = False
    # plot.yaxis.visible = False
    
    colors = ["#FFC000" if r[3] == 'invasive' else "#00B050" for r in db_rows]
    
    # colors = [
    #     "#FFC000" if config['invasive_map'][config['idx_to_id'][idx]] == 1 else "#00B050"
    #     for idx in range(len(betas))
    # ]
    
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
    print(betas)
    print(config['idx_to_id'])
    print(config['all_plants'])
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


# 6. Ranking of beta scores
# def beta_scores_ranking(weighted=1):
#     betas = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
#     plant_names = [config['all_plants'][config['idx_to_id'][idx]] for idx in range(len(betas))]
    
#     df = pd.DataFrame({
#         "plant": plant_names,
#         "beta": betas
#     })
#     df["rank"] = df["beta"].rank(ascending=False, method="min").astype(int)
#     df["color"] = [
#         "#FFC000" if config['invasive_map'][config['idx_to_id'][idx]] == 1 else "#00B050"
#         for idx in range(len(betas))
#     ]
    
#     df = df.sort_values("beta", ascending=True)
    
#     source = ColumnDataSource(df)
    
#     title = "Plant Attractiveness Ranking (weighted)" if weighted else "Plant Attractiveness Ranking"
    
#     plot = figure(
#         y_range=list(df["plant"]),
#         x_axis_label="Normalized Beta Score",
#         y_axis_label="Plant",
#         height=600,
#         sizing_mode="stretch_width",
#         title=title
#     )
    
#     plot.hbar(
#         y="plant",
#         right="beta",
#         height=0.6,
#         color="color",
#         source=source
#     )
    
#     labels = LabelSet(
#         x="beta",
#         y="plant",
#         text="rank",
#         x_offset=5,
#         y_offset=-8,
#         text_font_size="10pt",
#         text_color="black"
#     )
    
#     plot.add_layout(labels)
    
#     return plot


def beta_scores_ranking_V2(db_rows, weighted=1):
    
    betas = [r[6] if weighted else r[5] for r in db_rows]
    plant_names = [r[2] for r in db_rows]
    colors = ['#FFC000' if r[3] == 'invasive' else '#00B050' for r in db_rows]
    
    # betas = config['weighted_beta_normalized'] if weighted else config['unweighted_beta_normalized']
    # plant_names = [config['all_plants'][config['idx_to_id'][idx]] for idx in range(len(betas))]
    
    df = pd.DataFrame({
        "plant": plant_names,
        "beta": betas,
        "color": colors
    })
    df["rank"] = df["beta"].rank(ascending=False, method="min").astype(int)
    # df["color"] = [
    #     "#FFC000" if config['invasive_map'][config['idx_to_id'][idx]] == 1 else "#00B050"
    #     for idx in range(len(betas))
    # ]
    
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


def save_survey_cycle_analysis_data():
    
    print('--------------------- saving data ----------------------------')
    config = initialize()
    
    # print(config)
    
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
    
    print('--------------------- end of saving data ----------------------------')


def refresh_survey_cycle_analysis_data_by_cycle_id(cycle_id):
    # initialize()
    analysis_dao = AnalysisDAO()
    # survey_dao = SurveyDAO()
    # cycle_id = survey_dao.get_active_survey_cycle_id()
    
    config = initialize(cycle_id)
    
    # print(config)
    
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
