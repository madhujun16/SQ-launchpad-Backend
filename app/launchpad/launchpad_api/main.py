#!/usr/bin/env python3

import connexion
from launchpad_api import encoder

# Create the Connexion app globally so Flask can find it
app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api(
    'openapi.yaml',
    arguments={'title': 'launchpad API'},
    pythonic_params=True
)

# The actual Flask app is `app.app`
flask_app = app.app

if __name__ == '__main__':
    app.run(port=8080, debug=True)
