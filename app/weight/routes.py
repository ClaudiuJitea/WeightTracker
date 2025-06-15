from flask import render_template, flash, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from app.extensions import db
from app.weight import bp
from app.weight.forms import WeightEntryForm, WeightGoalForm
from app.models import WeightEntry, WeightGoal, FastingSession
from datetime import datetime, timedelta

@bp.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    form = WeightEntryForm()
    goal_form = WeightGoalForm()

    # Get current active fast
    current_fast = FastingSession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(FastingSession.start_time.desc()).first()

    if form.validate_on_submit():
        entry = WeightEntry(weight=form.weight.data, user=current_user)
        db.session.add(entry)
        
        # Check if the user has reached their weight goal
        active_goal = WeightGoal.query.filter_by(user_id=current_user.id, active=True).first()
        if active_goal:
            # For weight loss goal
            if active_goal.start_weight > active_goal.target_weight and form.weight.data <= active_goal.target_weight:
                flash('🎉 Congratulations! You have reached your weight loss goal! 🎉', 'success')
                active_goal.completed = True
                # Keep the goal active so it still shows in the UI, but mark it as completed
            # For weight gain goal
            elif active_goal.start_weight < active_goal.target_weight and form.weight.data >= active_goal.target_weight:
                flash('🎉 Congratulations! You have reached your weight gain goal! 🎉', 'success')
                active_goal.completed = True
                # Keep the goal active so it still shows in the UI, but mark it as completed
        
        db.session.commit()
        flash('Weight entry added successfully!', 'success')
        return redirect(url_for('weight.tracker'))

    # Get weight statistics
    weight_entries = WeightEntry.query.filter_by(user_id=current_user.id).order_by(WeightEntry.date.desc()).all()
    starting_weight = weight_entries[-1].weight if weight_entries else None
    current_weight = weight_entries[0].weight if weight_entries else None
    total_loss = current_weight - starting_weight if current_weight and starting_weight else None

    # Get active weight goal
    active_goal = WeightGoal.query.filter_by(user_id=current_user.id, active=True).first()

    # Calculate progress based on meeting daily/weekly/monthly goals
    recent_progress = {
        'daily': 0,
        'weekly': 0,
        'monthly': 0
    }
    
    if weight_entries and len(weight_entries) >= 2 and active_goal:
        # For daily progress, use the most recent weight change
        latest_two = weight_entries[:2]
        daily_change = latest_two[0].weight - latest_two[1].weight  # Negative means weight loss
        recent_progress['daily'] = daily_change
        
        # For weekly progress, use the most recent week's worth of changes
        weekly_change = 0
        for i in range(len(weight_entries) - 1):
            current_entry = weight_entries[i]
            next_entry = weight_entries[i + 1]
            days_between = (current_entry.date - next_entry.date).days
            if days_between <= 7:  # Only include changes within the last 7 days
                change = current_entry.weight - next_entry.weight
                weekly_change += change
            else:
                break
        recent_progress['weekly'] = weekly_change
        
        # For monthly progress, use the most recent month's worth of changes
        monthly_change = 0
        for i in range(len(weight_entries) - 1):
            current_entry = weight_entries[i]
            next_entry = weight_entries[i + 1]
            days_between = (current_entry.date - next_entry.date).days
            if days_between <= 30:  # Only include changes within the last 30 days
                change = current_entry.weight - next_entry.weight
                monthly_change += change
            else:
                break
        recent_progress['monthly'] = monthly_change

    # Initialize empty arrays for chart data
    dates = []
    weights = []
    goal_line = []
    
    # Prepare data for the chart
    if weight_entries:
        if active_goal:
            goal_start_date = active_goal.start_date.date()
            actual_start_weight = active_goal.start_weight  # Use the weight saved when goal was created
            
            for entry in reversed(weight_entries):
                dates.append(entry.date.strftime('%Y-%m-%d'))
                weights.append(float(entry.weight))  # Ensure weight is a float
                days_from_start = (entry.date.date() - goal_start_date).days
                if days_from_start >= 0:  # Only calculate goal for dates after goal start
                    total_days = (active_goal.target_date.date() - goal_start_date).days
                    if total_days > 0:
                        daily_change = (active_goal.target_weight - actual_start_weight) / total_days
                        goal_weight = actual_start_weight + (daily_change * days_from_start)
                        goal_line.append(float(goal_weight))  # Ensure goal weight is a float
                    else:
                        goal_line.append(float(actual_start_weight))  # Ensure start weight is a float
                else:
                    # For dates before goal start, don't show any goal line
                    goal_line.append(None)

            # If there's an active goal, extend the goal line to the target date
            if dates:
                last_date = datetime.strptime(dates[-1], '%Y-%m-%d')
                target_date = active_goal.target_date.date()
                
                # Calculate how many days to add
                days_to_add = (target_date - last_date.date()).days
                
                # Add future dates and corresponding goal values
                for i in range(1, days_to_add + 1):
                    future_date = last_date + timedelta(days=i)
                    dates.append(future_date.strftime('%Y-%m-%d'))
                    
                    days_from_start = (future_date.date() - goal_start_date).days
                    total_days = (target_date - goal_start_date).days
                    
                    if total_days > 0:
                        daily_change = (active_goal.target_weight - actual_start_weight) / total_days
                        goal_weight = actual_start_weight + (daily_change * days_from_start)
                    else:
                        goal_weight = actual_start_weight
                        
                    weights.append(None)  # Add None for actual weights on future dates
                    goal_line.append(float(goal_weight))  # Ensure goal weight is a float
        else:
            # If no active goal, just add the weight entries to the chart
            for entry in reversed(weight_entries):
                dates.append(entry.date.strftime('%Y-%m-%d'))
                weights.append(float(entry.weight))  # Ensure weight is a float
    
    # Ensure we have at least empty arrays if no data
    if not dates:
        dates = []
    if not weights:
        weights = []
    if not goal_line:
        goal_line = []
        
    # Ensure all arrays have the same length
    max_length = max(len(dates), len(weights), len(goal_line))
    
    # Pad arrays to ensure they all have the same length
    if len(dates) < max_length:
        # If dates array is shorter, add placeholder dates
        for i in range(len(dates), max_length):
            if i > 0 and i-1 < len(dates):
                # Try to extrapolate from the last date
                last_date = datetime.strptime(dates[i-1], '%Y-%m-%d')
                dates.append((last_date + timedelta(days=1)).strftime('%Y-%m-%d'))
            else:
                # Fallback to today's date + index
                dates.append((datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d'))
    
    if len(weights) < max_length:
        # Pad weights array with null values
        weights.extend([None] * (max_length - len(weights)))
    
    if len(goal_line) < max_length:
        # Pad goal_line array with null values
        goal_line.extend([None] * (max_length - len(goal_line)))
    
    # Debug output
    print(f"Dates length: {len(dates)}, Weights length: {len(weights)}, Goal line length: {len(goal_line)}")

    return render_template('weight_tracker.html',
                         form=form,
                         goal_form=goal_form,
                         weight_entries=weight_entries,
                         starting_weight=starting_weight,
                         current_weight=current_weight,
                         total_loss=total_loss,
                         dates=dates,
                         weights=weights,
                         goal_line=goal_line if active_goal and goal_line else [],
                         active_goal=active_goal,
                         recent_progress=recent_progress,
                         current_fast=current_fast)

@bp.route('/set_goal', methods=['POST'])
@login_required
def set_goal():
    form = WeightGoalForm()
    if form.validate_on_submit():
        # Deactivate any existing active goals
        WeightGoal.query.filter_by(user_id=current_user.id, active=True).update({'active': False})
        
        # Get the current weight from the most recent weight entry
        latest_entry = WeightEntry.query.filter_by(user_id=current_user.id).order_by(WeightEntry.date.desc()).first()
        if not latest_entry:
            flash('Please add a weight entry before setting a goal.', 'error')
            return redirect(url_for('weight.tracker'))
        
        start_weight = latest_entry.weight

        # Create new goal with current datetime as start_date
        current_time = datetime.utcnow()
        goal = WeightGoal(
            start_weight=start_weight,
            target_weight=form.target_weight.data,
            start_date=current_time,
            target_date=datetime.combine(form.target_date.data, datetime.min.time()),
            goal_type=form.goal_type.data,
            user=current_user,
            active=True
        )
        
        # Calculate and display expected weekly loss
        days_until_target = (goal.target_date - current_time).days
        if days_until_target > 0:
            total_loss = abs(goal.target_weight - goal.start_weight)
            weekly_loss = (total_loss / days_until_target) * 7
            
            if form.goal_type.data == 'steady':
                message = f'Your goal is set to lose {weekly_loss:.1f} kg per week (recommended 0.5-1 kg/week)'
            elif form.goal_type.data == 'moderate':
                message = f'Your goal is set to lose {weekly_loss:.1f} kg per week (0.5% of current weight)'
            elif form.goal_type.data == 'aggressive':
                message = f'Your goal is set to lose {weekly_loss:.1f} kg per week (1% of current weight)'
            else:
                message = f'Your custom goal is set to lose {weekly_loss:.1f} kg per week'
                
            if weekly_loss > 1:
                message += '. Note: This is an aggressive goal. Consider extending your timeline for healthier weight loss.'
            
            flash(message, 'info')
        
        db.session.add(goal)
        db.session.commit()
        flash('Weight goal set successfully!', 'success')
    return redirect(url_for('weight.tracker'))

@bp.route('/cancel_goal', methods=['POST'])
@login_required
def cancel_goal():
    active_goal = WeightGoal.query.filter_by(user_id=current_user.id, active=True).first()
    if active_goal:
        active_goal.active = False
        db.session.commit()
        flash('Weight goal cancelled successfully!', 'success')
    return redirect(url_for('weight.tracker'))

@bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = WeightEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You cannot delete this entry.', 'error')
        return redirect(url_for('weight.tracker'))
    
    db.session.delete(entry)
    db.session.commit()
    flash('Weight entry deleted successfully!', 'success')
    return redirect(url_for('weight.tracker'))

@bp.route('/edit/<int:entry_id>', methods=['POST'])
@login_required
def edit_entry(entry_id):
    entry = WeightEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You cannot edit this entry.', 'error')
        return redirect(url_for('weight.tracker'))
    
    new_weight = request.form.get('weight')
    try:
        new_weight = float(new_weight)
        if new_weight < 20 or new_weight > 500:
            raise ValueError("Weight must be between 20 and 500 kg")
        
        entry.weight = new_weight
        db.session.commit()
        flash('Weight entry updated successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('weight.tracker')) 