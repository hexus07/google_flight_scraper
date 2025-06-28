import base64
from typing import Any, List, Optional, TYPE_CHECKING, Literal, Union # for better readability and maintainability
import google_flights.flights_pb2 as PB
from dataclasses import dataclass

class FlightData:
    """
    Representation of flight data.

    Args:
        date (str): Date of the flight.
        from_airport (List[str]): Departure airports.
        to_airport (List[str]): Arrival airports.
        airlines (List[str], optional): List of airline codes. Default is null List.
        max_stops (int, optional): Maximum number of stops. Default is None.
        itin_data: (dict, optional): Itinerary data for the flight. Default is None.

    """
    # Attributes of the class (restricting all other atributees of a class)
    __slots__ = ("date", "from_airport", "to_airport", "airlines", "max_stops", "itin_data")
    date: str
    from_airport: List[str]
    to_airport: List[str]
    airlines: Optional[List[str]]

    max_stops: Optional[int]
    itin_data: Optional[dict]

    def __init__( 
        self,
        *,
        date: str,
        from_airport: Union[List[str]],
        to_airport: Union[List[str]],
        airlines: Optional[List[str]] = [],
        max_stops: Optional[int] = None,
        itin_data: Optional[Union[dict, List[dict]]] = None,  # Itinerary data for the flight
    ):
        self.date = date

        self.airlines = [
            airline
            for airline in airlines
        ]
        self.from_airport = [
            airport 
            for airport in from_airport
        ]
        self.to_airport = [
            airport
            for airport in to_airport
        ]
        if max_stops is not None:
            self.max_stops = max_stops
        
        self.itin_data = [
            itin_data
            for itin_data in (itin_data or [{}])
        ]

    def attach(self, info: PB.Info) -> None: 
        
        data = info.data.add()
        data.date = self.date

        for from_airport in self.from_airport:
            from_flight = data.from_flight.add()
            from_flight.airport = from_airport
            from_flight.flag = -1

        for to_airport in self.to_airport:
            to_flight = data.to_flight.add()
            to_flight.airport = to_airport
            to_flight.flag = -1

        if self.airlines:
            data.airlines.extend(self.airlines)


        if self.max_stops is not None:
            data.max_stops = self.max_stops

        for itin in self.itin_data:
            if itin != {}:
                itin_data = data.itin_data.add()
                itin_data.departure_airport = itin.get("departure_airport", "")
                itin_data.departure_date = itin.get("departure_date", "")
                itin_data.arrival_airport = itin.get("arrival_airport", "")
                itin_data.flight_code = itin.get("flight_code", "")
                itin_data.flight_number = str(itin.get("flight_number", ""))

    

class Passengers:
    def __init__(
        self,
        *,
        adults: int = 0,
        children: int = 0,
        infants_in_seat: int = 0,
        infants_on_lap: int = 0,
    ):
        assert (
            sum((adults, children, infants_in_seat, infants_on_lap)) <= 9
        ), "Too many passengers (> 9)"
        assert (
            infants_on_lap <= adults
        ), "You must have at least one adult per infant on lap"
        
        self.pb = []
        self.pb += [PB.Passenger.ADULT for _ in range(adults)]
        self.pb += [PB.Passenger.CHILD for _ in range(children)]
        self.pb += [PB.Passenger.INFANT_IN_SEAT for _ in range(infants_in_seat)]
        self.pb += [PB.Passenger.INFANT_ON_LAP for _ in range(infants_on_lap)]

        self._data = (adults, children, infants_in_seat, infants_on_lap)
    def attach(self, info: PB.Info) -> None:  # type: ignore
        for p in self.pb:
            info.passengers.append(p)

    def __repr__(self) -> str:
        return f"Passengers({self._data})"


class TFSData:
    """``?tfs=`` data. (internal)

    Use `TFSData.from_interface` instead.
    """

    def __init__(
        self,
        *,
        flight_data: List[FlightData],
        seat: PB.Seat,  # type: ignore
        trip: PB.Trip,  # type: ignore
        passengers: Passengers,
    ):
        
        self.flight_data = flight_data
        self.seat = seat
        self.trip = trip
        self.passengers = passengers

    def pb(self) -> PB.Info:  # type: ignore
        info = PB.Info()
        info.seat = self.seat
        info.trip = self.trip

        info.flag_1 = 14  
        info.flag_2 = 1  
        info.flag_3 = -1 

        self.passengers.attach(info)

        for fd in self.flight_data:
            fd.attach(info)

                
        return info

    def to_string(self) -> bytes:
        return self.pb().SerializeToString()

    def as_b64(self) -> bytes:
        return base64.b64encode(self.to_string())

    @staticmethod
    def from_interface(
        *,
        flight_data: List[FlightData],
        trip: Literal["round-trip", "one-way", "multi-city"],
        passengers: Passengers,
        seat: Literal["economy", "premium-economy", "business", "first"],
    ):
        """Use ``?tfs=`` from an interface.

        Args:
            flight_data (list[FlightData]): Flight data as a list.
            trip ("one-way" | "round-trip" | "multi-city"): Trip type.
            passengers (Passengers): Passengers.
            seat ("economy" | "premium-economy" | "business" | "first"): Seat.
        """
        trip_t = {
            "round-trip": PB.Trip.ROUND_TRIP,
            "one-way": PB.Trip.ONE_WAY,
            "multi-city": PB.Trip.MULTI_CITY,
        }[trip]
        seat_t = {
            "economy": PB.Seat.ECONOMY,
            "premium-economy": PB.Seat.PREMIUM_ECONOMY,
            "business": PB.Seat.BUSINESS,
            "first": PB.Seat.FIRST,
        }[seat]

        return TFSData(
            flight_data=flight_data,
            seat=seat_t,
            trip=trip_t,
            passengers=passengers,
        )

    
    def __repr__(self) -> str:
        return (
            f"TFSData(flight_data={self.flight_data}, seat={self.seat}, "
            f"trip={self.trip}, passengers={self.passengers}, max_stops={self.max_stops})"
        )

@dataclass
class ItinerarySummary:
    flights: str
    price: int
    currency: str

    @classmethod
    def from_b64(cls, b64_string: str) -> 'ItinerarySummary':
        raw = base64.b64decode(b64_string)
        pb = PB.ItinerarySummary()
        pb.ParseFromString(raw)
        return cls(pb.flights, pb.price.price / 100, pb.price.currency)