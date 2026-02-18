from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
import certifi
from datetime import datetime, timedelta, time
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
    try:
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
                series_events = db_handler.get_all_series()
            else:
                events = db_handler.get_events_by_tag_dt(
                    variable, start_date, end_date)
                series_events = db_handler.get_series_by_tag(variable)

        else:
            if variable == "all_events":
                events = db_handler.get_all_events()
                series_events = db_handler.get_all_series()
            else:
                events = db_handler.get_events_by_tag(variable)
                series_events = db_handler.get_series_by_tag(variable)
        # Generate events from series and add them to the events list
        for series in series_events:
            events += generate_daily_events(series, start_date, end_date)

        # Sort all events by date first, then by start time
        # This handles both regular events with 'start_time' and series events where we've set 'start_time'
        events.sort(key=lambda event: (
            event['date']['day'].date(),
            event['date']['start_time'].time(
            ) if event['date']['start_time'] is not None else time(23, 59, 59)
        ))
        return render_template("events.html", events=events, event_type=variable)

    except PyMongoError as e:
        app.logger.exception("Database error while loading events: %s", e)
        # Show a friendlier message instead of a generic 500 error
        return render_template(
            "db_error.html",
            message="We’re having trouble loading events right now. "
                    "This usually means our database is temporarily unavailable or we’ve hit a plan limit. "
                    "Please try again in a few minutes."
        ), 503


def generate_daily_events(series, start_date=None, end_date=None):
    """Generate daily events from a series dynamically without storing them."""
    daily_events = []

    current_date = max(series['start_date'], datetime.now(
    )) if series['start_date'] is not None else datetime.now()
    series_end_date = series['end_date'] if series['end_date'] is not None else current_date + \
        timedelta(days=90)

    if start_date:
        current_date = max(current_date, start_date)
    if end_date and end_date is not None:
        end_date = min(end_date, series_end_date)
    else:
        end_date = series_end_date
    current_date = current_date.replace(
        hour=series['open_time'].hour, minute=series['open_time'].minute)
    while current_date <= end_date:
        event = {
            "name": series['name'],
            "location": series['location'],
            "date": {
                "day": current_date,
                "start_time": series['open_time'],
                "end_time": series['close_time']
            },
            "links": series['links'],
            "tags": series['tags'],
            "isSeries": "True"
        }
        daily_events.append(event)
        current_date += timedelta(days=1)
    return daily_events


@app.route('/api/event/<event_id>')
def get_event(event_id):
    try:
        event = db_handler.get_event_details(event_id)
    except PyMongoError as e:
        app.logger.exception(
            "Database error while loading event details: %s", e)
        return jsonify({
            'error': 'We’re having trouble loading this event right now. '
                     'Please try again in a few minutes.'
        }), 503

    if event:
        return jsonify(event)
    return jsonify({'error': 'Event not found'}), 404


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.exception("Unhandled internal server error: %s", error)
    return render_template(
        "db_error.html",
        message="Something went wrong on our side. "
                "If this keeps happening, please check back later while we fix it."
    ), 500


if __name__ == "__main__":
    if Config.DEVELOPMENT_ENV:
        app.run(debug=Config.DEVELOPMENT_ENV)
    else:
        port = int(Config.PORT)
        app.run(host="0.0.0.0", port=port)
