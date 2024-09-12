from flask import Flask, render_template, jsonify, request
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

    # Get optional query parameters
    start_date = request.args.get('startdate')
    end_date = request.args.get('enddate')

    # Validate and parse the dates
    if start_date and end_date:
        try:
            # Try to parse the dates
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            # Handle invalid date format by returning an error or a message
            return "Invalid date format. Please use YYYY-MM-DD.", 400
        if variable == "all_events":
            events = db_handler.get_all_events_dt(start_date, end_date)
        else:
            events = db_handler.get_events_by_tag_dt(
                variable, start_date, end_date)

    else:
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
