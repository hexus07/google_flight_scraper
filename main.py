# -*- coding: utf-8 -*-
# Imorting necessary libraries
from typing import List, Literal, Optional, Union
from selectolax.lexbor import LexborHTMLParser, LexborNode

from dataclass import Flight, Result
from filter import TFSData, create_filter
# from local_playwright import local_playwright_fetch
from primp import Client

from hashlib import sha256
from datetime import datetime

from flights_pb_implem import FlightData, Passengers

from decoder import DecodedResult, ResultDecoder # decodoer of the response by kftang
import re
import json
DataSource = Literal['html', 'js']

# Function to fetch data from a URL with given parameters - serverless
def fetch(params: dict):
    client = Client(impersonate="chrome_126", verify=False)
    res = client.get("https://www.google.com/travel/flights", params=params, cookies={
        'SOCS': 'CAISNQgjEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjUwNDIzLjA0X3AwGgJ1ayACGgYIgP6lwAY',
        'OTZ': '8053484_44_48_123900_44_436380',
        'NID': '8053484_44_48_123900_44_436380', # checked from the browser actual
    })
    assert res.status_code == 200, f"{res.status_code} Result: {res.text_markdown}"
    return res


# Function to parse the response and extract flight data from filter
def get_flights_from_filter(
        filter: TFSData,
        currency: str = "EUR",
        *,
        data_source: DataSource = "js",
        mode: Literal["common", "local"] = "common",
) -> Union[Result, DecodedResult, None]: 
    data = filter.as_b64() # Encoding filter data to base64

    params = {
        "tfs": data.decode("utf-8"), # Decoding the base64 data
        "hl": "en-GB", # For 24-hour format
        "tfu": "EgQIABABIgA",
        "curr": currency,
    } 

    if mode == 'common':
        res = fetch(params)

    try:
        return parse_response(res, data_source, dangerously_allow_looping_last_item=False)
    except RuntimeError as e:
        raise e
    

def parse_response(
    r,
    data_source: DataSource,
    *,
    
    dangerously_allow_looping_last_item: bool = False
) -> Union[Result, DecodedResult, None]:
    class _blank:
        def text(self, *_, **__):
            return ""

        def iter(self):
            return []

    blank = _blank()

    def safe(n: Optional[LexborNode]):
        return n or blank

    parser = LexborHTMLParser(r.text)

    if data_source == "js":
        script = parser.css_first(r'script.ds\:1').text()

        match = re.search(r'^.*?\{.*?data:(\[.*\]).*\}', script)
        assert match, "No data found in script tag"
        data = json.loads(match.group(1))
        return ResultDecoder.decode(data) if data is not None else None
    else:   # # HTML parsing
        flights = []

        for i, fl in enumerate(parser.css('div[jsname="IWWDBc"], div[jsname="YdtKid"]')):
            print
            is_best_flight = i == 0

            for item in fl.css("ul.Rk10dc li")[
                : (None if dangerously_allow_looping_last_item or i == 0 else -1)
            ]:
                # Flight name
                name = safe(item.css_first("div.sSHqwe.tPgKwe.ogfYpf span")).text(
                    strip=True
                )

                # Get departure & arrival time
                dp_ar_node = item.css("span.mv1WYe div")
                try:
                    departure_time = dp_ar_node[0].text(strip=True)
                    arrival_time = dp_ar_node[1].text(strip=True)
                except IndexError:
                    # sometimes this is not present
                    departure_time = ""
                    arrival_time = ""

                # Get arrival time ahead
                time_ahead = safe(item.css_first("span.bOzv6")).text()

                # Get duration
                duration = safe(item.css_first("li div.Ak5kof div")).text()

                # Get flight stops
                stops = safe(item.css_first(".BbR8Ec .ogfYpf")).text()

                # Get delay
                delay = safe(item.css_first(".GsCCve")).text() or None

                # Get prices
                price = safe(item.css_first(".YMlIz.FpEdX")).text() or "0"
                
                # Stops formatting
                try:
                    stops_fmt = 0 if stops == "Nonstop" else int(stops.split(" ", 1)[0])
                except ValueError:
                    stops_fmt = "Unknown"

                flights.append(
                    {
                        "is_best": is_best_flight,
                        "name": name,
                        "departure": " ".join(departure_time.split()),
                        "arrival": " ".join(arrival_time.split()),
                        "arrival_time_ahead": time_ahead,
                        "duration": duration,
                        "stops": stops_fmt,
                        "delay": delay,
                        "price": price.replace(",", ""),
                    }
                )

        current_price = safe(parser.css_first("span.gOatQ")).text()
        if not flights:
            raise RuntimeError("No flights found:\n{}".format(r.text_markdown))

        return Result(current_price=current_price, flights=[Flight(**fl) for fl in flights])  # type: ignore




def __main__():

    # TESTING PURPOSES ONLY
    filter = create_filter(
    flight_data=[
        # Include more if it's not a one-way trip
        FlightData(
            date="2025-07-20",  # Date of departure
            from_airport=["VNO"],  # Departure (airport)
            to_airport=["BCN"],  # Arrival (airport)
        ),
    ],
    trip="one-way",  # Trip type
    passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),  # Passengers
    seat="economy",  # Seat type
    max_stops=1,  # Maximum number of stops
    
    )
    print(filter.as_b64().decode("utf-8"))
    flight_data = get_flights_from_filter(filter, data_source='js', mode="common")
    for flight in flight_data.best:
        print(flight)
        print("\n")



if __name__ == "__main__":
    __main__()