from flask import Flask, redirect, url_for, session, request, jsonify
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import datetime
from calendar_service import calendar_bp

app = Flask(__name__)
app.secret_key = os.urandom(24)
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Register the calendar blueprint
app.register_blueprint(calendar_bp, url_prefix='/api')

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=credentials)
    events_result = service.events().list(calendarId='primary', timeMin=datetime.datetime.utcnow().isoformat() + 'Z', maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])
    return jsonify(events)

@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        'client_secret.json', scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    print("flow",request.args)
    if 'code' not in request.args:
        auth_uri, _ = flow.authorization_url(prompt='consent')
        print("ccc")
        return redirect(auth_uri)
    else:
        flow.fetch_token(authorization_response=request.url)
        session['credentials'] = flow.credentials_to_dict()
        print("eee")
        return redirect(url_for('index'))

@app.route('/add_event', methods=['POST'])
def add_event():
    if 'credentials' not in session:
        return redirect(url_for('oauth2callback'))
    credentials = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=credentials)
    event = {
        'summary': request.form['summary'],
        'description': request.form.get('description', ''),
        'start': {
            'dateTime': request.form['start_datetime'],
            'timeZone': 'YOUR_TIME_ZONE_HERE',
        },
        'end': {
            'dateTime': request.form['end_datetime'],
            'timeZone': 'YOUR_TIME_ZONE_HERE',
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify(event)

if __name__ == '__main__':
    app.run(debug=True)
