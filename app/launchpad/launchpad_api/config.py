import os
import logging
import tempfile
import atexit
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import mysql.connector
from launchpad_api.utils.common_functions import get_pii_encryption_key_from_secrets

load_dotenv()
logging.basicConfig(level=logging.INFO)

# === Secret Manager paths ===
db_secrets = {
    "key": "projects/464251598887/secrets/launchpad_mysql_key/versions/latest",
    "certificate": "projects/464251598887/secrets/launchpad_mysql_certificate/versions/latest",
    "ca": "projects/464251598887/secrets/launchpad_mysql_ca/versions/latest",
    "db_credentials": "projects/464251598887/secrets/launchpad_db_credentials/versions/latest"
}


def create_temp_file(content):
    """Write a secret string to a temporary file and return its path."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
    temp_file.write(content)
    temp_file.flush()
    return temp_file.name


def cleanup_temp_files(file_paths):
    """Remove temp SSL files when app exits."""
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)


def create_database_if_not_exists(connection, database_name):
    """Ensure the given database exists."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"SHOW DATABASES LIKE '{database_name}'")
        if cursor.fetchone():
            logging.info("Database '%s' already exists.", database_name)
        else:
            logging.info("Creating database '%s'...", database_name)
            cursor.execute(f"CREATE DATABASE `{database_name}`")
            logging.info("Database '%s' created successfully.", database_name)
    except mysql.connector.Error as e:
        logging.exception("Error creating database: %s", e)
    finally:
        cursor.close()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    # === Load SSL and DB credentials ===
    # Try to get from Secret Manager, fallback to environment variables
    cert_file_content = get_pii_encryption_key_from_secrets(db_secrets.get("certificate"))
    key_file_content = get_pii_encryption_key_from_secrets(db_secrets.get("key"))
    ca_file_content = get_pii_encryption_key_from_secrets(db_secrets.get("ca"))
    db_credentials = get_pii_encryption_key_from_secrets(db_secrets.get("db_credentials"))

    # Fallback to environment variables if secrets not available
    if not db_credentials:
        db_credentials = {
            "username": os.getenv("DB_USERNAME", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "server_ip": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "launchpad_db")
        }

    username = db_credentials.get("username") if db_credentials else os.getenv("DB_USERNAME", "root")
    password = db_credentials.get("password") if db_credentials else os.getenv("DB_PASSWORD", "")
    server_ip = db_credentials.get("server_ip") if db_credentials else os.getenv("DB_HOST", "localhost")
    database = db_credentials.get("database", "launchpad_db") if db_credentials else os.getenv("DB_NAME", "launchpad_db")

    # === Handle SSL credentials (optional for local dev) ===
    use_ssl = os.getenv("DB_USE_SSL", "false").lower() == "true"
    cert_file_path = None
    key_file_path = None
    ca_file_path = None

    if use_ssl and cert_file_content and key_file_content and ca_file_content:
        # Write SSL credentials to temp files
        cert_file_path = create_temp_file(cert_file_content)
        key_file_path = create_temp_file(key_file_content)
        ca_file_path = create_temp_file(ca_file_content)
    else:
        logging.info("SSL disabled or SSL certificates not available. Using non-SSL connection for local development.")

    # === Ensure database exists ===
    try:
        if use_ssl and cert_file_path and key_file_path and ca_file_path:
            conn = mysql.connector.connect(
                user=username,
                password=password,
                host=server_ip,
                ssl_ca=ca_file_path,
                ssl_cert=cert_file_path,
                ssl_key=key_file_path
            )
        else:
            conn = mysql.connector.connect(
                user=username,
                password=password,
                host=server_ip
            )
        create_database_if_not_exists(conn, database)
        conn.close()
    except Exception as e:
        logging.warning(f"Could not connect to database during config initialization: {e}")
        logging.info("Database connection will be attempted when needed.")

    # === SQLAlchemy Database URI ===
    if use_ssl and cert_file_path and key_file_path and ca_file_path:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{username}:{password}@{server_ip}:3306/{database}"
            f"?ssl_ca={ca_file_path}&ssl_cert={cert_file_path}&ssl_key={key_file_path}"
        )
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{username}:{password}@{server_ip}:3306/{database}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# === Register cleanup on exit ===
def register_cleanup():
    file_paths = []
    if Config.cert_file_path:
        file_paths.append(Config.cert_file_path)
    if Config.key_file_path:
        file_paths.append(Config.key_file_path)
    if Config.ca_file_path:
        file_paths.append(Config.ca_file_path)
    if file_paths:
        atexit.register(lambda: cleanup_temp_files(file_paths))


register_cleanup()

# === Initialize SQLAlchemy engine ===
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,      # handles dropped connections gracefully
    pool_recycle=3600,       # avoids "MySQL has gone away"
)
Session = sessionmaker(bind=engine)
Base = declarative_base()
