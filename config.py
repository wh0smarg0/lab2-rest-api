import os

PROPAGATE_EXCEPTIONS = True
FLASK_DEBUG = True
#Використовуємо змінні середовища для підключення до БД
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/finance_db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
API_TITLE = "Finance REST API"
API_VERSION = "v1"
OPENAPI_VERSION = "3.0.3"
OPENAPI_URL_PREFIX = "/"
OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
JWT_SECRET_KEY = "277429514895990073851732729762754298193"