import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from models import Source, Event, Detail
from scrapers.base_scraper import BaseScraper
import time


class MSGScraper(BaseScraper):
    def __init__(self, source, db_handler):
        super().__init__(source, db_handler)  # Call the base class initializer
        # Initialize the Chrome WebDriver
        # Specify the path to your ChromeDriver
        self.driver = webdriver.Firefox()
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_events(self):
        url = self.source.link
        self.driver.get(url)

        # Wait for the JavaScript content to load
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[class*='EventCard_card__']")))
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Page source at error:")
            print(self.driver.page_source)
            self.driver.quit()
            return []

        # Optional: Give some extra time to ensure all content is loaded
        time.sleep(5)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        events = []

        for event_elem in soup.select("[class*='EventCard_card__']"):
            # Extract the name of the event
            name = event_elem.find(
                'div', class_='EventCard_title__4Vkof').text.strip()

            # Extract the date components
            day_of_week = event_elem.find(
                'div', class_='EventCard_day-of-week__0fbbn').text.strip()
            day_of_month = event_elem.find(
                'div', class_='EventCard_day-of-month__tiss0').text.strip()
            month_year = event_elem.find(
                'div', class_='EventCard_month-year__jk8J2').text.strip()

            # Combine the date components into a single string
            date_str = f"{day_of_week} {day_of_month} {month_year}".replace(
                '‘', '')
            date = datetime.strptime(date_str, "%a %d %b %y")
            # Extract the start time
            start_time_str = event_elem.find(
                'div', class_='EventCard_showtimes-container__VMcWp').text.strip()
            start_time = datetime.strptime(start_time_str.split(" ")[
                                           0], "%I:%M%p")

            # Extract the performer
            performer = event_elem.find(
                'div', class_='EventCard_event-details__qURNZ').text.strip()

            # Extract the price (you may need to adjust this depending on the actual structure)
            price_elem = event_elem.find('span', class_='price')
            if price_elem:
                price = float(price_elem.text.strip().replace('$', ''))
            else:
                price = 0.0  # Default price if not found

            # Extract the link to buy tickets
            link = event_elem.find('a', class_='Button_button__Bw_LG')['href']

            event = Event(
                name=name,
                tags=["MSG", "Concert"],  # Example tags
                # Example start time
                date={"day": date.date().isoformat(),
                      "start_time": start_time},
                performer=performer,
                price=price,
                links={"ticket": link},
                source_id=str(self.source._id)
            )
            if not self.is_duplicate(event, events):
                events.append(event)

        self.driver.quit()
        return events

    def scrape_event_details(self, event: Event):
        # In a real scenario, you might need to visit the event's specific page
        # Here, we're creating example details
        return Detail(
            age_limit=None,
            league=None,
            teams=None,
            drink_minimum=None,
            genre=None,
            tournament_name=None,
            details={"short": f"{event.name} at MSG",
                     "long": f"Enjoy {event.name} performed by {event.performer} at Madison Square Garden."},
            sport=None,
            event_id=""  # This will be filled in the run method
        )

    def is_duplicate(self, new_event, existing_events):
        """
        Check if the new_event already exists in the existing_events list.
        """
        for event in existing_events:
            if (event.name == new_event.name and
                event.date['day'] == new_event.date['day'] and
                    event.date['start_time'] == new_event.date['start_time']):
                return True
        return False
