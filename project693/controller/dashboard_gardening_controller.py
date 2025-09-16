from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.analysis_dao import AnalysisDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select, NumeralTickFormatter, FactorRange, LabelSet
from bokeh.resources import CDN
from bokeh.transform import factor_cmap, dodge
import pandas as pd


analysis_dao = AnalysisDAO()

@app.route("/dashboard/analysis-gardening/", methods=["GET"])
def choices_by_gardening():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )
    
    gardening_group_values = analysis_dao.list_survey_gardening_count()
    
    invasive_count_list = []
    non_invasive_count_list = []
    invasive_percentage_list = []
    non_invasive_percentage_list = []
    invasive_percentage_display_list = []
    non_invasive_percentage_display_list = []
    
    
    for group in gardening_group_values:
        invasive_count_list.append(int(group[0]))
        non_invasive_count_list.append(int(group[1]))
        
        if int(group[0]) + int(group[1]) == 0:
            invasive_percentage_list.append(0)
            non_invasive_percentage_list.append(0)
            invasive_percentage_display_list.append(0)
            non_invasive_percentage_display_list.append(0)
        else:
            invasive_perc = float(round(group[0] / (group[0] + group[1]), 2))
            non_invasive_perc = float(round(group[1] / (group[0] + group[1]), 2))
            invasive_percentage_list.append(invasive_perc)
            non_invasive_percentage_list.append(non_invasive_perc)
            invasive_percentage_display_list.append("{:.2f}".format(100 * invasive_perc))
            non_invasive_percentage_display_list.append("{:.2f}".format(100 * non_invasive_perc))
    
    garden_group = ['Gardener', 'Non-Gardener']
    # years = ['Invasive', 'Non-Invasive']

    data = {'garden_group' : garden_group,
            'Invasive'   : invasive_count_list,
            'Non_Invasive'   : non_invasive_count_list,
            'Invasive_Percentage': invasive_percentage_list,
            'Non_Invasive_Percentage': non_invasive_percentage_list,
            'Invasive_Percentage_Display': invasive_percentage_display_list,
            'Non_Invasive_Percentage_Display': non_invasive_percentage_display_list
           }

    source = ColumnDataSource(data=data)
    
    # add label position (centered in the bar)
    source.data['Invasive_Labels'] = [f"{100 * p:.2f}%" for p in invasive_percentage_list]
    source.data['Invasive_Label_Y'] = [p / 2 for p in invasive_percentage_list]
    source.data['Non_Invasive_Labels'] = [f"{100 * p:.2f}%" for p in non_invasive_percentage_list]
    source.data['Non_Invasive_Label_Y'] = [p / 2 for p in non_invasive_percentage_list]
    
    plot = figure(x_range=garden_group, y_range=(0, 1), title="Invasive Choices by Gardening",
            height=450, sizing_mode="stretch_width")

    plot.vbar(x=dodge('garden_group', -0.2, range=plot.x_range), top='Invasive_Percentage', source=source,
        width=0.4, color="#FFC000", legend_label="Invasive")

    plot.vbar(x=dodge('garden_group',  0.2,  range=plot.x_range), top='Non_Invasive_Percentage', source=source,
        width=0.4, color="#00B050", legend_label="Non-Invasive")
    
    plot.xaxis.major_label_text_font_size = "11pt" 
    plot.yaxis.major_label_text_font_size = "11pt"
    
    # Invasive Labels
    labels_invasive = LabelSet(
        x=dodge("garden_group", -0.2, range=plot.x_range),
        y="Invasive_Label_Y",
        text="Invasive_Labels",
        level="glyph",
        source=source,
        text_font_size="18pt",
        text_color="RoyalBlue",
        text_align="center",
        text_baseline="middle"
    )
    plot.add_layout(labels_invasive)
    
    # Non-Invasive Labels
    labels_non_invasive = LabelSet(
        x=dodge("garden_group", 0.2, range=plot.x_range),
        y="Non_Invasive_Label_Y",
        text="Non_Invasive_Labels",
        level="glyph",
        source=source,
        text_font_size="18pt",
        text_color="RoyalBlue",
        text_align="center",
        text_baseline="middle"
    )
    plot.add_layout(labels_non_invasive)
    
    script, div = components(plot)
    
    return render_template("dashboard/dashboard_gardening.html", script=script, div=div, data=data, current_page="gardening")
