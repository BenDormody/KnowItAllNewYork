from abc import ABC, abstractmethod
from models import Source, Event, Detail
from db_handler import DBHandler


class BaseScraper(ABC):
    def __init__(self, source: Source, db_handler: DBHandler):
        self.source = source
        self.db_handler = db_handler

    @abstractmethod
    def scrape_events(self):
        pass

    def run(self):
        events_and_details = self.scrape_events()
        for event, details in events_and_details:
            if not self.db_handler.is_event_in_database(event):
                # Insert the event and get its ID
                event_id = self.db_handler.insert_event(event.to_dict())
                # Update the details with the event_id and insert them
                details.event_id = str(event_id)
                self.db_handler.insert_details(details.to_dict())
            else:
                print(
                    f"Event '{event.name}' on {event.date['day']} at {event.date['start_time']} already exists in the database.")
