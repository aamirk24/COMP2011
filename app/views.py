from flask import Blueprint, request, flash, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user, logout_user
from . import db, get_exercises
from .models import Exercise, Workout, User, WorkoutSession, SessionExercise, ExerciseSet
from .models import Height, Weight
from .forms import WorkoutForm, WorkoutSessionForm, EmptyWorkoutForm, UpdateForm
from .forms import HeightForm, WeightForm
import json

views = Blueprint('views', __name__)


@views.route('/landing', methods=['POST', 'GET'])
def landing():
    return render_template('landing.html', user=current_user)


@views.route('/exercise', methods=['POST', 'GET'])
@login_required
def home():
    exercises = Exercise.query.all()

    return render_template('exercise.html', exercises=exercises, user=current_user)


@views.route('/exercises', methods=['GET'])
@login_required
def get_all_exercises():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    exercises = Exercise.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'exercises': [{
            'id': e.id,
            'name': e.name,
            'target': e.target,
            'secondaryMuscles': e.secondaryMuscles,
            'instructions': e.instructions,
            'gifUrl': e.gifUrl
        } for e in exercises.items],
        'total': exercises.total,
        'pages': exercises.pages,
        'current_page': exercises.page
    })


@views.route('/create_workout', methods=['GET', 'POST'])
@login_required
def create_workout():
    form = WorkoutForm()

    form.exercises.choices = [(exercise.id, exercise.name) for exercise in Exercise.query.all()]

    if form.validate_on_submit():
        new_workout = Workout(
            name=form.name.data,
            description=form.description.data,
            creator=current_user
        )

        # Adding exercises
        selected_exercises = Exercise.query.filter(Exercise.id.in_(form.exercises.data)).all()
        new_workout.exercises.extend(selected_exercises)

        db.session.add(new_workout)
        db.session.commit()

        return redirect(url_for('views.dashboard'))

    return render_template('create_workout.html', form=form, user=current_user)


@views.route('/delete_workout', methods=['POST'])
@login_required
def delete_workout():
    workout = json.loads(request.data)
    workoutId = workout['workoutId']
    workout = Workout.query.get(workoutId)

    if workout:
        if workout.creator_id == current_user.id:
            db.session.delete(workout)
            db.session.commit()
            return redirect(url_for('views.dashboard'))

    return jsonify({"success": False}), 400


@views.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    workouts = Workout.query.filter_by(creator=current_user).all()

    recent_sessions = WorkoutSession.query.filter_by(user=current_user).order_by(WorkoutSession.start_time.desc()).all()

    for session in recent_sessions:
        session.total_sets = sum(len(exercise.sets) for exercise in session.session_exercises)

    return render_template('dashboard.html',
                           user=current_user,
                           workouts=workouts,
                           recent_sessions=recent_sessions)


@views.route('/profile-info', methods=['POST', 'GET'])
@login_required
def profile_info():
    form = UpdateForm(obj=current_user)

    if form.validate_on_submit():

        # Updating information
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            user.first_name = form.first_name.data
            user.username = form.username.data
            user.birthdate = form.birthdate.data
            user.gender = form.gender.data
            user.city = form.city.data
            user.county = form.county.data
            user.country = form.country.data

            db.session.commit()
            return redirect(url_for('views.profile_info'))

    return render_template('profile_info.html', user=current_user, form=form)


@views.route('/tracking', methods=['GET', 'POST'])
@login_required
def tracking():
    # Fetch user's workouts
    workouts = Workout.query.filter_by(creator=current_user).all()

    # Fetch all exercises for the exercise selection dropdown
    exercises = Exercise.query.all()

    # Fetch user's recent workout sessions
    recent_sessions = WorkoutSession.query.filter_by(user=current_user) \
        .order_by(WorkoutSession.start_time.desc()) \
        .limit(10) \
        .all()

    return render_template('tracking.html',
                           user=current_user,
                           workouts=workouts,
                           exercises=exercises,
                           recent_sessions=recent_sessions)


@views.route('/start_empty_workout', methods=['POST'])
@login_required
def start_empty_workout():
    workout_session = WorkoutSession(
        user=current_user,
        notes='Empty Workout'
    )
    db.session.add(workout_session)
    db.session.commit()

    return jsonify({
        'success': True,
        'session_id': workout_session.id,
        'message': 'Workout session started'
    })


@views.route('/add_session_exercise', methods=['POST'])
@login_required
def add_session_exercise():
    data = request.get_json()

    # Find the workout session
    workout_session = WorkoutSession.query.get_or_404(data['session_id'])

    # Create session exercise
    session_exercise = SessionExercise(
        workout_session=workout_session,
        exercise_id=data['exercise_id'],
        order=len(workout_session.session_exercises) + 1
    )
    db.session.add(session_exercise)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Exercise added to session'
    })


@views.route('/remove_session_exercise', methods=['POST'])
@login_required
def remove_session_exercise():
    data = request.get_json()

    session_id = data.get('session_id')
    exercise_id = data.get('exercise_id')

    if not (session_id and exercise_id):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Find and remove the session exercise
    session_exercise = SessionExercise.query.filter_by(
        workout_session_id=session_id,
        exercise_id=exercise_id
    ).first_or_404()

    if not session_exercise:
        return jsonify({'success': False, 'message': 'Error in findind'})

    # Delete associated sets first to maintain referential integrity
    for exercise_set in session_exercise.sets:
        db.session.delete(exercise_set)

    # Remove the session exercise
    db.session.delete(session_exercise)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Exercise removed from session'
    })


@views.route('/delete_session', methods=['POST'])
@login_required
def delete_session():
    session = json.loads(request.data)
    sessionId = session['sessionId']
    session = WorkoutSession.query.get(sessionId)

    if session:
        if session.user_id == current_user.id:
            db.session.delete(session)
            db.session.commit()
            return redirect(url_for('views.tracking'))

    return jsonify({"success": False}), 400


@views.route('/add_exercise_set', methods=['POST'])
@login_required
def add_exercise_set():
    data = request.get_json()

    # Find the session exercise
    session_exercise = SessionExercise.query.filter_by(
        workout_session_id=data['session_id'],
        exercise_id=data['exercise_id']
    ).first_or_404()

    # Create exercise set
    exercise_set = ExerciseSet(
        session_exercise=session_exercise,
        set_number=data['set_number'],
        reps=data['reps'],
        weight=data.get('weight'),
        is_completed=False
    )
    db.session.add(exercise_set)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Set added to exercise'
    })


@views.route('/end_workout_session', methods=['POST'])
@login_required
def end_workout_session():
    data = request.get_json()

    session = WorkoutSession.query.get_or_404(data['session_id'])

    # Update the session notes with the workout name
    session.notes = data.get('workout_name', 'Custom Workout')

    # Commit the changes
    db.session.commit()

    return jsonify({"status": "success", "message": "Workout session ended."})


@views.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    return render_template('account.html', user=current_user)


@views.route('/delete_account', methods=['POST', 'GET'])
@login_required
def delete_account():
    user = current_user

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('views.landing'))


@views.route('/measurements', methods=['POST', 'GET'])
@login_required
def measurements():
    heightForm = HeightForm()
    weightForm = WeightForm()

    if heightForm.validate_on_submit():
        date = Height.query.filter_by(user_id=current_user.id,
                                      date=heightForm.date.data).first()

        # If data exists for the date, update height value
        if date:
            date.height = heightForm.height.data
            db.session.commit()

        # Create a new record if data for the date does not exist
        else:
            new_height = Height(user_id=current_user.id,
                                height=heightForm.height.data,
                                date=heightForm.date.data)

            db.session.add(new_height)
            db.session.commit()

    if weightForm.validate_on_submit():
        date = Weight.query.filter_by(user_id=current_user.id,
                                      date=weightForm.date.data).first()

        # If data exists for the date, update weight value
        if date:
            date.weight = weightForm.weight.data
            db.session.commit()

        # Create a new record if data for the date does not exist
        else:
            new_weight = Weight(user_id=current_user.id,
                                weight=weightForm.weight.data,
                                date=weightForm.date.data)

            db.session.add(new_weight)
            db.session.commit()

    # Get all height records for the current user for graph/table
    height_data = db.session.query(Height.height, Height.date).filter(
        Height.user_id == current_user.id
        ).order_by(Height.date).all()

    heights = [height for height, _ in height_data]
    height_dates = [date.strftime("%d %b %y") for _, date in height_data]
    height_data = zip(heights, height_dates)

    # Get all weight records for the current user for graph/table
    weight_data = db.session.query(Weight.weight, Weight.date).filter(
        Height.user_id == current_user.id
        ).order_by(Weight.date).all()
    weights = [weight for weight, _ in weight_data]
    weight_dates = [date.strftime("%d %b %y") for _, date in weight_data]
    weight_data = zip(weights, weight_dates)

    return render_template('measurements.html',
                           user=current_user,
                           heightForm=heightForm,
                           weightForm=weightForm,
                           height_data=height_data,
                           heights=heights,
                           height_dates=height_dates,
                           weight_data=weight_data,
                           weights=weights,
                           weight_dates=weight_dates)


@views.route('/discard_workout_session', methods=['POST'])
@login_required
def discard_workout_session():
    data = request.get_json()
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({"success": False, "message": "Session ID is required."}), 400

    session = WorkoutSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    if session:
        db.session.delete(session)
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Workout session not found."}), 404
