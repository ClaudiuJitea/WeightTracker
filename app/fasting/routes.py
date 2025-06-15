from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.fasting import bp
from app.fasting.forms import FastingSessionForm
from app.models import FastingSession
from datetime import datetime, timedelta
from sqlalchemy import func

def calculate_fasting_stats(user_id):
    # Get all completed fasting sessions
    completed_sessions = FastingSession.query.filter_by(
        user_id=user_id,
        completed=True
    ).all()
    
    if not completed_sessions:
        return None
        
    total_fasts = len(completed_sessions)
    total_hours = sum(session.duration for session in completed_sessions)
    avg_duration = total_hours / total_fasts
    longest_fast = max(completed_sessions, key=lambda x: x.duration)
    
    # Modify this line to handle None values for target_hours
    success_rate = len([s for s in completed_sessions if s.target_hours is None or s.duration >= s.target_hours]) / total_fasts * 100
    
    # Calculate weekly stats
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_sessions = [s for s in completed_sessions if s.start_time >= week_ago]
    weekly_hours = sum(session.duration for session in weekly_sessions)
    
    # Calculate monthly stats
    month_ago = datetime.utcnow() - timedelta(days=30)
    monthly_sessions = [s for s in completed_sessions if s.start_time >= month_ago]
    monthly_hours = sum(session.duration for session in monthly_sessions)
    
    return {
        'total_fasts': total_fasts,
        'total_hours': total_hours,
        'avg_duration': avg_duration,
        'longest_fast': longest_fast,
        'success_rate': success_rate,
        'weekly_hours': weekly_hours,
        'monthly_hours': monthly_hours,
        'weekly_sessions': len(weekly_sessions),
        'monthly_sessions': len(monthly_sessions)
    }

def calculate_streaks(user_id):
    completed_sessions = FastingSession.query.filter_by(
        user_id=user_id,
        completed=True
    ).order_by(FastingSession.start_time.desc()).all()
    
    if not completed_sessions:
        return None
    
    # Calculate current/best streaks of successful fasts (reaching target)
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    for session in completed_sessions:
        # Consider a fast successful if target_hours is None or the duration meets/exceeds the target
        if session.target_hours is None or session.duration >= session.target_hours:
            temp_streak += 1
            if temp_streak > best_streak:
                best_streak = temp_streak
        else:
            if current_streak == 0:  # Only update current streak if we haven't broken it yet
                current_streak = temp_streak
            temp_streak = 0
    
    if current_streak == 0:  # If we never broke the streak
        current_streak = temp_streak
    
    # Calculate consistency (fasts completed in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_sessions = FastingSession.query.filter(
        FastingSession.user_id == user_id,
        FastingSession.completed == True,
        FastingSession.start_time >= week_ago
    ).count()
    
    consistency = (weekly_sessions / 7) * 100  # Percentage of days with completed fasts
    
    return {
        'current_streak': current_streak,
        'best_streak': best_streak,
        'weekly_consistency': consistency
    }

@bp.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    form = FastingSessionForm()
    
    # Get current active fast
    current_fast = FastingSession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(FastingSession.start_time.desc()).first()

    # Get fasting history
    fasting_history = FastingSession.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(FastingSession.start_time.desc()).all()

    # Calculate statistics and streaks
    stats = calculate_fasting_stats(current_user.id)
    streaks = calculate_streaks(current_user.id)

    if form.validate_on_submit():
        if current_fast:
            flash('You already have an active fast. Please end it before starting a new one.', 'error')
            return redirect(url_for('fasting.tracker'))

        # Get target hours based on fasting type
        fasting_type = form.fasting_type.data
        if fasting_type == 'custom':
            target_hours = form.target_hours.data
        else:
            # Extract hours from the fasting type value (e.g., '16/8' -> 16)
            target_hours = int(fasting_type.split('/')[0] if '/' in fasting_type else fasting_type)

        session = FastingSession(
            start_time=datetime.utcnow(),
            target_hours=target_hours,
            user=current_user
        )
        db.session.add(session)
        db.session.commit()
        flash('Fasting session started!', 'success')
        return redirect(url_for('fasting.tracker'))

    return render_template('fasting_tracker.html',
                         form=form,
                         current_fast=current_fast,
                         fasting_history=fasting_history,
                         stats=stats,
                         streaks=streaks,
                         timedelta=timedelta)

@bp.route('/end/<int:session_id>', methods=['POST'])
@login_required
def end_session(session_id):
    session = FastingSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash('You cannot end this fasting session.', 'error')
        return redirect(url_for('fasting.tracker'))

    if session.completed:
        flash('This fasting session is already completed.', 'error')
        return redirect(url_for('fasting.tracker'))

    session.end_time = datetime.utcnow()
    session.completed = True
    db.session.commit()

    duration = session.duration
    message = f'Fasting session completed! Duration: {duration:.1f} hours'
    if session.target_hours:
        if duration >= session.target_hours:
            message += f' (Target: {session.target_hours} hours - Goal achieved!)'
        else:
            message += f' (Target: {session.target_hours} hours - Keep trying!)'
    
    flash(message, 'success')
    return redirect(url_for('fasting.tracker'))

@bp.route('/cancel/<int:session_id>', methods=['POST'])
@login_required
def cancel_session(session_id):
    session = FastingSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash('You cannot cancel this fasting session.', 'error')
        return redirect(url_for('fasting.tracker'))

    if session.completed:
        flash('This fasting session is already completed.', 'error')
        return redirect(url_for('fasting.tracker'))

    db.session.delete(session)
    db.session.commit()
    flash('Fasting session cancelled.', 'success')
    return redirect(url_for('fasting.tracker'))

@bp.route('/delete/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    session = FastingSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash('You cannot delete this fasting session.', 'error')
        return redirect(url_for('fasting.tracker'))

    if not session.completed:
        flash('Cannot delete an active fasting session. Please end or cancel it first.', 'error')
        return redirect(url_for('fasting.tracker'))

    db.session.delete(session)
    db.session.commit()
    flash('Fasting session deleted.', 'success')
    return redirect(url_for('fasting.tracker'))

@bp.route('/status')
@login_required
def status():
    current_fast = FastingSession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(FastingSession.start_time.desc()).first()

    if not current_fast:
        return jsonify({
            'active': False,
            'message': 'No active fast'
        })

    return jsonify({
        'active': True,
        'duration': current_fast.duration,
        'target_hours': current_fast.target_hours,
        'progress': current_fast.progress
    })

@bp.route('/end_fast', methods=['POST'])
@login_required
def end_fast():
    # Get the current active fast
    current_fast = FastingSession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(FastingSession.start_time.desc()).first()
    
    if not current_fast:
        flash('No active fasting session found.', 'error')
        return redirect(url_for('fasting.tracker'))
    
    current_fast.end_time = datetime.utcnow()
    current_fast.completed = True
    db.session.commit()
    
    duration = current_fast.duration
    message = f'Fasting session completed! Duration: {duration:.1f} hours'
    if current_fast.target_hours:
        if duration >= current_fast.target_hours:
            message += f' (Target: {current_fast.target_hours} hours - Goal achieved!)'
        else:
            message += f' (Target: {current_fast.target_hours} hours - Keep trying!)'
    
    flash(message, 'success')
    return redirect(url_for('fasting.tracker'))

@bp.route('/start_fast', methods=['GET', 'POST'])
@login_required
def start_fast():
    # Handle GET requests by redirecting to tracker
    if request.method == 'GET':
        return redirect(url_for('fasting.tracker'))
    
    # Check if there's already an active fast
    current_fast = FastingSession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(FastingSession.start_time.desc()).first()
    
    if current_fast:
        flash('You already have an active fast. Please end it before starting a new one.', 'error')
        return redirect(url_for('fasting.tracker'))
    
    # Get form data
    is_undefined = request.form.get('is_undefined') == 'on'
    target_hours = None if is_undefined else float(request.form.get('target_hours', 16))
    
    # Create new fasting session
    session = FastingSession(
        start_time=datetime.utcnow(),
        target_hours=target_hours,
        user=current_user
    )
    db.session.add(session)
    db.session.commit()
    
    flash('Fasting session started!', 'success')
    return redirect(url_for('fasting.tracker'))