import argparse
import logging
import os
import sys

from sqlsorcery import SQLite, PostgreSQL, MSSQL


parser = argparse.ArgumentParser(description="Pick which ones")
parser.add_argument("--debug", help="Enable debug logging", action="store_true")
parser.add_argument("--all", help="Import all data", action="store_true")
parser.add_argument("--accounts", help="Create student accounts", action="store_true")
parser.add_argument("--users", help="Import users and groups", action="store_true")
parser.add_argument(
    "--meetings", help="Import meetings and participants", action="store_true"
)
args, _ = parser.parse_known_args()

ENABLE_MAILER = int(os.getenv("ENABLE_MAILER", default=0))
DEBUG_MODE = args.debug or int(os.getenv("DEBUG_MODE", default=0))
ZOOM_KEY = os.getenv("ZOOM_KEY")
ZOOM_SECRET = os.getenv("ZOOM_SECRET")
ACCOUNTS = args.accounts or args.all
USERS = args.users or args.all
MEETINGS = args.meetings or args.all


USER_COLUMNS = [
    "id",
    "first_name",
    "last_name",
    "email",
    "type",
    "status",
    "pmi",
    "timezone",
    "dept",
    "created_at",
    "last_login_time",
    "last_client_version",
    "verified",
]


def set_logging():
    """Configure logging level and outputs"""
    logging.basicConfig(
        handlers=[
            logging.FileHandler(filename="app.log", mode="w+"),
            logging.StreamHandler(sys.stdout),
        ],
        level=logging.DEBUG if DEBUG_MODE else logging.INFO,
        format="%(asctime)s | %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %I:%M:%S%p %Z",
    )
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)


class DatabaseTypeError(Exception):
    def __init__(self):
        self.message = (
            "Connection Failed: Verify DB_TYPE variable is set in the environment."
        )
        super().__init__(self.message)


def db_connection():
    """Set database connection based on type"""
    db_type = os.getenv("DB_TYPE")
    default_config = {
        "schema": os.getenv("DB_SCHEMA"),
        "server": os.getenv("DB_SERVER"),
        "port": os.getenv("DB_PORT"),
        "db": os.getenv("DB"),
        "user": os.getenv("DB_USER"),
        "pwd": os.getenv("DB_PWD"),
    }
    if db_type == "mssql":
        return MSSQL(**default_config)
    elif db_type == "postgres":
        return PostgreSQL(**default_config)
    elif db_type == "sqlite":
        return SQLite(path=os.getenv("DB"))
    else:
        raise DatabaseTypeError()

