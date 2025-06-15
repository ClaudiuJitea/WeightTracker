from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange, Optional

class FoodEntryForm(FlaskForm):
    food_name = StringField('Food Name', validators=[DataRequired()])
    calories = IntegerField('Calories', validators=[
        DataRequired(),
        NumberRange(min=0, max=5000, message='Please enter a valid calorie amount between 0 and 5000')
    ])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ])
    protein = FloatField('Protein (g)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Please enter a valid protein amount between 0 and 500g')
    ])
    carbs = FloatField('Carbohydrates (g)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Please enter a valid carbs amount between 0 and 500g')
    ])
    fat = FloatField('Fat (g)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Please enter a valid fat amount between 0 and 500g')
    ])
    fiber = FloatField('Fiber (g)', validators=[
        Optional(),
        NumberRange(min=0, max=100, message='Please enter a valid fiber amount between 0 and 100g')
    ])
    submit = SubmitField('Add Food Entry')

class TDEECalculatorForm(FlaskForm):
    weight = FloatField('Weight (kg)', validators=[
        DataRequired(),
        NumberRange(min=20, max=500, message='Please enter a valid weight between 20 and 500 kg')
    ])
    height = IntegerField('Height (cm)', validators=[
        DataRequired(),
        NumberRange(min=100, max=250, message='Please enter a valid height between 100 and 250 cm')
    ])
    age = IntegerField('Age', validators=[
        DataRequired(),
        NumberRange(min=15, max=120, message='Please enter a valid age between 15 and 120')
    ])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female')
    ])
    activity_level = SelectField('Activity Level', choices=[
        ('1.2', 'Sedentary (little or no exercise)'),
        ('1.375', 'Lightly active (light exercise/sports 1-3 days/week)'),
        ('1.55', 'Moderately active (moderate exercise/sports 3-5 days/week)'),
        ('1.725', 'Very active (hard exercise/sports 6-7 days/week)'),
        ('1.9', 'Extra active (very hard exercise/sports & physical job)')
    ])
    goal = SelectField('Goal', choices=[
        ('maintain', 'Maintain weight'),
        ('lose_light', 'Light weight loss (-500 calories)'),
        ('lose_moderate', 'Moderate weight loss (-750 calories)'),
        ('lose_aggressive', 'Aggressive weight loss (-1000 calories)'),
        ('water_fast', 'Water fasting (0 calories)'),
        ('gain', 'Gain weight (+500 calories)')
    ])
    submit = SubmitField('Calculate TDEE') 