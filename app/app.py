from flask import Flask, render_template, jsonify
import mysql.connector
import os
import time

app = Flask(__name__)


# ============================================================
# Database Configuration
# ============================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

# ============================================================
# Database Connection
# ============================================================

def get_db_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        port=DB_CONFIG["port"],
        connection_timeout=5
    )


# ============================================================
# Frontend
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# Health Check
# ============================================================

@app.route("/health")
def health():

    try:

        connection = get_db_connection()

        if connection.is_connected():
            connection.close()

            return jsonify({
                "status": "healthy"
            }), 200

    except Exception:

        return jsonify({
            "status": "unhealthy"
        }), 503

    return jsonify({
        "status": "unhealthy"
    }), 503


# ============================================================
# Users API
# ============================================================

@app.route("/api/users")
def get_users():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                name,
                role
            FROM users
            ORDER BY id
        """)

        users = cursor.fetchall()

        return jsonify({
            "users": users
        }), 200

    except Exception as e:

        app.logger.error(
            "Database error: %s",
            e
        )

        return jsonify({
            "error": "Unable to retrieve users"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ============================================================
# Application Status
# ============================================================

@app.route("/api/status")
def status():

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )

        user_count = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return jsonify({

            "application": "Fluid AI DevOps Demo",

            "status": "Running",

            "backend": "Flask",

            "database": "MySQL",

            "database_status": "Connected",

            "users": user_count

        }), 200

    except Exception as e:

        app.logger.error(
            "Database connection error: %s",
            e
        )

        return jsonify({

            "application": "Fluid AI DevOps Demo",

            "status": "Running",

            "backend": "Flask",

            "database": "MySQL",

            "database_status": "Disconnected",

            "users": 0

        }), 503


# ============================================================
# Application Startup
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
