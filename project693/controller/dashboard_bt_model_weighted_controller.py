from flask import Flask, request, render_template, redirect, url_for, flash, session
from project693.controller import app
from werkzeug.utils import secure_filename
from project693.dao.plant_dao import PlantDAO
from project693.utils.session_manager import SessionManager
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, Select, NumeralTickFormatter
from bokeh.resources import CDN
import pandas as pd

@app.route("/dashboard/bt-model-weighted", methods=["GET", "POST"])
def bt_model_weighted():
    SessionManager.set(
        SessionManager.ACTIVE_PAGE, SessionManager.Page.DASHBOARD.value
    )

    if request.method == "POST":
        pass
        return redirect(url_for("list_plants"))
    
    # Sample dataset
    # df = pd.DataFrame({
    #     "category": ["A", "A", "A", "B", "B", "B"],
    #     "x": [1, 2, 3, 1, 2, 3],
    #     "y": [4, 5, 6, 7, 6, 5]
    # })

    # Selected category from form
    # selected_category = request.form.get("category", "A")
    # selected_category = "A"
    # filtered_df = df[df["category"] == selected_category]

    # source1 = ColumnDataSource(filtered_df)
    # source2 = ColumnDataSource(filtered_df)

    # Plot 1: Line chart
    # plot = figure(height=450, sizing_mode="stretch_width", title=f"Line Plot - Category {selected_category}")
    # plot.line("x", "y", source=source1, line_width=2)

    # Plot 2: Scatter plot
    # plot2 = figure(height=450, sizing_mode="stretch_width", title="Scatter Plot")
    # plot2.circle("x", "y", source=source2, size=10, color="green")

    # Layout
    # layout = column(
    #     row(plot1, plot2)
    # )

    # Embed Bokeh in Flask
    # script, div = components(layout)
    
    categories = ["Invasive", "Non-Invasive"]
    values = [85, 15]
    colors = ["#F15F36", "#19A0AA"]
    
    total = sum(values)
    percentages = [v / total for v in values]
    
    source = ColumnDataSource(data=dict(categories=categories, percentages=percentages, colors=colors))
    plot = figure(x_range=categories, height=450, sizing_mode="stretch_width", toolbar_location="above")
    plot.vbar(x="categories", top="percentages", width=0.6, source=source, color="colors")
    plot.yaxis.formatter = NumeralTickFormatter(format="0%")
    
    # plot.xaxis.axis_label_text_font_size = "50pt"
    # plot.yaxis.axis_label_text_font_size = "50pt"
    
    plot.xaxis.major_label_text_font_size = "12pt"
    plot.yaxis.major_label_text_font_size = "12pt"
    
    script, div = components(plot)
    
    return render_template("dashboard/dashboard.html", script=script, div=div, current_page="bt_model_weighted")
