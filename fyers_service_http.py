# fyers_service.py

from flask import Flask, request, jsonify
from fyers_apiv3 import fyersModel
import os
from dotenv import load_dotenv
from flask_cors import CORS
import ssl
from multiprocessing import Process


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

    session = fyersModel.SessionModel(
        client_id=CLIENT_ID,
        secret_key=SECRET_KEY,
        redirect_uri=REDIRECT_URI,
        response_type="code",
        grant_type="authorization_code"
    )

    session.set_token(auth_code)

    response = session.generate_token()

    return jsonify(response)


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
