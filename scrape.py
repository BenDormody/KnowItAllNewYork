from db_handler import DBHandler
from scrapers.scraper_factory import get_scraper


def main():

    db_handler = DBHandler()

    # Get all sources from the database
    sources = db_handler.get_all_sources()

    for source in sources:
        try:
            scraper = get_scraper(source, db_handler)
            print(f"trying: {source.venue}")
            scraper.run()
            print(f"Scraping completed for {source.venue}")
        except ValueError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"An error occurred while scraping {source.venue}: {str(e)}")

    db_handler.close_connection()


if __name__ == "__main__":
    main()
