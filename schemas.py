import uuid
from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class FileSchema(Schema):
    id = fields.Int(dump_only=True)
    filename = fields.Str(required=True)
    filepath = fields.Str(required=True)
    encrypted_key = fields.Str(required=True, load_only=True)
    file_uuid = fields.Str(required=True)
