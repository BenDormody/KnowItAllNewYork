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

    @abstractmethod
    def scrape_event_details(self, event: Event):
        pass

    def run(self):
        events = self.scrape_events()
        for event in events:
            if not self.db_handler.is_event_in_database(event):
                # Insert the event and get its ID
                event_id = self.db_handler.insert_event(event.to_dict())
                # Scrape event details and insert them
                event_details = self.scrape_event_details(event)
                event_details.event_id = str(event_id)
                self.db_handler.insert_details(event_details.to_dict())
            '''else:
                print(
                    f"Event '{event.name}' on {event.date['day']} at {event.date['start_time'].time()} already exists in the database.")'''
