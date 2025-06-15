from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProfileForm(FlaskForm):
    height = FloatField('Height (cm)', validators=[
        DataRequired(),
        NumberRange(min=100, max=250, message='Please enter a valid height between 100 and 250 cm')
    ])
    submit = SubmitField('Update Profile') 