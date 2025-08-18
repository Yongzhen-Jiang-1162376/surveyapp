from flask import session
from project693.dao.base_dao import BaseDAO
from project693.model import User
from project693.model import enums
from project693.utils.hash_utils import get_password_hash
from project693.model.enums import (
    Role,
    Status,
)
import json


class UserDao(BaseDAO):
    def __init__(self) -> None:
        super().__init__()

    def authenticate_user(self, user_name, password):
        query = (
            r"select id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status"
            " from users where username = %s and password_hash = %s"
        )

        result = self.execute_query(query, (user_name, get_password_hash(password)))
        if len(result) > 0:
            # Convert role, status, and voting_permission to enums
            role_enum = enums.Role[result[0][9].upper()]
            status_enum = enums.Status[result[0][10].upper()]

            # Create the User object
            user = User(
                id=result[0][0],
                username=result[0][1],
                password_hash=result[0][2],
                email=result[0][3],
                first_name=result[0][4],
                last_name=result[0][5],
                location=result[0][6],
                description=result[0][7],
                avatar=result[0][8],
                role=role_enum,  # Pass role as enum
                status=status_enum,  # Pass status as enum
            )

            if user.status == enums.Status.ACTIVE:
                return user, ""
            else:
                return (
                    None,
                    "Your account has been deactivated. Please contact an admin.",
                )
        else:
            return None, "Invalid username or password. Please try again."

    def get_user_details(self, user_id):
        query = (
            r"select id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status"
            " from users where id = %s"
        )

        result = self.execute_query(query, (user_id,))
        if len(result) > 0:
            # Convert role, status to enums
            role_enum = enums.Role[result[0][9].upper()]
            status_enum = enums.Status[result[0][10].upper()]

            # Create the User object
            user = User(
                id=result[0][0],
                username=result[0][1],
                password_hash=result[0][2],
                email=result[0][3],
                first_name=result[0][4],
                last_name=result[0][5],
                location=result[0][6],
                description=result[0][7],
                avatar=result[0][8],
                role=role_enum,  # Pass role as enum
                status=status_enum,  # Pass status as enum
            )

            return user


    def find_by_email(self, email):
        query = "SELECT * FROM users WHERE email = %s"
        result = self.execute_query(query, (email,))

        if len(result) > 0:
            row = result[0]

            # Access values using tuple indices
            return User(
                id=row[0],  # 'id' column
                username=row[1],  # 'username' column
                password_hash=row[2],  # 'password_hash' column
                email=row[3],  # 'email' column
                first_name=row[4],  # 'first_name' column
                last_name=row[5],  # 'last_name' column
                location=row[6],  # 'location' column
                description=row[7],  # 'description' column
                avatar=row[8],  # 'avatar' column
                role=Role[row[9].upper()],  # Convert string to Role enum
                status=Status[row[10].upper()],  # Convert string to Status enum
            )
        return None

    def find_by_id(self, user_id):
        query = "select id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status from users where id = %s"
        result = self.execute_query(query, (user_id,))

        if result:
            user_data = result[0]
            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                first_name=user_data[4],
                last_name=user_data[5],
                location=user_data[6],
                description=user_data[7],
                avatar=user_data[8],
                role=enums.Role(user_data[9]),
                status=enums.Status(user_data[10]),
            )

        return None

    def update_user(self, user: User):
        query = (
            "update users set username = %s, password_hash = %s, email = %s, first_name = %s, last_name = %s, "
            "location = %s, description = %s, avatar = %s, role = %s, status = %s where id = %s"
        )
        self.execute_non_query(
            query,
            (
                user.username,
                user.password_hash,
                user.email,
                user.first_name,
                user.last_name,
                user.location,
                user.description,
                user.avatar,
                user.role.value,
                user.status.value,
                user.id,
            ),
        )


    def update_backend_user(
        self,
        user_id,
        username=None,
        email=None,
        first_name=None,
        last_name=None,
        location=None,
        description=None,
    ):
        query = "UPDATE users SET "
        params = []

        if username is not None:
            query += "username = %s, "
            params.append(username)
        if email is not None:
            query += "email = %s, "
            params.append(email)
        if first_name is not None:
            query += "first_name = %s, "
            params.append(first_name)
        if last_name is not None:
            query += "last_name = %s, "
            params.append(last_name)
        if location is not None:
            query += "location = %s, "
            params.append(location)
        if description is not None:
            query += "description = %s, "
            params.append(description)

        query = query.rstrip(", ")
        query += " WHERE id = %s"
        params.append(user_id)

        self.execute_non_query(query, params)

    def find_by_username(self, username):
        query = """
            SELECT id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status 
            FROM users 
            WHERE username = %s
        """
        result = self.execute_query(query, (username,))
        if result:
            user_data = result[0]
            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                first_name=user_data[4],
                last_name=user_data[5],
                location=user_data[6],
                description=user_data[7],
                avatar=user_data[8],
                role=enums.Role(user_data[9]),
                status=enums.Status(user_data[10]),
            )
        return None


    def get_full_user_info(self, user_id):
        query = """
            SELECT id, username, password_hash, email, first_name, last_name, location, description, avatar, role, status
            FROM users
            WHERE id = %s
        """
        result = self.execute_query(query, (user_id,))

        if result:
            user_data = result[0]
            role_str = user_data[9]
            role = enums.Role[role_str.upper()]
            status_str = user_data[10]
            status = enums.Status[status_str.upper()]

            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                first_name=user_data[4],
                last_name=user_data[5],
                location=user_data[6],
                description=user_data[7],
                avatar=user_data[8],
                role=role,
                status=status,
            )
        return None