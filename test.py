from filter import create_filter, Passengers
from flights_pb_implem import FlightData
from main import get_flights_from_filter

def test_workflow():
    # Step 1: Create a filter
    print("Creating filter...")
    flight_filter = create_filter(
        flight_data=[
            FlightData(
                airlines=["BT", "FR"],  # Airline code (optional)
                date="2025-07-25",  # Date of departure
                from_airport=["MAD"],  # Departure airport
                to_airport=["KUN", "VNO"],  # Arrival airports
            ),
        ],
        trip="one-way",  # Trip type
        passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),  # Passengers
        seat="economy",  # Seat type
        max_stops=1,  # Maximum number of stops
    )
    print("Filter created successfully.")

    # Step 2: Fetch flight data using the filter
    print("Fetching flight data...")
    try:
        flight_data = get_flights_from_filter(flight_filter, data_source='js', mode="common")
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return

    # Step 3: Process and display the results
    if flight_data is not None:
        print("\nBest Flights:")
        if flight_data.best:
            for flight in flight_data.best:
                print(flight)
                print()
        else:
            print("No best flights found or the best result in Other Flights (All Flights).") # When applying filter for airline, Google Flights in most cases segregates them into "All Flights" and "Best Flights", insead of "Best Flights" and "Other Flights". 

        print("\nOther Flights:")
        if flight_data.other:
            for flight in flight_data.other:
                print(flight)
                print()
        else:
            print("No other flights found.")
    else:
        print("No flight data returned.")

if __name__ == "__main__":
    test_workflow()