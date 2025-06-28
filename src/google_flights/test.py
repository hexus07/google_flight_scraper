from filter import create_filter
from flights_pb_implem import FlightData, Passengers, TFSData
from main import get_one_way_options, get_round_trip_options, get_booking_url

# 1) One-way, direct only, economy, specific airline (UX), single adult
flight_filter_round = create_filter(
    flight_data=[
        FlightData(
            date="2025-08-01",
            from_airport=["MAD"],
            to_airport=["BCN"],
        ),          
            FlightData(           
            date="2025-08-09",
            from_airport=["BCN"],
            to_airport=["MAD"],
        ),
    ],
    trip="round-trip",
    passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
    seat="economy",
)

for option in get_round_trip_options(flight_filter_round, number_of_options=1, currency="UAH", language="ru-UA"):
    print(option)
    print('\n')


flight_filter_one_way = create_filter(
    flight_data=[
        FlightData(
            date="2025-08-01",
            from_airport=["MAD"],
            to_airport=["BCN"],
        ),          
    ],
    trip="one-way",
    passengers=Passengers(adults=2, children=1, infants_in_seat=0, infants_on_lap=0),
    seat="economy",
    max_stops=0,  # Direct flights only
)

for option in get_one_way_options(flight_filter_one_way):
    print(option)
    print('\n')



