from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import requests

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "app.db"

EXERCISE_DB_API_URL = "https://exercisedb.p.rapidapi.com/exercises"
API_KEY = "03b7d82e16mshab008f6186e501bp1d7bc7jsn23666f9bad67"


def get_exercises(limit, offset):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    params = {
        "limit": limit,  # Number of exercises to fetch
        "offset": offset  # Starting point for pagination

    }
    response = requests.get(EXERCISE_DB_API_URL, headers=headers, params=params)

    if response.status_code == 200:
        # Return the exercises as JSON
        return response.json()
    else:
        # Handle error response
        return None


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from .views import views
    from .auth import auth

    from .models import User, Exercise

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()
        sync_data(app, Exercise)

    login_manager = LoginManager()
    login_manager.login_view = 'views.landing'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def sync_data(app, Exercise):
    with app.app_context():

        Exercise.query.delete()
        db.session.commit()

        exercise_count = Exercise.query.count()

        if exercise_count == 0:
            offset = 0
            limit = 100

            while True:
                exercises = get_exercises(limit=limit, offset=offset)

                if not exercises:
                    break

                # Prepare a list of Exercise objects
                exercise_objects = [
                    Exercise(
                        name=exercise_data.get('name'),
                        target=exercise_data.get('target'),
                        secondaryMuscles=exercise_data.get('secondaryMuscles', []),
                        instructions=exercise_data.get('instructions', []),
                        gifUrl=exercise_data.get('gifUrl')
                    )
                    for exercise_data in exercises
                ]

                # Bulk insert
                db.session.bulk_save_objects(exercise_objects)
                db.session.commit()

                offset += limit
