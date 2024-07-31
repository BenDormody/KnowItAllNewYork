from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi
from datetime import datetime
from pytz import timezone
from config import Config
from models import Source, Event, Detail


class DBHandler:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI, tlsCAFile=certifi.where())
        self.db = self.client.get_database('KIANY')
        self.sources = self.db.sources
        self.events = self.db.events
        self.details = self.db.details
        self.tz = timezone('EST')

    def insert_source(self, source_data):
        """Insert a new source into the database."""
        return self.sources.insert_one(source_data).inserted_id

    def insert_event(self, event_data):
        """Insert a new event into the database."""
        return self.events.insert_one(event_data).inserted_id

    def insert_details(self, details_data):
        """Insert event details into the database."""
        return self.details.insert_one(details_data).inserted_id

    def get_events_by_tag(self, tag):
        """Get all events with a specific tag that are not in the past."""
        current_date = datetime.now(tz=self.tz)
        return list(self.events.find({"tag": tag, "date": {"$gte": current_date}}).sort("date"))

    def get_event_details(self, event_id):
        """Get details for a specific event."""
        details = self.details.find_one({'parent_event': event_id})
        if details:
            details['_id'] = str(details['_id'])
        return details

    def get_events_by_source(self, source_id):
        """Get all events for a specific source."""
        return list(self.events.find({"source_id": source_id}))

    def update_event(self, event_id, updated_data):
        """Update an existing event."""
        return self.events.update_one({"_id": ObjectId(event_id)}, {"$set": updated_data})

    def update_details(self, details_id, updated_data):
        """Update existing event details."""
        return self.details.update_one({"_id": ObjectId(details_id)}, {"$set": updated_data})

    def delete_event(self, event_id):
        """Delete an event and its associated details."""
        self.details.delete_one({"parent_event": event_id})
        return self.events.delete_one({"_id": ObjectId(event_id)})

    def get_all_sources(self):
        return [Source(**source) for source in self.sources.find()]

    def is_event_in_database(self, event):
        """
        Check if the event already exists in the database.
        """
        query = {
            'name': event.name,
            'date.day': event.date['day'],
            'date.start_time': event.date['start_time']
        }
        return self.events.find_one(query) is not None

    def close_connection(self):
        """Close the database connection."""
        self.client.close()
