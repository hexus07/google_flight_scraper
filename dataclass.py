from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


@dataclass
class Result:
    current_price: Literal["low", "typical", "high"]
    flights: List[Flight]


@dataclass
class Flight:
    is_best: bool
    airline_name: str
    flight_number: str
    flight_class: str
    operator: Optional[str]
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
    delay: Optional[str]
    stops: int
    plane: str
    emissions: Optional[str]
    price: str
    #flight_id: str
