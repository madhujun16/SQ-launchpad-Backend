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

CREATE TABLE IF NOT EXISTS software_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hardware_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS software_modules (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  category_id INT NOT NULL,
  license_fee DECIMAL(10, 2) NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES software_categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hardware_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NULL,
  category_id INT NOT NULL,
  subcategory VARCHAR(255) NULL,
  manufacturer VARCHAR(255) NULL,
  configuration_notes TEXT NULL,
  unit_cost DECIMAL(10, 2) NOT NULL,
  support_type VARCHAR(255) NULL,
  support_cost DECIMAL(10, 2) NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_by VARCHAR(255) NULL,
  updated_by VARCHAR(255) NULL,
  FOREIGN KEY (category_id) REFERENCES hardware_categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recommendation_rules (
  id INT AUTO_INCREMENT PRIMARY KEY,
  software_category_id INT NOT NULL,
  hardware_category_id INT NOT NULL,
  is_mandatory BOOLEAN DEFAULT FALSE,
  quantity INT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (software_category_id) REFERENCES software_categories(id) ON DELETE CASCADE,
  FOREIGN KEY (hardware_category_id) REFERENCES hardware_categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scoping_approvals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  site_id INT NOT NULL,
  site_name VARCHAR(255) NOT NULL,
  deployment_engineer_id INT NOT NULL,
  deployment_engineer_name VARCHAR(255) NOT NULL,
  ops_manager_id INT NULL,
  ops_manager_name VARCHAR(255) NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  reviewed_at DATETIME NULL,
  reviewed_by INT NULL,
  review_comment TEXT NULL,
  rejection_reason TEXT NULL,
  scoping_data JSON NOT NULL,
  cost_breakdown JSON NOT NULL,
  version INT NOT NULL DEFAULT 1,
  previous_version_id INT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE,
  FOREIGN KEY (deployment_engineer_id) REFERENCES users(id),
  FOREIGN KEY (ops_manager_id) REFERENCES users(id),
  FOREIGN KEY (reviewed_by) REFERENCES users(id),
  FOREIGN KEY (previous_version_id) REFERENCES scoping_approvals(id),
  INDEX idx_scoping_approvals_site_id (site_id),
  INDEX idx_scoping_approvals_status (status),
  INDEX idx_scoping_approvals_deployment_engineer_id (deployment_engineer_id)
);

CREATE TABLE IF NOT EXISTS approval_actions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  approval_id INT NOT NULL,
  action VARCHAR(50) NOT NULL,
  performed_by INT NOT NULL,
  performed_by_role VARCHAR(50) NOT NULL,
  performed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  comment TEXT NULL,
  action_metadata JSON NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (approval_id) REFERENCES scoping_approvals(id) ON DELETE CASCADE,
  FOREIGN KEY (performed_by) REFERENCES users(id),
  INDEX idx_approval_actions_approval_id (approval_id)
);

CREATE TABLE IF NOT EXISTS procurement_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    site_id INT NOT NULL,
    delivery_date DATE NULL,
    delivery_receipt_url VARCHAR(500) NULL,
    summary TEXT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    completed_at DATETIME NULL,
    completed_by INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE,
    FOREIGN KEY (completed_by) REFERENCES users(id),
    UNIQUE KEY unique_site_procurement (site_id),
    INDEX idx_procurement_data_site_id (site_id),
    INDEX idx_procurement_data_status (status)
);

CREATE TABLE IF NOT EXISTS go_live_data (
  id INT AUTO_INCREMENT PRIMARY KEY,
  site_id INT NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'offline',
  go_live_date DATETIME NULL,
  signed_off_by INT NULL,
  notes TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (site_id) REFERENCES site(id) ON DELETE CASCADE,
  FOREIGN KEY (signed_off_by) REFERENCES users(id),
  UNIQUE KEY unique_site_go_live (site_id),
  INDEX idx_go_live_data_site_id (site_id),
  INDEX idx_go_live_data_status (status)
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
