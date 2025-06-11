from filter import create_filter
from flights_pb_implem import FlightData, Passengers, TFSData
from main import get_flights_from_filter, get_booking_url, get_round_trip_options, get_one_way_options
from search import search_airline, search_airport
from decoder import DecodedResult

itinerary1 = {
    "departure_airport": "ORY",
    "departure_date": "2025-07-20",
    "arrival_airport": "MAD",
    "flight_code": "UX",
    "flight_number": "1028"
}


itinerary2 = {
    "departure_airport": "MAD",
    "departure_date": "2025-07-25",
    "arrival_airport": "ORY",
    "flight_code": "UX",
    "flight_number": "1029"
}

departure_date = [2025, 7, 20]  # Departure date: 2025-07-20

print(f"{departure_date[0]}-{departure_date[1]:02d}-{departure_date[2]:02d}")

flight_filter = create_filter(flight_data = [
            FlightData(
                airlines= []  ,  # Airline code (optional)
                date="2025-07-20",  # Date of departure
                from_airport=["VNO"],  # Departure airport
                to_airport=["MAD"],  # Itinerary data (optional)
                #itin_dataitinerary1=,  # Itinerary data (optional)
            ), FlightData(
                airlines= []  ,  # Airline code (optional)
                date="2025-07-25",  # Date of departure
                from_airport=["MAD"],  # Departure airport
                to_airport=["VNO"],
                #itin_data=itinerary2,  # Itinerary data (optional)
            )
        ],
        trip="round-trip",  # Trip type
        passengers=Passengers(adults=2, children=1, infants_in_seat=0, infants_on_lap=0),  # Passengers
        seat="economy",  # Seat type
        max_stops=1,  # Maximum number of stops
    )


flight_filter1 = create_filter(flight_data = [
            FlightData(
                airlines= []  ,  # Airline code (optional)
                date="2025-07-20",  # Date of departure
                from_airport=["VNO"],  # Departure airport
                to_airport=["MAD"],  # Itinerary data (optional)
                #itin_dataitinerary1=,  # Itinerary data (optional)
            )],
        trip="one-way",  # Trip type
        passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),  # Passengers
        seat="economy",  # Seat type
        max_stops=1,  # Maximum number of stops
    )

# Get flights from the filter
one_way_flights = get_one_way_options(flight_filter1)

for flight in one_way_flights:
    print(flight.get("url"))