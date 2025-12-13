from .launchpad_api.main import get_main_app

# Get Connexion app
connexion_app = get_main_app()

# Extract actual Flask app from it
app = connexion_app.app

if __name__ == '__main__':
    app.run(port=8080, debug=True)
