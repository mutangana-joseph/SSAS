
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SSAS_ADMIN_ACCESS_CODE=os.getenv("SSAS_ADMIN_ACCESS_CODE")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SSAS_DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
