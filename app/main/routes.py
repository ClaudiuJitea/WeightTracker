from flask import render_template, redirect, url_for, send_from_directory, request, flash
from flask_login import login_required, current_user
from app.main import bp
from app.models import WeightEntry, CalorieEntry
from datetime import datetime, timedelta
from app.main.forms import ProfileForm
from app.extensions import db

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory('static/images', 'favicon.ico')

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get current weight and change
    latest_weight = WeightEntry.query.filter_by(user_id=current_user.id).order_by(WeightEntry.date.desc()).first()
    week_ago_weight = WeightEntry.query.filter(
        WeightEntry.user_id == current_user.id,
        WeightEntry.date <= datetime.utcnow() - timedelta(days=7)
    ).order_by(WeightEntry.date.desc()).first()
    
    current_weight = latest_weight.weight if latest_weight else None
    weight_change = (latest_weight.weight - week_ago_weight.weight) if latest_weight and week_ago_weight else None

    # Get weight history for the chart (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    weight_entries = WeightEntry.query.filter(
        WeightEntry.user_id == current_user.id,
        WeightEntry.date >= thirty_days_ago
    ).order_by(WeightEntry.date.asc()).all()

    dates = []
    weights = []
    if weight_entries:
        for entry in weight_entries:
            dates.append(entry.date.strftime('%Y-%m-%d'))
            weights.append(entry.weight)

    # Get calories for today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    calories_today = sum(entry.calories for entry in CalorieEntry.query.filter(
        CalorieEntry.user_id == current_user.id,
        CalorieEntry.date >= today_start
    ).all())

    return render_template('dashboard.html',
                         current_weight=current_weight,
                         weight_change=weight_change,
                         calories_today=calories_today,
                         daily_calorie_goal=2500,  # This should be customizable per user
                         dates=dates,
                         weights=weights)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.height = form.height.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.height.data = current_user.height
    return render_template('profile.html', form=form) 