import os
import requests

from flask import Flask, request

os.environ["BOT_ID"] = "7a825a4574e5e534bd9b3ba9c5"
os.environ["PORT"] = "8080"

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'You could put any content here you like, perhaps even a homepage for your bot!'


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

    return 'ok', 200


def send(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('BOT_ID'),
        'text': msg,
    }
    r = requests.post(url, json=data)
    print("GroupMe response: " + str(r))
