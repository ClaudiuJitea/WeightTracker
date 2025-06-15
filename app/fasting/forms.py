from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange

class FastingSessionForm(FlaskForm):
    target_hours = IntegerField('Target Hours', validators=[
        DataRequired(),
        NumberRange(min=1, max=504, message='Please enter a valid duration between 1 and 504 hours (21 days)')
    ])
    fasting_type = SelectField('Fasting Type', choices=[
        ('16/8', '16/8 Intermittent Fasting (16 hours fast)'),
        ('18/6', '18/6 Intermittent Fasting (18 hours fast)'),
        ('20/4', '20/4 Intermittent Fasting (20 hours fast)'),
        ('24', 'One Day Fast (24 hours)'),
        ('36', 'Monk Fast (36 hours)'),
        ('48', 'Two Day Fast (48 hours)'),
        ('72', 'Three Day Fast (72 hours)'),
        ('120', 'Five Day Fast (120 hours)'),
        ('168', 'Seven Day Fast (168 hours)'),
        ('240', 'Ten Day Fast (240 hours)'),
        ('336', 'Two Week Fast (336 hours)'),
        ('504', 'Three Week Fast (504 hours)'),
        ('custom', 'Custom Duration')
    ])
    submit = SubmitField('Start Fasting') 