from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from datetime import datetime
from pytz import timezone
from config import Config
from db_handler import DBHandler

db_handler = DBHandler()

app = Flask(__name__)

tz = timezone('EST')


@app.route("/")
def index():
    return render_template("home.html")


@app.route('/events/<variable>')
def events(variable):
    if variable == "all_events":
        events = db_handler.get_all_events()
    else:
        events = db_handler.get_events_by_tag(variable)
    return render_template("events.html", events=events, event_type=variable)


@app.route('/api/event/<event_id>')
def get_event(event_id):
    event = db_handler.get_event_details(event_id)
    if event:
        return jsonify(event)
    return jsonify({'error': 'Event not found'}), 404


if __name__ == "__main__":
    if Config.DEVELOPMENT_ENV:
        app.run(debug=Config.DEVELOPMENT_ENV)
    else:
        port = int(Config.PORT)
        app.run(host="0.0.0.0", port=port)
