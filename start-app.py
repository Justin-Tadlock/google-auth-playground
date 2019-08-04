import json
import requests
import httplib2

from flask import (
    Flask,
    jsonify,
    session as login_session,
    redirect,
    url_for,
    request,
    make_response,
    render_template
)

from google.oauth2 import id_token
from google.auth.transport import requests


# Set up the application
app = Flask(__name__)
try:
    app.secret_key = open('secret_key.txt', 'r').read()
except:
    print('Error: Please create a \'secret_key.txt\' file within the app\'s directory')


# Get Secrets Data
try:
    SECRET_DATA = json.loads(open('client_secrets.json', 'r').read())['web']
    CLIENT_ID = SECRET_DATA['client_id']
    CLIENT_SECRET = SECRET_DATA['client_secret']

    # Get the redirect uri from the file in the form of '/url'
    CLIENT_REDIRECT = SECRET_DATA['redirect_uris'][0]
    CLIENT_REDIRECT = '/%s' % (CLIENT_REDIRECT.split('/')[-1])
except:
    print('Error: Please download your \'client_secrets.json\' file from your \'https://console.developers.google.com\' project')

# Create data used to print into the user posts table
user_posts = [
    {"name": "Billy", "secret": "Likes Polka dot patterns, but will never admit it."},
    {"name": "Bobby", "secret": "Thinks Billy needs a shower."},
    {"name": "Lauren", "secret": "Wants John to ask her out"},
    {"name": "John", "secret": "Wants to ask Lauren out, but she's always so cold to him. He's not sure if he should ask her or not."}
]


def Is_Authenticated():
    logged_in = False

    if 'user' in login_session:
        logged_in = True

    return logged_in


@app.route(CLIENT_REDIRECT, methods=['POST'])
def Authentication_Callback():
    try:
        # Check if the POST request is trying to log in
        if 'idtoken' in request.form:
            if not Is_Authenticated():
                # Get the token from the POST form
                token = request.form['idtoken']

                # Specify the CLIENT_ID of the app that accesses the backend:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                    CLIENT_ID
                )

                verified_providers = [
                    'accounts.google.com',
                    'https://accounts.google.com'
                ]

                if idinfo['iss'] not in verified_providers:
                    raise ValueError('Wrong issuer.')

                # ID token is valid.
                # Get the user's Google Account ID from the decoded token.
                userid = idinfo['sub']

                # Add the token to the flask session variable
                login_session['user'] = token

                ret_response = make_response(
                    jsonify(
                        message='Successfully verified. You are logged in!',
                        status=200)
                )

            # If the user is already logged in,
            # we don't need to do any authentication.
            else:
                ret_response = make_response(
                    jsonify(message='User is already logged in.', status=201)
                )

        # If the POST request does not contain the idtoken field,
        # that means we are trying to log out.
        else:
            # When we have a logged in user,
            # we should remove their token from our
            # logged in sessions variable
            if Is_Authenticated():
                login_session.pop('user', None)

            ret_response = make_response(
                jsonify(message="User has been logged out", status=200)
            )

    except ValueError:
        # Invalid token
        ret_response = make_response(
            jsonify(message='Error: unable to verify token id', status=401)
        )

    return ret_response


@app.route('/')
def Index():
    return render_template(
        'index.html',
        client_id=CLIENT_ID,
        authenticated=Is_Authenticated(),
        user_posts=user_posts
    )


if __name__ == '__main__':
    app.debug = True
    app.run(
        host='0.0.0.0',
        port=5000
    )
