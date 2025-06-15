from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import datetime, timedelta

class WeightEntryForm(FlaskForm):
    weight = FloatField('Weight (kg)', validators=[
        DataRequired(),
        NumberRange(min=20, max=500, message='Please enter a valid weight between 20 and 500 kg')
    ])
    submit = SubmitField('Save Entry')

class WeightGoalForm(FlaskForm):
    target_weight = FloatField('Target Weight (kg)', validators=[
        DataRequired(),
        NumberRange(min=20, max=500, message='Please enter a valid weight between 20 and 500 kg')
    ])
    goal_type = SelectField('Goal Type', choices=[
        ('steady', 'Steady Loss (Recommended)'),
        ('aggressive', 'Aggressive Loss (1% per week)'),
        ('moderate', 'Moderate Loss (0.5% per week)'),
        ('custom', 'Custom Target Date')
    ], validators=[DataRequired()])
    target_date = DateField('Target Date')
    submit = SubmitField('Set Goal')

    def validate_target_date(self, field):
        # Only validate target_date if goal_type is 'custom'
        if self.goal_type.data == 'custom':
            if not field.data:
                raise ValidationError('Target date is required for custom goals')
            if field.data <= datetime.now().date():
                raise ValidationError('Target date must be in the future')
            if field.data > datetime.now().date() + timedelta(days=365*2):
                raise ValidationError('Target date cannot be more than 2 years in the future')
        
    def validate(self, extra_validators=None):
        if not super().validate():
            return False
            
        if self.goal_type.data != 'custom':
            # Calculate target date based on goal type
            current_date = datetime.now().date()
            
            # Get current weight from the database
            from flask_login import current_user
            from app.models import WeightEntry
            latest_entry = WeightEntry.query.filter_by(user_id=current_user.id)\
                .order_by(WeightEntry.date.desc()).first()
            
            if not latest_entry:
                return False
                
            current_weight = latest_entry.weight
            
            if self.goal_type.data == 'aggressive':
                # 1% loss per week
                weeks_needed = abs(self.target_weight.data - current_weight) / (current_weight * 0.01)
                self.target_date.data = current_date + timedelta(weeks=weeks_needed)
            elif self.goal_type.data == 'moderate':
                # 0.5% loss per week
                weeks_needed = abs(self.target_weight.data - current_weight) / (current_weight * 0.005)
                self.target_date.data = current_date + timedelta(weeks=weeks_needed)
            elif self.goal_type.data == 'steady':
                # Aim for 0.5-1 kg per week
                kg_to_lose = abs(self.target_weight.data - current_weight)
                weeks_needed = kg_to_lose / 0.75  # Average of 0.75 kg per week
                self.target_date.data = current_date + timedelta(weeks=weeks_needed)
                
        return True