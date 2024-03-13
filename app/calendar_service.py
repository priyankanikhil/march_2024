import traceback
from flask import request, jsonify, session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from flask import Blueprint

calendar_bp = Blueprint('calendar', __name__)

def get_calendar_service(credentials):
    """
    Create a Google Calendar service using the provided credentials.
    """
    try:
        service = build('calendar', 'v3', credentials=credentials)
        print(credentials, "credential")
    except Exception as e:
        print("The API client is not authenticated.")
        raise e
    return service

@calendar_bp.route('/calendars', methods=['GET'])
def list_calendars():
    """
    Get all calendars and their IDs.
    """
    try:
        credentials = Credentials(**session.get('credentials'))
        service = get_calendar_service(credentials)
        calendars = service.calendarList().list().execute()
        return jsonify(calendars)
    except ValueError as e:
        traceback.print_exc()
        print(e, "exception")
        return jsonify({'error': str(e)}), 400

@calendar_bp.route('/events/<calendar_id>', methods=['GET'])
def list_events(calendar_id):
    """
    Get all events corresponding to the given calendar ID.
    """
    credentials = Credentials(**session.get('credentials'))
    service = get_calendar_service(credentials)
    events = service.events().list(calendarId=calendar_id).execute()
    return jsonify(events)

@calendar_bp.route('/events/<calendar_id>', methods=['POST'])
def add_event(calendar_id):
    """
    Add an event to the specified calendar.
    """
    credentials = Credentials(**session.get('credentials'))
    service = get_calendar_service(credentials)
    event_data = request.json.get('event_data')
    event = service.events().insert(calendarId=calendar_id, body=event_data).execute()
    return jsonify(event)
