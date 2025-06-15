from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.calories import bp
from app.calories.forms import FoodEntryForm, TDEECalculatorForm
from app.models import CalorieEntry
from datetime import datetime, timedelta
from sqlalchemy import func

def calculate_daily_nutrients(entries):
    """Calculate daily nutritional breakdown from entries."""
    daily_nutrients = {
        'protein': sum(entry.protein for entry in entries if entry.protein),
        'carbs': sum(entry.carbs for entry in entries if entry.carbs),
        'fat': sum(entry.fat for entry in entries if entry.fat),
        'fiber': sum(entry.fiber for entry in entries if entry.fiber)
    }
    
    # Calculate percentages
    total_macros = daily_nutrients['protein'] + daily_nutrients['carbs'] + daily_nutrients['fat']
    if total_macros > 0:
        daily_nutrients['protein_percentage'] = (daily_nutrients['protein'] / total_macros) * 100
        daily_nutrients['carbs_fat_ratio'] = daily_nutrients['carbs'] / daily_nutrients['fat'] if daily_nutrients['fat'] > 0 else 0
    else:
        daily_nutrients['protein_percentage'] = 0
        daily_nutrients['carbs_fat_ratio'] = 0
    
    # Calculate fiber percentage against daily goal (25g recommended)
    daily_nutrients['fiber_percentage'] = (daily_nutrients['fiber'] / 25) * 100
    
    return daily_nutrients

def calculate_target_nutrients(daily_calories):
    """Calculate target nutritional values based on daily calorie goal."""
    return {
        'protein': daily_calories * 0.3 / 4,  # 30% of calories from protein (4 cal/g)
        'carbs': daily_calories * 0.45 / 4,   # 45% of calories from carbs (4 cal/g)
        'fat': daily_calories * 0.25 / 9,     # 25% of calories from fat (9 cal/g)
        'fiber': 25  # Standard daily fiber recommendation
    }

def calculate_weekly_stats(user_id):
    """Calculate weekly statistics for calorie tracking."""
    week_ago = datetime.utcnow() - timedelta(days=7)
    entries = CalorieEntry.query.filter(
        CalorieEntry.user_id == user_id,
        CalorieEntry.date >= week_ago
    ).all()
    
    if not entries:
        return None
        
    daily_totals = {}
    for entry in entries:
        date = entry.date.date()
        daily_totals[date] = daily_totals.get(date, 0) + entry.calories
    
    avg_calories = sum(daily_totals.values()) / len(daily_totals) if daily_totals else 0
    goal_adherence = len([cal for cal in daily_totals.values() if 1800 <= cal <= 2200]) / len(daily_totals) * 100 if daily_totals else 0
    
    return {
        'avg_calories': avg_calories,
        'goal_adherence': goal_adherence
    }

def calculate_meal_distribution(entries):
    """Calculate calorie distribution across meal times."""
    distribution = {
        'breakfast': 0,
        'lunch': 0,
        'dinner': 0
    }
    
    for entry in entries:
        hour = entry.date.hour
        if 6 <= hour < 11:
            distribution['breakfast'] += entry.calories
        elif 11 <= hour < 16:
            distribution['lunch'] += entry.calories
        elif 16 <= hour < 22:
            distribution['dinner'] += entry.calories
    
    return distribution

def get_frequent_foods(user_id):
    """Get most frequently logged foods in the past week."""
    week_ago = datetime.utcnow() - timedelta(days=7)
    frequent_foods = db.session.query(
        CalorieEntry.food_name,
        func.count(CalorieEntry.id).label('count'),
        func.avg(CalorieEntry.calories).label('avg_calories')
    ).filter(
        CalorieEntry.user_id == user_id,
        CalorieEntry.date >= week_ago
    ).group_by(
        CalorieEntry.food_name
    ).order_by(
        func.count(CalorieEntry.id).desc()
    ).limit(5).all()
    
    return [
        {
            'name': food.food_name,
            'count': food.count,
            'calories': round(food.avg_calories)
        }
        for food in frequent_foods
    ]

@bp.route('/calculator', methods=['GET', 'POST'])
@login_required
def calculator():
    form = FoodEntryForm()
    if form.validate_on_submit():
        entry = CalorieEntry(
            food_name=form.food_name.data,
            calories=form.calories.data,
            meal_type=form.meal_type.data,
            protein=form.protein.data or 0,
            carbs=form.carbs.data or 0,
            fat=form.fat.data or 0,
            fiber=form.fiber.data or 0,
            user=current_user
        )
        db.session.add(entry)
        db.session.commit()
        flash('Food entry added successfully!', 'success')
        return redirect(url_for('calories.calculator'))

    # Get today's entries
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    food_entries = CalorieEntry.query.filter(
        CalorieEntry.user_id == current_user.id,
        CalorieEntry.date >= today_start
    ).order_by(CalorieEntry.date.desc()).all()

    # Calculate daily totals
    calories_consumed = sum(entry.calories for entry in food_entries)
    daily_goal = 2500  # This should be customizable per user
    calories_remaining = daily_goal - calories_consumed

    # Calculate nutritional breakdown
    daily_nutrients = calculate_daily_nutrients(food_entries)
    target_nutrients = calculate_target_nutrients(daily_goal)

    # Calculate weekly statistics
    weekly_stats = calculate_weekly_stats(current_user.id)

    # Calculate meal distribution
    meal_distribution = calculate_meal_distribution(food_entries)

    # Get frequent foods
    frequent_foods = get_frequent_foods(current_user.id)

    return render_template('calorie_calculator.html',
                         form=form,
                         food_entries=food_entries,
                         daily_goal=daily_goal,
                         calories_consumed=calories_consumed,
                         calories_remaining=calories_remaining,
                         daily_nutrients=daily_nutrients,
                         target_nutrients=target_nutrients,
                         weekly_stats=weekly_stats,
                         meal_distribution=meal_distribution,
                         frequent_foods=frequent_foods)

@bp.route('/edit/<int:entry_id>', methods=['POST'])
@login_required
def edit_entry(entry_id):
    entry = CalorieEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You cannot edit this entry.', 'error')
        return redirect(url_for('calories.calculator'))
    
    try:
        food_name = request.form.get('food_name')
        calories = int(request.form.get('calories'))
        meal_type = request.form.get('meal_type')
        
        if not food_name or calories < 0 or calories > 5000:
            raise ValueError("Invalid input values")
        
        entry.food_name = food_name
        entry.calories = calories
        entry.meal_type = meal_type
        db.session.commit()
        flash('Food entry updated successfully!', 'success')
    except (ValueError, TypeError) as e:
        flash('Invalid input. Please check your values.', 'error')
    
    return redirect(url_for('calories.calculator'))

@bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = CalorieEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You cannot delete this entry.', 'error')
        return redirect(url_for('calories.calculator'))
    
    db.session.delete(entry)
    db.session.commit()
    flash('Food entry deleted successfully!', 'success')
    return redirect(url_for('calories.calculator'))

@bp.route('/calculate_tdee', methods=['GET', 'POST'])
@login_required
def calculate_tdee():
    form = TDEECalculatorForm()
    if form.validate_on_submit():
        # Calculate BMR using Mifflin-St Jeor Equation
        if form.gender.data == 'male':
            bmr = 10 * form.weight.data + 6.25 * form.height.data - 5 * form.age.data + 5
        else:
            bmr = 10 * form.weight.data + 6.25 * form.height.data - 5 * form.age.data - 161

        # Calculate TDEE
        activity_multiplier = float(form.activity_level.data)
        tdee = bmr * activity_multiplier

        # Adjust for goal
        if form.goal.data == 'lose_light':
            tdee -= 500
        elif form.goal.data == 'lose_moderate':
            tdee -= 750
        elif form.goal.data == 'lose_aggressive':
            tdee -= 1000
        elif form.goal.data == 'water_fast':
            tdee = 0  # Set to 0 for water fasting
        elif form.goal.data == 'gain':
            tdee += 500

        # Ensure TDEE doesn't go below a safe minimum (except for water fasting)
        if form.goal.data != 'water_fast':
            min_safe_calories = 1200 if form.gender.data == 'female' else 1500
            tdee = max(tdee, min_safe_calories)

        return render_template('tdee_result.html',
                             bmr=round(bmr),
                             tdee=round(tdee),
                             goal=form.goal.data)

    return render_template('tdee_calculator.html', form=form) 