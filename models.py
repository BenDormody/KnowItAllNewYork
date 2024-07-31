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
    address: str
    link: str
    _id: Optional[str] = field(default=None)

    def to_dict(self):
        source_dict = asdict(self)
        if source_dict['_id'] is None:
            del source_dict['_id']
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
