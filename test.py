from filter import create_filter, Passengers
from flights_pb_implem import FlightData
from main import get_flights_from_filter

def __main__():

    # TESTING PURPOSES ONLY
    filter = create_filter(
    flight_data=[
        # Include more if it's not a one-way trip
        FlightData(
            date="2025-07-21",  # Date of departure
            from_airport=["VNO"],  # Departure (airport)
            to_airport=["RIX"],  # Arrival (airport)
        ),
    ],
    trip="one-way",  # Trip type
    passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),  # Passengers
    seat="economy",  # Seat type
    max_stops=1,  # Maximum number of stops
    
    )
    #print(filter.as_b64().decode("utf-8"))
    #flight_data = get_flights_from_filter(filter, data_source='html', mode="local")
    flight_data = get_flights_from_filter(filter, data_source='js', mode="common")

    if flight_data is not None:
        print('Best:')
        for flight in flight_data.best:
            print(flight)
            print()

if __name__ == "__main__":
    __main__()