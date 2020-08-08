from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class RequestForm(FlaskForm):
    url = StringField('Url', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Submit')