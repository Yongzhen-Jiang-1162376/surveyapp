"""
Script to generate password hashes for user accounts.

This module provides functionality to hash passwords using a salt.
"""

from collections import namedtuple
from flask import Flask
from flask_hashing import Hashing

PASSWORD_SALT = "d653bda9e01ec6c5b6c36f53d0d2ee4c"

app = Flask(__name__)
hashing = Hashing(app)

# function to generate hash
def get_password_hash(password):
    """
    Generate a hash for the provided password.

    Args:
        password (str): The plain-text password to be hashed.

    Returns:
        str: The hashed password value.
    """
    password_hash = hashing.hash_value(password, PASSWORD_SALT)
    return password_hash

# function to check hash
def check_password_hash( password,password_hash):
    """
    Check if the provided password matches the stored hash.
    """
    return hashing.check_value(password, password_hash, PASSWORD_SALT)
