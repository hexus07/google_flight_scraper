import base64
from flights_pb2 import (
    BookingRequest,
    FlightData,
    ItineraryData,
    Airport,
)

# build the two FlightData messages
fd1 = FlightData(
    date="2025-07-20",
    itin_data=ItineraryData(
        departure_airport="OTP",
        departure_date="2025-07-20",
        arrival_airport="MAD",
        flight_code="W4",
        flight_number="3173",
    ),
    max_stops=0,
    from_flight=[Airport(flag=-1, airport="OTP")],
    to_flight  =[Airport(flag=-1, airport="MAD")],
)

fd2 = FlightData(
    date="2025-07-25",
    itin_data=ItineraryData(
        departure_airport="MAD",
        departure_date="2025-07-25",
        arrival_airport="OTP",
        flight_code="W4",
        flight_number="3172",
    ),
    max_stops=0,
    from_flight=[Airport(flag=-1, airport="MAD")],
    to_flight  =[Airport(flag=-1, airport="OTP")],
)

# assemble the booking request
req = BookingRequest(
    version         = 14,
    trip_flag       = 1,
    flights         = [fd1, fd2],
    passengers_flag = -1,
    seat_flag       = -1,

    # your exact 11-byte blob:
    info_trip_flag  = -1,
)



# serialize and Base64-encode
tfs = base64.b64encode(req.SerializeToString()).decode()
print(tfs)
