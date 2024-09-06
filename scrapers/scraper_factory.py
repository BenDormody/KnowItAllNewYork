from models import Source
from db_handler import DBHandler
from scrapers.msg_scraper import MSGScraper


def get_scraper(source: Source, db_handler: DBHandler):

    if source.scraper == "MSGScraper":
        return MSGScraper(source, db_handler)
    # Add more conditions for other venues
    else:
        raise ValueError(f"No scraper available for venue: {source.venue}")
