from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.analysis_dao import AnalysisDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select, NumeralTickFormatter, LabelSet
from bokeh.resources import CDN
import pandas as pd
import json


analysis_dao = AnalysisDAO()


@app.route("/dashboard/", methods=["GET"])
def dashboard():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )
    
    categories = ["Invasive", "Non-Invasive"]
    # values = [85, 15]
    values = [[int(r[0]), int(r[1])] for r in analysis_dao.list_choice_count()][0]
    
    colors = ["#FFC000", "#00B050"]
    
    total = sum(values)
    percentages = [v / total for v in values]
    
    percentages_display = ["{:.2f}".format(round(100 * percentages[0], 2)), "{:.2f}".format(100 - round(100 * percentages[0], 2))]
    
    source = ColumnDataSource(data=dict(categories=categories, percentages=percentages, colors=colors))
    
    source.data['labels'] = [f"{p*100:.2f}%" for p in percentages]
    source.data['label_y'] = [p / 2 for p in percentages]
    
    labels = LabelSet(
        x="categories",
        y="label_y",
        text="labels",
        level="glyph",
        x_offset=0,
        y_offset=0,
        source=source,
        text_font_size="28pt",
        text_color="RoyalBlue",
        text_align="center",
        text_baseline="middle"
    )
    
    plot = figure(x_range=categories, height=450, y_range=(0, 1), sizing_mode="stretch_width")
    plot.vbar(x="categories", top="percentages", width=0.5, source=source, color="colors")
    plot.yaxis.formatter = NumeralTickFormatter(format="0%")
    
    plot.xaxis.major_label_text_font_size = "11pt"
    plot.yaxis.major_label_text_font_size = "11pt"
    
    plot.add_layout(labels)
    
    script, div = components(plot)
    
    data = {
        'percentages': percentages_display,
        'count': values
    }
    
    return render_template("dashboard/dashboard.html", script=script, div=div, data=data, current_page="dashboard")
