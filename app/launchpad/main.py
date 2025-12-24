import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from launchpad_api.main import get_main_app

# Get Connexion app
connexion_app = get_main_app()

# Extract actual Flask app from it
app = connexion_app.app

if __name__ == '__main__':
    app.run(port=8080, debug=True, host='0.0.0.0')
