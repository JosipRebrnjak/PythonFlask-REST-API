from db import db

class FileModel(db.Model):
    __tablename__= "uploaded_files"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    encrypted_key = db.Column(db.String(255), nullable=False)
    file_uuid = db.Column(db.String(36), unique=True, nullable=False)
