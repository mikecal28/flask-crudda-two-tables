# Homework: 9/22/2022

# Finish the User CRUDDA operations and endpoints

# Create Organization CRUDDA operations and endpoints
# - Add Org
# - Update Org
# - Get Org by ID
# - Get all orgs
# - Delete org
# - Activate org
# - Deactivate org

# Add the "organization" dictionary to the get user by id results so instead of:
# {
#     "active": 1,
#     "city": "Orem",
#     "email": "jason@devpipeline.com",
#     "first_name": "Jason",
#     "last_name": "Fletcher",
#     "org_id": 1,
#     "phone": "8014044268",
#     "state": "UT",
#     "user_id": 1
# },
# it would return organization data in a sub dictionary, if it exists:
#         {
#             "active": 1,
#             "city": "Orem",
#             "email": "jason@devpipeline.com",
#             "first_name": "Jason",
#             "last_name": "Fletcher",
#             "org_id": 1,
#             "organization": {
#                 "org_id": 1,
#                 "name": "DevPipeline",
#                 "city": "Orem",
#                 "state": "UT",
#                 "phone": "3853090807",
#                 "active": 1
#             },
#             "phone": "8014044268",
#             "state": "UT",
#             "user_id": 1
#         }


# ASSIGNMENT START:

import psycopg2
from flask import Flask, request, jsonify
from pprint import pprint

# CREATES APP
app = Flask(__name__)

conn = psycopg2.connect("dbname='usermgt' user='mike' host='localhost'")
cursor = conn.cursor()


def create_all():
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS Users (
         user_id SERIAL PRIMARY KEY,
         first_name VARCHAR NOT NULL,
         last_name VARCHAR,
         email VARCHAR NOT NULL UNIQUE,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         org_id int,
         active smallint
      );
   """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS Organizations (
         org_id SERIAL PRIMARY KEY,
         name VARCHAR NOT NULL,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         active smallint
      );
   """
    )
    print("Creating tables...")
    conn.commit()


# GET USERS BY ID
@app.route("/user/get/<user_id>", methods=["GET"])
def get_users_by_id(user_id):
    result = cursor.execute(
        """
   SELECT * FROM users
   WHERE user_id=%s;""",
        [user_id],
    )

    results = cursor.fetchone()

    if results:
        user = {
            "user_id": results[0],
            "first_name": results[1],
            "last_name": results[2],
            "email": results[3],
            "phone": results[4],
            "city": results[5],
            "state": results[6],
            "org_id": results[7],
            "organization": {},
            "active": results[8],
        }

    result = cursor.execute(
        """
   SELECT * FROM organizations
   WHERE org_id=%s;""",
        [results[7]],
    )

    results = cursor.fetchone()

    if results:
        user["organization"] = {
            "org_id": results[0],
            "name": results[1],
            "phone": results[2],
            "city": results[3],
            "state": results[4],
            "active": results[5],
        }

        return jsonify(user)
    else:
        return jsonify("No user found")


# GETS ALL ACTIVE USERS
@app.route("/user/get/all", methods=["GET"])
def get_all_active_users():
    results_list = []
    result = cursor.execute(
        """
   SELECT * FROM users
      WHERE active=1"""
    )
    results = cursor.fetchall()
    if results:
        for tuple in results:
            user = {
                "user_id": tuple[0],
                "first_name": tuple[1],
                "last_name": tuple[2],
                "email": tuple[3],
                "phone": tuple[4],
                "city": tuple[5],
                "state": tuple[6],
                "org_id": tuple[7],
                "active": tuple[8],
            }
            results_list.append(user)
            user = {}

        return jsonify(results_list)

    else:
        return jsonify("No users found")


# ADDING A USER
def add_user(first_name, last_name, email, phone, city, state, org_id, active):
    cursor.execute(
        f"""
      INSERT INTO users
         (first_name, last_name, email, phone, city, state, org_id, active)
         VALUES
         (%s, %s, %s, %s, %s, %s, %s, %s);""",
        (first_name, last_name, email, phone, city, state, org_id, active),
    )
    conn.commit()


@app.route("/user/add", methods=["POST"])
def user_add():
    post_data = request.get_json()
    first_name = post_data.get("first_name")
    last_name = post_data.get("last_name")
    email = post_data.get("email")
    phone = post_data.get("phone")
    city = post_data.get("city")
    state = post_data.get("state")
    org_id = post_data.get("org_id")
    active = post_data.get("active")

    response = add_user(
        first_name, last_name, email, phone, city, state, org_id, active
    )

    return jsonify("Good job")


# UPDATING A USER
@app.route("/user/update/<user_id>", methods=["POST"])
def user_update(user_id):
    update_fields = []
    update_values = []
    field_names = [
        "user_id",
        "first_name",
        "last_name",
        "email",
        "city",
        "state",
        "org_id",
        "active",
    ]
    values = []

    post_data = request.get_json()

    for field in field_names:
        field_value = post_data.get(field)
        if field_value:
            update_fields.append(str(field) + "=%s")
            update_values.append(field_value)

    if update_fields:
        update_values.append(user_id)
        query_string = (
            f"UPDATE users SET " + ", ".join(update_fields) + f"WHERE user_id=%s"
        )
        cursor.execute(query_string, update_values)
        conn.commit()

        return jsonify("User Updated"), 200
    else:
        return jsonify("No values sent in body"), 418


# DELETING A USER
@app.route("/user/delete/<user_id>", methods=["DELETE"])
def user_delete(user_id):
    result = cursor.execute(
        """
   SELECT * FROM users
   WHERE user_id=%s;""",
        [user_id],
    )

    results = cursor.fetchone()

    if results:

        query_string = f"DELETE FROM users WHERE user_id=%s"
        cursor.execute(query_string, [user_id])
        conn.commit()

        return jsonify("User Deleted"), 200
    else:
        return jsonify("User does not exist"), 418


# DEACTIVATING A USER
@app.route("/user/deactivate/<user_id>", methods=["PATCH"])
def user_deactivate(user_id):
    result = cursor.execute(
        """
   SELECT * FROM users
   WHERE user_id=%s;""",
        [user_id],
    )

    results = cursor.fetchone()

    if results:
        if str(results[8]) == "1":

            query_string = f"UPDATE users SET active=0 WHERE user_id=%s"
            cursor.execute(query_string, [user_id])
            conn.commit()

        else:
            return jsonify("User is already inactive"), 418

        return jsonify("User Deactivated"), 200
    else:
        return jsonify("User not found"), 418


# ACTIVATING A USER
@app.route("/user/activate/<user_id>", methods=["PATCH"])
def user_activate(user_id):
    result = cursor.execute(
        """
   SELECT * FROM users
   WHERE user_id=%s;""",
        [user_id],
    )

    results = cursor.fetchone()

    if results:
        if str(results[8]) == "0":

            query_string = f"UPDATE users SET active=1 WHERE user_id=%s"
            cursor.execute(query_string, [user_id])
            conn.commit()

        else:
            return jsonify("User is already active"), 418

        return jsonify("User Activated"), 200
    else:
        return jsonify("User not found"), 418


# ADDING AN ORGANIZATION
def add_organization(name, phone, city, state, active):
    cursor.execute(
        f"""
      INSERT INTO organizations
         (name, phone, city, state, active)
         VALUES
         (%s, %s, %s, %s, %s);""",
        (name, phone, city, state, active),
    )
    conn.commit()


@app.route("/organization/add", methods=["POST"])
def organization_add():
    post_data = request.get_json()
    name = post_data.get("name")
    phone = post_data.get("phone")
    city = post_data.get("city")
    state = post_data.get("state")
    active = post_data.get("active")

    response = add_organization(name, phone, city, state, active)

    return jsonify("Good job")


# GETS ALL ACTIVE ORGANIZATIONS
@app.route("/organization/get/all", methods=["GET"])
def get_all_active_organizations():
    results_list = []
    result = cursor.execute(
        """
   SELECT * FROM organizations
      WHERE active=1"""
    )
    results = cursor.fetchall()
    if results:
        for tuple in results:
            organization = {
                "org_id": tuple[0],
                "name": tuple[1],
                "phone": tuple[2],
                "city": tuple[3],
                "state": tuple[4],
                "active": tuple[5],
            }
            results_list.append(organization)
            organization = {}

        return jsonify(results_list)

    else:
        return jsonify("No organizations found")


# UPDATING AN ORGANIZATION
@app.route("/organization/update/<org_id>", methods=["POST"])
def organization_update(org_id):
    update_fields = []
    update_values = []
    field_names = [
        "org_id",
        "name",
        "phone",
        "city",
        "state",
        "active",
    ]
    values = []

    post_data = request.get_json()

    for field in field_names:
        field_value = post_data.get(field)
        if field_value:
            update_fields.append(str(field) + "=%s")
            update_values.append(field_value)

    if update_fields:
        update_values.append(org_id)
        query_string = (
            f"UPDATE organizations SET " + ", ".join(update_fields) + f"WHERE org_id=%s"
        )
        cursor.execute(query_string, update_values)
        conn.commit()

        return jsonify("Organization Updated"), 200
    else:
        return jsonify("No values sent in body"), 418


# DELETING AN ORGANIZATION
@app.route("/organization/delete/<org_id>", methods=["DELETE"])
def organization_delete(org_id):
    result = cursor.execute(
        """
   SELECT * FROM organizations
   WHERE org_id=%s;""",
        [org_id],
    )

    results = cursor.fetchone()

    if results:

        query_string = f"DELETE FROM organizations WHERE org_id=%s"
        cursor.execute(query_string, [org_id])
        conn.commit()

        return jsonify("Organization Deleted"), 200
    else:
        return jsonify("Organization does not exist"), 418


# DEACTIVATING AN ORGANIZATION
@app.route("/organization/deactivate/<org_id>", methods=["PATCH"])
def organization_deactivate(org_id):
    result = cursor.execute(
        """
   SELECT * FROM organizations
   WHERE org_id=%s;""",
        [org_id],
    )

    results = cursor.fetchone()

    if results:
        if str(results[5]) == "1":

            query_string = f"UPDATE organizations SET active=0 WHERE org_id=%s"
            cursor.execute(query_string, [org_id])
            conn.commit()

        else:
            return jsonify("Organization is already inactive"), 418

        return jsonify("Organization Deactivated"), 200
    else:
        return jsonify("Organization not found"), 418


# ACTIVATING AN ORGANIZATION
@app.route("/organization/activate/<org_id>", methods=["PATCH"])
def organization_activate(org_id):
    result = cursor.execute(
        """
   SELECT * FROM organizations
   WHERE org_id=%s;""",
        [org_id],
    )

    results = cursor.fetchone()

    if results:
        if str(results[5]) == "0":

            query_string = f"UPDATE organizations SET active=1 WHERE org_id=%s"
            cursor.execute(query_string, [org_id])
            conn.commit()

        else:
            return jsonify("Organization is already active"), 418

        return jsonify("Organization Activated"), 200
    else:
        return jsonify("Organization not found"), 418


# INITIALIZES APP
if __name__ == "__main__":
    create_all()
    app.run(debug=True, port="5000")
