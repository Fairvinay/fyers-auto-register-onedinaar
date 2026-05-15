# fyers_service.py

from flask import Flask, request, jsonify
from fyers_apiv3 import fyersModel
import os
from dotenv import load_dotenv
from flask_cors import CORS
import ssl
from multiprocessing import Process
import requests
import logging

# 🔥 create unsafe SSL context (for local/dev only)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# This loads variables from .env into os.environ
load_dotenv() 

app = Flask(__name__)

# This enables CORS for all routes and all origins
CORS(app)

CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI")

@app.route("/generate-auth-url")
def generate_auth_url():

    session = fyersModel.SessionModel(
        client_id=CLIENT_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code"
    )

    auth_url = session.generate_authcode()

    return jsonify({
        "auth_url": auth_url
    })


@app.route("/generate-token", methods=["POST"])
def generate_token():

    data = request.json
    auth_code = data.get("auth_code")

    print(f"User passed in  auth_code , {auth_code}.")

    print(f"CLIENT_ID, {CLIENT_ID}. You are SECRET_KEY {SECRET_KEY} redirect_uri {REDIRECT_URI}.")
    session = fyersModel.SessionModel(
        client_id=CLIENT_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )
    # Returns True if variable is NOT None AND NOT empty
    if session:
        print("session fyersModel.SessionModel has a value and is not empty.")
    else:
        print("session fyersModel.SessionModel is either None or empty.")
    session.set_token(auth_code)

    #response = session.generate_token()
    # Configure logging to track issues
    #logging.basicConfig(level=logging.INFO)
    #logger = logging.getLogger(__name__)
    token = ""  # Variable created by assignment
    try:
        # Attempt to generate the token
        response = session.generate_token()
        print(f"Token generated {response} ")
        # If using requests, raise exception for 4xx/5xx responses
        #response.raise_for_status() 
    
        token = response #.json().get('token')
        print(f"Token generated successfully.")

    except requests.exceptions.HTTPError as http_err:
        # Handles HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
        print(f"HTTP error occurred: {http_err}")
        # Consider raising a custom exception or returning None
    except requests.exceptions.ConnectionError as conn_err:
        # Handles DNS failures, refused connections
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as time_err:
        #    Handles request timeouts
        print(f"Timeout error occurred: {time_err}")
    except requests.exceptions.RequestException as req_err:
        # Catches any other requests-related exceptions
        print(f"An error occurred during request: {req_err}")
    except ValueError as val_err:
        # Handles JSON decoding errors
        print(f"Error parsing JSON response: {val_err}")
    except Exception as e:
        #   Catches non-requests related exceptions (last resort)
        print(f"An unexpected error occurred: {e}")




    return jsonify(token)


def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT env variable
    cert_file = os.path.join(os.path.dirname(__file__), "ssl.crt/server.crt")
    key_file = os.path.join(os.path.dirname(__file__), "ssl.key/server.key")
    app.run(
        host="0.0.0.0", port=port, debug=False, use_reloader=False 
    )


# new running main
def main():
    # flask_thread = Thread(target=run_flask)
    # flask_thread.start()
    flask_process = Process(target=run_flask)
    flask_process.start()

    print("✅ Flask server started.")

if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000)
    main()
