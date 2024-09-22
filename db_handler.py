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
        self.categories = self.db.categories
        self.series = self.db.series
        self.tz = timezone('EST')

    def insert_source(self, source_data):
        """Insert a new source into the database."""
        return self.sources.insert_one(source_data).inserted_id

    def update_source(self, source_id, updated_data):
        """Update an existing source."""
        updated_data['last_scraped'] = datetime.now(
            tz=self.tz)  # Automatically set last_scraped to current datetime
        return self.sources.update_one({"_id": ObjectId(source_id)}, {"$set": updated_data})

    def insert_event(self, event_data):
        """Insert a new event into the database."""
        return self.events.insert_one(event_data).inserted_id

    def insert_details(self, details_data):
        """Insert event details into the database."""
        return self.details.insert_one(details_data).inserted_id

    def get_events_by_tag(self, tag):
        """Get all events with a specific tag or its sub_tags that are not in the past."""
        current_date = datetime.now(tz=self.tz)

        # Retrieve the category document with the specified tag
        category = self.categories.find_one({"tag_name": tag})

        if not category:
            # Return empty list if the category is not found
            return []

        # Extract sub_tags from the category
        sub_tags = category.get("sub_tags", [])

        # Find all events that have a tag in the sub_tags list
        return list(self.events.find({
            "tags": {"$in": sub_tags},
            "date.day": {"$gte": current_date}
        }))

    def get_events_by_tag_dt(self, tag, start_date, end_date):
        """Get all events with a specific tag or its sub_tags that are not in the past."""

        # Retrieve the category document with the specified tag
        category = self.categories.find_one({"tag_name": tag})

        if not category:
            # Return empty list if the category is not found
            return []

        # Extract sub_tags from the category
        sub_tags = category.get("sub_tags", [])

        # Find all events that have a tag in the sub_tags list
        return list(self.events.find({
            "tags": {"$in": sub_tags},
            "date.day": {"$gte": start_date, "$lte": end_date}
        }))

    def get_all_events(self):
        current_date = datetime.now(tz=self.tz)
        return list(self.events.find({"date.day": {"$gte": current_date}}))

    def get_all_events_dt(self, start_date, end_date):

        return list(
            self.events.find(
                {"date.day": {"$gte": start_date, "$lte": end_date}}
            )
        )

    def get_event_details(self, event_id):
        """Get details for a specific event."""
        details = self.details.find_one({'parent_event': event_id})
        if details:
            details['_id'] = str(details['_id'])
        return details

    def get_events_by_source(self, source_id):
        """Get all events for a specific source."""
        return list(self.events.find({"source_id": source_id}))

    def get_events_by_source_dt(self, source_id, start_date, end_date):
        """Get all events for a specific source within a specified date range."""
        return list(
            self.events.find(
                {
                    "source_id": source_id,
                    "date.day": {"$gte": start_date, "$lte": end_date}
                }
            )
        )

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

    def delete_past_events(self):
        """Delete all events from prior to today"""
        current_date = datetime.now(tz=self.tz)
        past_events = list(self.events.find(
            {"date.day": {"$lt": current_date}}))
        for event in past_events:
            self.delete_event(event['_id'])
        print(f"Deleted {len(past_events)} past events")

    def get_all_sources(self):
        return [Source(**source) for source in self.sources.find()]

    def get_all_series(self):
        current_date = datetime.now(tz=self.tz)
        return list(self.series.find({"$or": [
            {"enddate": {"$gte": current_date}},
            {"enddate": None}
        ]}))

    def get_series_by_tag(self, tag):
        current_date = datetime.now(tz=self.tz)
        category = self.categories.find_one({"tag_name": tag})

        if not category:
            # Return empty list if the category is not found
            return []

        # Extract sub_tags from the category
        sub_tags = category.get("sub_tags", [])

        return list(self.series.find({
            "tags": {"$in": sub_tags},
            "$or": [
                {"enddate": {"$gte": current_date}},
                {"enddate": None}
            ]
        }))

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
