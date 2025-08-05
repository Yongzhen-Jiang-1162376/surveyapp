from flask import session
from enum import Enum


class SessionManager:
    # Session keys as constants
    USER = "user"
    ACTIVE_PAGE = "active_page"

    class Page(Enum):
        HOME = "home"
        LOGIN = "login"
        USER_PROFILE = "user_profile"
        SITE_MANAGEMENT = "site_management"
        SITEHOME = "site_home"
        ADDPLANT = "add_plant"
        LISTPLANTS = "list_plants"
        DASHBOARD = "dashboard"
        LIST_IMAGE_VARIATIONS = "list_image_variations"

    @staticmethod
    def set(key, value):
        """set session variable"""
        session[key] = value

    @staticmethod
    def get(key):
        """get session variable"""
        return session.get(key)

    @staticmethod
    def remove(key):
        """remove session variable"""
        if key in session:
            del session[key]

    @staticmethod
    def clear():
        """clear all session variable"""
        session.clear()