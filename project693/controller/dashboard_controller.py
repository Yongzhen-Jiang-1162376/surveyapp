from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.analysis_dao import AnalysisDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select, NumeralTickFormatter
from bokeh.resources import CDN
import pandas as pd
import json


analysis_dao = AnalysisDAO()


@app.route("/dashboard/", methods=["GET", "POST"])
def dashboard():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )

    if request.method == "POST":
        pass
        return redirect(url_for("list_plants"))
    
    categories = ["Invasive", "Non-Invasive"]
    # values = [85, 15]
    values = [[int(r[0]), int(r[1])] for r in analysis_dao.list_choice_count()][0]
    
    print(values)
    colors = ["#FFC000", "#00B050"]
    
    total = sum(values)
    percentages = [v / total for v in values]
    
    percentages_display = [round(100 * percentages[0], 2), 100 - round(100 * percentages[0], 2)]
    
    source = ColumnDataSource(data=dict(categories=categories, percentages=percentages, colors=colors))
    plot = figure(x_range=categories, height=450, sizing_mode="stretch_width", toolbar_location="above")
    plot.vbar(x="categories", top="percentages", width=0.6, source=source, color="colors")
    plot.yaxis.formatter = NumeralTickFormatter(format="0%")
    
    plot.xaxis.major_label_text_font_size = "12pt"
    plot.yaxis.major_label_text_font_size = "12pt"
    
    script, div = components(plot)
    
    
    # data table
    rows = analysis_dao.list_current_survey_results_with_plant_name()
    print(rows)
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
    
    data = {
        'percentages': percentages_display,
        'count': values,
        'datatable': json.dumps(datatable)
    }
    
    print(datatable)
    
    return render_template("dashboard/dashboard.html", script=script, div=div, data=data, current_page="dashboard")
