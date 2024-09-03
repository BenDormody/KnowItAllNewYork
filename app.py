from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from datetime import datetime
from pytz import timezone
from config import Config
from db_handler import DBHandler
import scrape

db_handler = DBHandler()

app = Flask(__name__)
DEVELOPMENT_ENV = True

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
    return render_template("events.html", events=events, event_type = variable)


@app.route('/api/event/<event_id>')
def get_event(event_id):
    event = db_handler.get_event_details(event_id)
    if event:
        return jsonify(event)
    return jsonify({'error': 'Event not found'}), 404


@app.route('/events/scrape_main')
def scrap_main():
    scrape.main()
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)
