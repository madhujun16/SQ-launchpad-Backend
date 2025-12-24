import connexion
from . import encoder
import logging
import json
import traceback
from connexion.exceptions import BadRequestProblem, Unauthorized
from .db import db
from flask import Response
from flask_cors import CORS
from flask_session import Session
from sqlalchemy import text
from .utils import messages, common_functions
from .config import db_secrets

logging.basicConfig(level=logging.INFO)

try:
    db_credentials = common_functions.get_pii_encryption_key_from_secrets(
        db_secrets.get("db_credentials")
    )
    if not db_credentials:
        logging.warning("DB credentials not configured in secrets, using environment variables")
        import os
        db_credentials = {
            "username": os.getenv("DB_USERNAME", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "server_ip": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "launchpad_db")
        }
except Exception as e:
    logging.warning(f"Error fetching DB credentials from secrets: {e}. Using environment variables.")
    import os
    db_credentials = {
        "username": os.getenv("DB_USERNAME", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "server_ip": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "launchpad_db")
    }

launchpad_database = db_credentials.get("database", "launchpad_db")

launchpad_db_creation_query = f"""
CREATE DATABASE IF NOT EXISTS {launchpad_database};
USE {launchpad_database};

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role INT NOT NULL,
    last_logged_in DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organization (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NULL,
    sector VARCHAR(100) NOT NULL,
    unit_code VARCHAR(50) NOT NULL UNIQUE,
    organization_logo VARCHAR(512) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site (
    id INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS page (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_name VARCHAR(255) NOT NULL,
    site_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uix_pagename_siteid UNIQUE (page_name, site_id),
    FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS section (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section_name VARCHAR(255) NOT NULL,
    page_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uix_sectionname_pageid UNIQUE (section_name, page_id),
    FOREIGN KEY (page_id) REFERENCES page(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS field (
    id INT AUTO_INCREMENT PRIMARY KEY,
    field_name VARCHAR(255) NOT NULL,
    field_value JSON NULL,
    section_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uix_fieldname_sectionid UNIQUE (field_name, section_id),
    FOREIGN KEY (section_id) REFERENCES section(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS role_permission_map (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL UNIQUE,
    permissions JSON NOT NULL
);
"""

def get_main_app():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Backend API'},
                pythonic_params=True)
    configure_app(app.app)
    register_extensions(app.app)
    logging.info("Initializing launchpad DB creation")
    setup_db_if_not_exists(app.app)
    app.add_error_handler(BadRequestProblem, handle_bad_request)
    app.add_error_handler(Unauthorized, handle_unauthorized_request)
    return app


def configure_app(app):
    try:
        app.config.from_object("app.launchpad.launchpad_api.config.Config")
    except Exception:
        # Fallback for running from app/launchpad directory
        from . import config
        app.config.from_object(config.Config)


def register_extensions(app):
    db.init_app(app)
    Session(app)
    CORS(app, supports_credentials=True)


def handle_bad_request(exception):
    return Response(
        response=json.dumps({'message': messages.generic_message}),
        status=400,
        mimetype="application/json"
    )


def handle_unauthorized_request(exception):
    return Response(
        response=json.dumps({'message': messages.unauthorised_error}),
        status=401,
        mimetype="application/json"
    )


def setup_db_if_not_exists(app):
    try:
        logging.info("Setting up database...")
        with app.app_context():
            if not db_credentials:
                logging.warning("DB credentials not available. Skipping database setup.")
                return False

            try:
                with db.engine.begin() as connection:  # 👈 begin() starts a transaction
                    for query in [q.strip() for q in launchpad_db_creation_query.split(';') if q.strip()]:
                        logging.info(f"Executing query: {query}")
                        try:
                            connection.execute(text(query))
                        except Exception as e:
                            logging.warning(f"Query failed: {query}\n{e}")
                            continue

                logging.info("Database and tables created successfully.")
                return True
            except Exception as e:
                logging.warning(f"Database setup failed (this is OK if database already exists): {e}")
                return False
    except Exception as e:
        logging.warning(f"Database setup failed: {e}")
        logging.info("Continuing without database setup - database may already exist or connection will be established later.")
        return False
