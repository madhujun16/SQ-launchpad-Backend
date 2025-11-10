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
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    # === Load SSL and DB credentials ===
    cert_file_content = get_pii_encryption_key_from_secrets(db_secrets["certificate"])
    key_file_content = get_pii_encryption_key_from_secrets(db_secrets["key"])
    ca_file_content = get_pii_encryption_key_from_secrets(db_secrets["ca"])
    db_credentials = get_pii_encryption_key_from_secrets(db_secrets["db_credentials"])

    username = db_credentials.get("username")
    password = db_credentials.get("password")
    server_ip = db_credentials.get("server_ip")
    database = db_credentials.get("database", "launchpad_db")

    # === Write SSL credentials to temp files ===
    cert_file_path = create_temp_file(cert_file_content)
    key_file_path = create_temp_file(key_file_content)
    ca_file_path = create_temp_file(ca_file_content)

    # === Ensure database exists ===
    conn = mysql.connector.connect(
        user=username,
        password=password,
        host=server_ip,
        ssl_ca=ca_file_path,
        ssl_cert=cert_file_path,
        ssl_key=key_file_path
    )
    create_database_if_not_exists(conn, database)
    conn.close()

    # === SQLAlchemy Database URI ===
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{username}:{password}@{server_ip}:3306/{database}"
        f"?ssl_ca={ca_file_path}&ssl_cert={cert_file_path}&ssl_key={key_file_path}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# === Register cleanup on exit ===
def register_cleanup():
    file_paths = [
        Config.cert_file_path,
        Config.key_file_path,
        Config.ca_file_path,
    ]
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
