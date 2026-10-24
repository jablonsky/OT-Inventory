import os

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///inventory.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
