import os


class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL")
    DEBUG = os.getenv("DEBUG")
    TESTING = os.getenv("TESTING")
    API_TITLE = os.getenv("API_TITLE")
    API_VERSION = os.getenv("API_VERSION")
