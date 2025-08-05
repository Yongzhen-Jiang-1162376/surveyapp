from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select
from bokeh.resources import CDN
import pandas as pd

@app.route("/dashboard/", methods=["GET", "POST"])
def dashboard():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )

    if request.method == "POST":
        pass
        return redirect(url_for("list_plants"))
    
    # Sample dataset
    df = pd.DataFrame({
        "category": ["A", "A", "A", "B", "B", "B"],
        "x": [1, 2, 3, 1, 2, 3],
        "y": [4, 5, 6, 7, 6, 5]
    })

    # Selected category from form
    # selected_category = request.form.get("category", "A")
    selected_category = "A"
    filtered_df = df[df["category"] == selected_category]

    source = ColumnDataSource(filtered_df)

    # Plot 1: Line chart
    plot1 = figure(height=300, width=400, title=f"Line Plot - Category {selected_category}")
    plot1.line("x", "y", source=source, line_width=2)

    # Plot 2: Scatter plot
    plot2 = figure(height=300, width=400, title="Scatter Plot")
    plot2.circle("x", "y", source=source, size=10, color="green")

    # Layout
    layout = column(
        row(plot1, plot2)
    )

    # Embed Bokeh in Flask
    script, div = components(layout)
    
    return render_template("dashboard/dashboard.html", script=script, div=div)
