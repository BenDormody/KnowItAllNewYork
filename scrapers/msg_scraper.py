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
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 5)

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

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        events_and_details = []

        for event_elem in soup.select("[class*='EventCard_card__']"):
            # Extract the name of the event
            # If the name is not specified we take the performer name instead
            name_elem = event_elem.find(
                'div', class_='EventCard_subtitle__YJCXM')
            if name_elem:
                name = name_elem.text.strip()
            else:
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
            ticket_tag = event_elem.find(
                'a', class_='Button_primary__IKq4E')
            if ticket_tag is not None:
                ticket_link = ticket_tag['href']
            elif event_elem.find('a', class_='Button_onsale__decsL') is not None:
                ticket_link = event_elem.find(
                    'a', class_='Button_onsale__decsL')['href']
            else:
                ticket_link = None
            # Extract the link to view event details
            details_link = event_elem.find(
                'a', class_='Button_secondary__Al6Z7')['href']

            # Scrape event details from the details link
            event_details_for_event, event_details = self.scrape_event_details(
                details_link)
            print(event_details_for_event)
            event = Event(
                name=name,
                tags=event_details_for_event.get("tags"),
                date={"day": date.date().isoformat(), "start_time": start_time},
                performer=event_details_for_event.get("performer"),
                price=price,
                location=event_details_for_event.get("location"),
                links={"ticket": ticket_link, "details": details_link},
                source_id=str(self.source._id)
            )
            if not self.is_duplicate(event, [e for e, _ in events_and_details]):
                events_and_details.append((event, event_details))

        self.driver.quit()
        return events_and_details

    def scrape_event_details(self, link):
        self.driver.get(link)
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".T55Ty")))
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Page source at error:")
            print(self.driver.page_source)
            return {}, Detail(
                age_limit=None,
                league=None,
                teams=None,
                drink_minimum=None,
                genre=None,
                tournament_name=None,
                details={"short": "Details not available",
                         "long": "Unable to retrieve details for this event."},
                sport=None,
                event_id=""
            )

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        performer_elem = soup.select_one("h1._1bZlN")
        performer = performer_elem.text.strip() if performer_elem else None

        event_name_elem = soup.select_one("p._1hMLF")
        event_name = event_name_elem.text.strip() if event_name_elem else None

        location_elem = soup.select_one("p._19NH9")
        location = location_elem.text.strip() if location_elem else "Location not available"

        overview_elem = soup.select_one("p.eyebrow")
        if overview_elem:
            short_description_elem = overview_elem.find_next_sibling(
                "div", class_="x17BN")
            short_description = short_description_elem.get_text(
                strip=True) if short_description_elem else "Overview not available"
        else:
            short_description = "Overview not available"

        long_description_elem = soup.select_one("div.x17BN")
        long_description = long_description_elem.get_text(
            strip=True) if long_description_elem else "Full details not available"

        tags = []
        tags_elem = soup.select_one("p.eyebrow")
        tag = tags_elem.text.strip() if tags_elem else "Tags not available"
        tags.append(tag)

        return {
            "performer": performer,
            "event_name": event_name,
            "location": location,
            "tags": tags
        }, Detail(
            age_limit=None,
            league=None,
            teams=None,
            drink_minimum=None,
            genre=None,
            tournament_name=None,
            details={
                "short": short_description,
                "long": long_description
            },
            sport=None,
            event_id=""
        )

    def is_duplicate(self, new_event, existing_events):
        for event in existing_events:
            if (event.name == new_event.name and
                event.date['day'] == new_event.date['day'] and
                    event.date['start_time'] == new_event.date['start_time']):
                return True
        return False
