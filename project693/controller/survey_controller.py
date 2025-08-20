from flask import request, render_template, redirect, url_for, session, flash
from project693.controller import app
from project693.utils.session_manager import SessionManager
from project693.dao.plant_dao import PlantDAO
from project693.dao.survey_dao import SurveyDAO
from project693.model.survey import SurveyMetadata, SurveyAnswer
import uuid


plant_dao = PlantDAO()
survey_dao = SurveyDAO()


@app.route("/survey/", methods=["GET", "POST"])
def survey():
    if request.method == "GET":
        return render_template("survey_intro.html")
    
    
    

    # POST method – user submitted intro form
    session["session_id"] = str(uuid.uuid4())  # new session
    session["question_number"] = 1
    session["answers"] = []

    # Save form metadata
    has_garden = request.form.get("has_garden") == "yes"
    age_range = request.form.get("age_range")

    # Save metadata with placeholder reasoning
    metadata = SurveyMetadata(
        session_id=session["session_id"],
        has_garden=has_garden,
        age=age_range,
        reasoning=None
    )
    survey_dao.save_metadata(metadata)

    # Start tracking pairs
    SessionManager.set("used_invasive", [])
    SessionManager.set("used_non_invasive", [])

    pair = plant_dao.get_random_pair([], [])
    if not pair:
        flash("Not enough plants in the database!", "warning")
        return redirect(url_for("list_plants"))

    SessionManager.set("last_pair", [pair[0].id, pair[1].id])

    return render_template("survey.html", pair=pair, question_number=1)


@app.route("/survey/next/", methods=["GET"])
def survey_next_get():
    if "session_id" not in session:
        return redirect(url_for("survey"))

    qn = session.get("question_number", 1)

    if qn == 11:
        return render_template("survey_questionnaire.html")

    used_invasive = SessionManager.get("used_invasive") or []
    used_non_invasive = SessionManager.get("used_non_invasive") or []

    pair = plant_dao.get_random_pair(
        used_invasive_ids=used_invasive,
        used_non_invasive_ids=used_non_invasive
    )

    if not pair:
        flash("Not enough plants left to continue the survey.", "warning")
        return redirect(url_for("list_plants"))

    SessionManager.set("last_pair", [pair[0].id, pair[1].id])
    
    print(qn)

    return render_template("survey.html", pair=pair, question_number=qn)

@app.route("/survey/next/", methods=["POST"])
def survey_next():
    if "session_id" not in session:
        return redirect(url_for("survey"))

    # Selected image id
    selected_id = request.form.get("selected_id")
    session_id = session.get("session_id")
    
    # 2 image ids in this choice
    image_1_id = request.form.get("image_1_id")
    image_2_id = request.form.get("image_2_id")

    # Current question number
    qn = session.get("question_number", 1)

    # Save answer
    answer = SurveyAnswer(
        session_id=session_id,
        question_number=qn,
        selected_plant_id=selected_id,
        image_1_id=image_1_id,
        image_2_id=image_2_id
    )
    survey_dao.survey_answer(answer)

    # Update answers list
    answers = SessionManager.get("answers") or []
    answers.append(selected_id)
    SessionManager.set("answers", answers)

    # Update used plants list
    used_invasive = SessionManager.get("used_invasive") or []
    used_non_invasive = SessionManager.get("used_non_invasive") or []
    last_pair = SessionManager.get("last_pair") or []

    for comp_id in last_pair:
        plant = plant_dao.get_plant_by_id(int(comp_id))
        if plant.invasiveness == 'invasive':
            if plant.id not in used_invasive:
                used_invasive.append(plant.id)
        else:
            if plant.id not in used_non_invasive:
                used_non_invasive.append(plant.id)

    SessionManager.set("used_invasive", used_invasive)
    SessionManager.set("used_non_invasive", used_non_invasive)

    # Increment question number
    session["question_number"] = qn + 1

    # Redirect to GET route to show next question
    return redirect(url_for("survey_next_get"))


@app.route("/survey/questionnaire/", methods=["POST"])
def survey_questionnaire():
    reasoning = request.form.get("reasoning")
    session_id = session.get("session_id")

    # Save reasoning as question 10
    survey_dao.update_reasoning(
    session_id=session_id,
    reasoning=reasoning
    )

    # Get all selected answers from session
    answers = SessionManager.get("answers") or []

    # Count invasive vs non-invasive
    invasive_count = 0
    non_invasive_count = 0

    for plant_id in answers:
        plant = plant_dao.get_plant_by_id(int(plant_id))
        if plant.invasiveness == 'invasive':
            invasive_count += 1
        else:
            non_invasive_count += 1

    total = invasive_count + non_invasive_count
    invasive_percent = round((invasive_count / total) * 100, 1) if total else 0
    non_invasive_percent = round((non_invasive_count / total) * 100, 1) if total else 0

     # Decide message
    if non_invasive_count >= 5:
        message = "Well done! You have a preference for native species. You're helping conserve New Zealand Biodiversity."
    elif invasive_count >= 5:
        message = "Be careful! You’re choosing non-native species and these can chomp the garden fence."
    else:
        message = "Thanks for your input! Your preferences have been recorded."

    # Clear session
    SessionManager.remove("question_number")
    SessionManager.remove("answers")
    SessionManager.remove("reasoning")
    SessionManager.remove("used_invasive")
    SessionManager.remove("used_non_invasive")
    session.pop("session_id", None)

    return render_template(
        "survey_complete.html",
        invasive_percent=invasive_percent,
        non_invasive_percent=non_invasive_percent,
        message=message
    )