from flask import Flask
from flask import render_template
from flask import g, request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash, abort
from project693.controller import app
from project693.dao.user_dao import UserDao
from project693.model import User
from datetime import datetime
from project693.utils.hash_utils import get_password_hash
from project693.model import enums
from project693.utils.session_manager import SessionManager
import re
import json

# visitor's access paths
exempt_routes_patterns = [
    r"^/home/.*$",
    r"^/login/.*$",
    r"^/logout/$",
    r"^/about_us/$",
    r"^/static/.*$",
    r"^/survey/$",
    r"^/survey/next/$",
    r"^/survey/questionnaire/$",
    r"^/survey/choice-summary/$",
    r"^/survey/plant-info$",
    r"^/favicon.ico$",
    r"^/misc/.*$",
    # r"^/dashboard/.*$",
]


def is_exempt_route(path):
    return any(re.match(pattern, path) for pattern in exempt_routes_patterns)


# role and permission mapping
role_permissions = {
    "siteadmin": [
        r"^/siteadmin/.*$",
        r"^/dashboard/.*$",         # dashboard page
        r"^/api/.*$",               # api
    ],
}


def is_allowed(role, path):
    return any(re.match(pattern, path) for pattern in role_permissions.get(role.value))


@app.before_request
def before_request():
    # Store user data in g.user if login
    if SessionManager.USER in session:
        user_dao = UserDao()
        user_id = session.get("user_id")
        result = user_dao.get_user_details(user_id)

        if result.status == enums.Status.INACTIVE:
            session.pop(SessionManager.USER, None)
            session.pop("login_username", None)
            session.pop("login_password", None)
            session.pop("user_role", None)
            session.pop("env", None)
            return redirect(url_for("login"))

        SessionManager.set(SessionManager.USER, result.to_dict())
        g.user = User.from_dict(SessionManager.get(SessionManager.USER))
    else:
        g.user = None

    if request.path == "/":
        return redirect(url_for("site_home"))

    # if the request path is not in exempt_route, check if the user has logged in
    if not is_exempt_route(request.path):
        if SessionManager.USER not in session:
            session["next_url"] = request.url
            return redirect(url_for("login"))
        else:
            # if the user is logged in, check if the user has access permission
            user = User.from_dict(SessionManager.get(SessionManager.USER))
            if not is_allowed(user.role, request.path):
                abort(403)


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # if the user has already logged in, navigate to the home page
        if SessionManager.USER in session:
            return redirect(url_for("site_home"))

        session["previous_page"] = (
            request.referrer
            if request.referrer != url_for("login")
            else None
        )
        
        login_username = session.get("login_username", "")
        login_password = session.get("login_password", "")
        SessionManager.set(SessionManager.ACTIVE_PAGE, SessionManager.Page.LOGIN.value)
        return render_template(
            "auth/login.html",
            login_username=login_username,
            login_password=login_password,
        )
    else:
        login_username = request.form.get("login_username")
        login_password = request.form.get("login_password")
        session["login_username"] = login_username
        session["login_password"] = login_password
        user_dao = UserDao()
        result, message = user_dao.authenticate_user(login_username, login_password)
        if result is None:
            flash(message)
            return redirect(url_for("login"))
        else:
            SessionManager.set(SessionManager.USER, result.to_dict())
            session["user_role"] = result.role.value
            session["user_id"] = result.id
            session["env"] = app.env

            # previous_page = session.get("previous_page") or session.pop(
            #     "next_url", url_for("site_home")
            # )
            return redirect(url_for("site_home"))


@app.route("/logout/", methods=["GET"])
def logout():
    session.pop(SessionManager.USER, None)
    session.pop("login_username", None)
    session.pop("login_password", None)
    session.pop("user_role", None)
    session.pop("env", None)
    return redirect(url_for("site_home"))