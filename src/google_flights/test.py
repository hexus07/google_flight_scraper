from filter import create_filter
from flights_pb_implem import FlightData, Passengers, TFSData
from main import get_one_way_options, get_round_trip_options, get_booking_url

flight_filter_one_way = create_filter(
    flight_data=[
        FlightData(
            date="2026-04-20",
            from_airport=["FRA"],
            to_airport=["BER"],
            airlines=['LH']
        ),
        FlightData(
            date="2026-04-30",
            from_airport=["BER"],
            to_airport=["FRA"],
        ),
    ],
    trip="round-trip",
    passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
    seat="economy",
    max_stops=0,  # Direct flights only
)
options = get_round_trip_options(flight_filter_one_way, sort = 'top_flight', number_of_options=1)

print(options)

