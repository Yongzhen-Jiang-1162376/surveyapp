from project693.dao.analysis_dao import AnalysisDAO
from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.dao.analysis_dao import AnalysisDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select, NumeralTickFormatter, LabelSet, Span
from bokeh.transform import dodge
from bokeh.resources import CDN
from scipy.optimize import minimize
import numpy as np
import pandas as pd



analysis_dao = AnalysisDAO()


all_plants_from_db = analysis_dao.list_survey_plants()
all_survey_results = analysis_dao.list_survey_results()

data = pd.DataFrame(all_survey_results, columns=[
    'winner',
    'loser',
    'RT',   # response time
    'invasive_winner',
    'invasive_loser'
])

invasive_map = {}

for index, row in data.iterrows():
    winner = int(row['winner'])
    loser = int(row['loser'])
    invasive_winner = int(row['invasive_winner'])
    invasive_map.update({
        winner: 1 if invasive_winner else 0
    })
    invasive_map.update({
        loser: 1 if not invasive_winner else 0
    })

image_ids = sorted(set(data['winner']).union(set(data['loser'])))
id_to_idx = {img_id: idx for idx, img_id in enumerate(image_ids)}
idx_to_id = {idx: img_id for img_id, idx in id_to_idx.items()}
all_plants = dict(all_plants_from_db)
num_images = len(image_ids)
betas_init = np.zeros(num_images)


def weighted_log_likelihood(betas, data):
    ll = 0.0
    for _, row in data.iterrows():
        # mapping image id to index
        i= id_to_idx[row['winner']]
        j = id_to_idx[row['loser']]
        beta_i, beta_j = betas[i], betas[j]
        weight = row['RT']       # weight
        p = np.exp(beta_i) / (np.exp(beta_i) + np.exp(beta_j))
        ll += weight * np.log(p + 1e-9)
    return -ll


def unweighted_log_likelihood(betas, data):
    ll = 0.0
    for _, row in data.iterrows():
        # mapping image id to index
        i= id_to_idx[row['winner']]
        j = id_to_idx[row['loser']]
        beta_i, beta_j = betas[i], betas[j]
        weight = 1      # un-weighted
        p = np.exp(beta_i) / (np.exp(beta_i) + np.exp(beta_j))
        ll += weight * np.log(p + 1e-9)
    return -ll

def constraint(betas):
    return betas[-1]


def calc_weighted_beta_estimates():
    result = minimize(
        fun=weighted_log_likelihood,
        x0=betas_init,
        args=(data,),
        constraints={'type': 'eq', 'fun': constraint},
        method='SLSQP'
    )
    return result.x

def calc_unweighted_beta_estimates():
    result = minimize(
        fun=unweighted_log_likelihood,
        x0=betas_init,
        args=(data,),
        constraints={'type': 'eq', 'fun': constraint},
        method='SLSQP'
    )
    return result.x

weighted_betas = calc_weighted_beta_estimates()
unweighted_betas = calc_unweighted_beta_estimates()

def calc_normalized_betas(betas):
    beta_min = betas.min()
    beta_max = betas.max()
    
    beta_scale_0_1 = (betas - beta_min) / (beta_max - beta_min)
    beta_normalized = beta_scale_0_1 * 2 - 1
    
    return beta_normalized

weighted_beta_normalized = calc_normalized_betas(weighted_betas)
unweighted_beta_normalized = calc_normalized_betas(unweighted_betas)

# 1. scatter chart win percentage vs beta 
def beta_vs_win_percentage(weighted=1):
    
    beta_normalized = weighted_beta_normalized if weighted else unweighted_beta_normalized
    
    # # Normalization of Betas
    # beta_min = beta_estimates.min()
    # beta_max = beta_estimates.max()
    
    # # Min-max scale to [0, 1]
    # beta_scale_0_1 = (beta_estimates - beta_min) / (beta_max - beta_min)
    
    # # rescale to [-1, +1]
    # beta_normalized = beta_scale_0_1 * 2 - 1
    
    # compare normalized invasive vs. non-invasive
    # normalized_invasive_betas = [beta_normalized[id_to_idx[key]] for key, value in invasive_map.items() if value == 1]
    # normalized_non_invasive_betas = [beta_normalized[id_to_idx[key]] for key, value in invasive_map.items() if value == 0]
    
    # percentage calculation
    wins = data['winner'].value_counts()
    appearances = pd.concat([data['winner'], data['loser']]).value_counts()
    win_percentages = (wins / appearances).fillna(0)
    
    plot_data = {
        'plant': [],
        'win_percentage': [],
        'bradley_terry_beta': [],
        'label_color': []
    }
    
    win_percentages_dict = win_percentages.to_dict()
    
    for idx in range(num_images):
        plant_name = all_plants[idx_to_id[idx]]
        win_percentages = win_percentages_dict[idx_to_id[idx]]
        bradley_terry_beta = float(beta_normalized[idx])
        color = '#FFC000' if invasive_map[idx_to_id[idx]] == 1 else '#00B050'
        
        plot_data['plant'].append(plant_name)
        plot_data['win_percentage'].append(win_percentages)
        plot_data['bradley_terry_beta'].append(bradley_terry_beta)
        plot_data['label_color'].append(color)
    
    source = ColumnDataSource(data=plot_data)
    
    x_min = min(plot_data['win_percentage']) - 0.1
    x_max = max(plot_data['win_percentage']) + 0.3

    plot = figure(
        x_range=(x_min, x_max),
        title="Bradley-Terry beta vs. Win %",
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


# 2. Histogram of attractiveness scores by each image
def beta_scores_by_image(weighted=1):
    beta_normalized = weighted_beta_normalized if weighted else unweighted_beta_normalized
    
    image_names = [all_plants[idx_to_id[idx]] for idx in range(len(beta_normalized))]
    scores = beta_normalized
    
    colors = [
        "#FFC000" if invasive_map[idx_to_id[idx]] == 1 else "#00B050"
        for idx in range(len(beta_normalized))
    ]

    source = ColumnDataSource(data=dict(
        names=image_names,
        score=scores,
        color=colors
    ))
    
    plot = figure(
        x_range=image_names, height=600, sizing_mode="stretch_width",
        title="Normalized Attractiveness Score per Plant",
        x_axis_label="Plant Name", y_axis_label="Score [-1, +1]"
    )

    plot.vbar(x="names", top="score", width=0.6, color="color", source=source)

    plot.xaxis.major_label_orientation = 0.785
    
    return plot


# 3. Histogram of attractiveness scores by plant type
def beta_scores_by_plant_type(weighted=1):
    beta_normalized = weighted_beta_normalized if weighted else unweighted_beta_normalized

    bins = np.linspace(min(beta_normalized), max(beta_normalized), 10)
    
    normalized_invasive_betas = [beta_normalized[id_to_idx[key]] for key, value in invasive_map.items() if value == 1]
    normalized_non_invasive_betas = [beta_normalized[id_to_idx[key]] for key, value in invasive_map.items() if value == 0]
    
    hist_invasive, edges_invasive = np.histogram(normalized_invasive_betas, bins=bins)
    hist_non_invasive, edges_non_invasive = np.histogram(normalized_non_invasive_betas, bins=bins)
    
    plot = figure(height=600, sizing_mode="stretch_width",
            title="Histogram of Normalized Attractiveness Scores",
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


# 4. Wins/Losses bar chart
def win_loss_by_image(weighted=1):
    images = [all_plants[id] for id in image_ids]
    
    wins = [int((data['winner'] == id).sum()) for id in image_ids]
    losses = [int((data['loser'] == id).sum()) for id in image_ids]

    source = ColumnDataSource(data=dict(
        images=images,
        wins=wins,
        losses=losses
    ))
    
    plot = figure(x_range=images, height=600, sizing_mode="stretch_width", title="Wins/Losses per Image")

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
