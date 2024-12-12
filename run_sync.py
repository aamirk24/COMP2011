from app import create_app
from app.models import Exercise


def main():
    app = create_app()
    from app import sync_data

    with app.app_context():
        sync_data(app, Exercise)


if __name__ == '__main__':
    main()