from app import create_app

flask_run = create_app()

if __name__ == "__main__":
    flask_run.run(debug = True)