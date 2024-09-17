from dataclasses import dataclass, asdict, field
import datetime
from typing import List, Dict, Optional, Union


@dataclass
class Event:
    name: str
    tags: List[str]
    date: Dict[str, Union[str, int, datetime.datetime, datetime.time]]
    performer: str
    price: float
    links: Dict[str, str]
    source_id: str
    location: Optional[str]
    _id: Optional[str] = field(default=None)

    def __post_init__(self):
        # Convert date strings to datetime objects
        if isinstance(self.date.get('day'), str):
            self.date['day'] = datetime.datetime.fromisoformat(
                self.date['day'])
        if isinstance(self.date.get('start_time'), str):
            self.date['start_time'] = datetime.datetime.strptime(
                self.date['start_time'], "%H:%M").time()

    def to_dict(self):
        event_dict = asdict(self)
        if event_dict['_id'] is None:
            del event_dict['_id']
        return event_dict


@dataclass
class Source:
    venue: str
    link: str
    scraper: Optional[str]
    _id: Optional[str] = field(default=None)
    last_scraped: Optional[datetime.datetime] = field(
        default=None)  # New field added

    def to_dict(self):
        source_dict = asdict(self)
        if source_dict['_id'] is None:
            del source_dict['_id']
        if source_dict['last_scraped'] is None:
            del source_dict['last_scraped']
        return source_dict


@dataclass
class Detail:
    age_limit: int
    league: Optional[str]
    teams: Optional[Dict[str, str]]
    drink_minimum: Optional[float]
    genre: Optional[str]
    tournament_name: Optional[str]
    details: Optional[Dict[str, str]]
    sport: Optional[str]
    event_id: str
    _id: Optional[str] = field(default=None)

    def to_dict(self):
        desc_dict = asdict(self)
        if desc_dict['_id'] is None:
            del desc_dict['_id']
        return desc_dict


@dataclass
class Category:
    tag_name: str
    sub_tags: List[str]
    _id: Optional[str] = field(default=None)

    def to_dict(self):
        desc_dict = asdict(self)
        if desc_dict['_id'] is None:
            del desc_dict['_id']
        return desc_dict


@dataclass
class EventSeries:
    name: str
    location: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    open_time: datetime.time
    close_time: datetime.time
    links: Dict[str, str]
    tags: list
    _id: Optional[str] = field(default=None)

    def to_dict(self):
        series_dict = asdict(self)
        if series_dict['_id'] is None:
            del series_dict['_id']
        return series_dict
