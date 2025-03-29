import os
import uuid
from flask import Flask, current_app, jsonify, request, send_from_directory
from flask.views import MethodView
from flask_smorest import Blueprint
from werkzeug.utils import secure_filename
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import jwt_required

from blocklist import BLOCKLIST
from db import db
from models import FileModel
from schemas import FileSchema

blp = Blueprint("Files", "files", __name__, description="Operations with files")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]

def check_key(key):
    return 


@blp.route("/upload")
class UploadFile(MethodView):
    def post(self):
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]
        file_password = request.form.get("password")

        if not request.content_type.startswith("multipart/form-data"):
            return jsonify({"error": "Invalid content type"}), 400

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        if not file_password:
            return jsonify({"error": "Password is required"}), 400

        checked_filename = secure_filename(file.filename)
        file_extension = file.filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"

        file_uuid = str(uuid.uuid4())
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)

        new_file = FileModel(
            filename=checked_filename,
            filepath=file_path,
            encrypted_key=pbkdf2_sha256.hash(file_password),
            file_uuid=file_uuid,
        )
        db.session.add(new_file)
        db.session.commit()

        return jsonify(
            {
                "message": "File uploaded successfully",
                "file_path": new_file.file_uuid,
            }
        ), 201


@blp.route("/get-file/<file_uuid>")
class DownloadFile(MethodView):
    def post(self, file_uuid):
        file_data = request.get_json()

        if not file_data or "password" not in file_data:
            return jsonify({"error": "Password is required"}), 400
        
        file_record = FileModel.query.filter_by(file_uuid=file_uuid).first()

        if not file_record:
            return jsonify({"error": "File not found"}), 404

        if not pbkdf2_sha256.verify(file_data["password"], file_record.encrypted_key):
            return jsonify({"error": "Invalid password"}), 401
    
        return send_from_directory(
            os.path.dirname(file_record.filepath),
            os.path.basename(file_record.filepath),
            as_attachment=True,
        )
