from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

# Association
workout_exercise = db.Table('workout_exercise',
                            db.Column('workout.id', db.Integer, db.ForeignKey('workout.id'), primary_key=True),
                            db.Column('exercise.id', db.Integer, db.ForeignKey('exercise.id'), primary_key=True))


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(1000))
    birthdate = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(150), nullable=True)
    county = db.Column(db.String(150), nullable=True)
    country = db.Column(db.String(150), nullable=True)

    # Relationships
    workouts = db.relationship('Workout', back_populates='creator', cascade='all, delete-orphan')
    workout_sessions = db.relationship('WorkoutSession', back_populates='user', cascade='all, delete-orphan')
    heights = db.relationship('Height', back_populates='user', cascade='all, delete-orphan')
    weights = db.relationship('Weight', back_populates='user', cascade='all, delete-orphan')


class Exercise(db.Model):
    __tablename__ = 'exercise'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    target = db.Column(db.String(150))
    secondaryMuscles = db.Column(db.PickleType)
    instructions = db.Column(db.PickleType)
    gifUrl = db.Column(db.String(1000))

    # Relationships
    workouts = db.relationship('Workout', secondary=workout_exercise, back_populates='exercises')
    session_exercises = db.relationship('SessionExercise', back_populates='exercise')

    def add_exercise(self):
        exercise = Exercise.query.get(self.get('id'))

        if not exercise:
            exercise = Exercise(
                id=self.get('id'),
                name=self.get('name'),
                target=self.get('target'),
                secondaryMuscles=self.get('secondaryMuscles'),
                instructions=self.get('instructions'),
                gifUrl=self.get('gifUrl')
            )
            db.session.add(exercise)

        return exercise


class Workout(db.Model):
    __tablename__ = 'workout'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(1000))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    creator = db.relationship('User', back_populates='workouts')
    exercises = db.relationship('Exercise', secondary=workout_exercise, back_populates='workouts')
    workout_sessions = db.relationship('WorkoutSession', back_populates='workout')

    # Converting to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creator_id': self.creator_id,
            'exercises': [exercise.id for exercise in self.exercises]
        }


class WorkoutSession(db.Model):
    __tablename__ = 'workout_session'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=True)  # Optional for custom/empty workouts
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='workout_sessions')
    workout = db.relationship('Workout', back_populates='workout_sessions')
    session_exercises = db.relationship('SessionExercise',
                                        back_populates='workout_session',
                                        cascade='all, delete-orphan')

    # Converting to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'workout_id': self.workout_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'notes': self.notes
        }


class SessionExercise(db.Model):
    __tablename__ = 'session_exercise'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    workout_session_id = db.Column(db.Integer, db.ForeignKey('workout_session.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)  # Track exercise order in session

    # Relationships
    workout_session = db.relationship('WorkoutSession', back_populates='session_exercises')
    exercise = db.relationship('Exercise', back_populates='session_exercises')
    sets = db.relationship('ExerciseSet', back_populates='session_exercise', cascade='all, delete-orphan')

    # Converting to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'exercise_id': self.exercise_id,
            'exercise_name': self.exercise.name,
            'order': self.order,
            'sets': [set.to_dict() for set in self.sets]
        }


class ExerciseSet(db.Model):
    __tablename__ = 'exercise_set'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    session_exercise_id = db.Column(db.Integer, db.ForeignKey('session_exercise.id'), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)

    # Relationships
    session_exercise = db.relationship('SessionExercise', back_populates='sets')

    # Converting to dictionary
    def to_dict(self):
        return {
            'id': self.id,
            'set_number': self.set_number,
            'reps': self.reps,
            'weight': self.weight,
            'is_completed': self.is_completed,
            'rest_time': self.rest_time
        }


class Height(db.Model):
    __tablename__ = 'height'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, unique=False)

    # Relationship
    user = db.relationship('User', back_populates='heights')


class Weight(db.Model):
    __tablename__ = 'weight'

    # Fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, unique=False)

    # Relationship
    user = db.relationship('User', back_populates='weights')
