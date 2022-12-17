from __future__ import print_function

import os
import requests

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from flask import Flask, request

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

os.environ["BOT_ID"] = "7a825a4574e5e534bd9b3ba9c5"
os.environ["PORT"] = "8080"

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'You could put any content here you like, perhaps even a homepage for your bot!'

def get_next_10():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=1024)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='umh7cerge6kqga6c88i0117j24@group.calendar.google.com', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)


@app.route('/', methods=['POST'])
def receive():
    print('Incoming message:')
    print(request.get_json())
    data = request.get_json()
    print(data['text'])

    # Prevent self-reply
    if data['sender_type'] != 'bot':
        if data['text'].startswith('/ping'):
            send(data['name'] + ' pinged me!')
        elif data['text'].startswith('/schedule'):
            get_next_10()

    return 'ok', 200


def send(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('BOT_ID'),
        'text': msg,
    }
    r = requests.post(url, json=data)
    print("GroupMe response: " + str(r))
