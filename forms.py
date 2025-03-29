from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField("Upload File", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Upload")

class DownloadForm(FlaskForm):
    password = PasswordField("Enter Password", validators=[DataRequired()])
    submit = SubmitField("Download")