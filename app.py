import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST
import models

from resources.user import blp as UserBlueprint
from resources.file import blp as FileBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    
    CORS(app)
    
    secret_key = os.getenv("SECRET_KEY")
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db").replace("postgresql://", "postgresql+psycopg2://")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["ALLOWED_EXTENSIONS"] = {"txt", "pdf", "png", "jpg", "jpeg"}
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    db.init_app(app)
    migrate=Migrate(app, db)
    api = Api(app)


    upload_folder = app.config["UPLOAD_FOLDER"]
    if not upload_folder:
        raise ValueError("UPLOAD_FOLDER not defined! Check .env file.")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    print(f"UPLOAD_FOLDER: {app.config['UPLOAD_FOLDER']}")
    app.config["SECRET_KEY"] = secret_key
    app.config["WTF_CSRF_SECRET_KEY"] = secret_key
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["JWT_SECRET_KEY"] = secret_key

    print("ALLOWED_EXTENSIONS:", app.config["ALLOWED_EXTENSIONS"])
    print("ALLOWED_EXTENSIONS TYPE:", type(app.config["ALLOWED_EXTENSIONS"]))

    jwt = JWTManager(app)

    # @jwt.additional_claims_loader
    # def add_claims_to_jwt(identity):
    #     # TODO: Read from a config file instead of hard-coding
    #     if identity == 1:
    #         return {"is_admin": True}
    #     return {"is_admin": False}

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    @app.after_request
    def set_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline';"
        return response
    


    api.register_blueprint(UserBlueprint)
    api.register_blueprint(FileBlueprint)

    return app
