# -*- coding: utf-8 -*-
# Imorting necessary libraries
from typing import List, Literal, Optional, Union
from selectolax.lexbor import LexborHTMLParser, LexborNode

from filter import TFSData
from local_playwright import local_playwright_fetch

from primp import Client
from datetime import datetime

from decoder import DecodedResult, ResultDecoder, Itinerary, ItinerarySummary, Flight # decodoer of the response by kftang
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
    print(res.url)  # Print the full URL
    
    assert res.status_code == 200, f"{res.status_code} Result: {res.text_markdown}"
    return res


# Function to parse the response and extract flight data from filter
def get_flights_from_filter(
        filter: TFSData,
        currency: str = "EUR",
        *,
        data_source: DataSource = "js",
        mode: Literal["common", "local"] = "common",
) -> Union[DecodedResult, None]: 
    data = filter.as_b64() # Encoding filter data to base64

    params = {
        "tfs": data.decode("utf-8"), # Decoding the base64 data
        "hl": "en-GB", # For 24-hour format
        "tfu": "EgQIABABIgA",
        "curr": currency,
    } 

    if mode == 'common':
        try:
            res = fetch(params)
        except Exception as e:
            print(f"Error fetching data: {e}")
            res = local_playwright_fetch(params)
    else: # Local mode for testing 
        res = local_playwright_fetch(params)

    try:
        return parse_response(res, data_source, dangerously_allow_looping_last_item=False)
    except RuntimeError as e:
        raise e
    

def parse_response(
    r,
    data_source: DataSource,
    *,
    
    dangerously_allow_looping_last_item: bool = False
) -> Union[DecodedResult, None]:
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
    else:   # HTML parsing - using local_playwright_fetch
        flights = []
        
        parser = LexborHTMLParser(r.text)
        fl = parser.css_first("div[jsname='IWWDBc']")

        if fl:
            is_best_flight = True
            departure_airport = safe(fl.css("ul.Rk10dc li.pIav2d .dPzsIb.AdWm1c   span")[6]).text()[1:-1]
            departure_airport_name = safe(fl.css_first("ul.Rk10dc li.pIav2d .ZHa2lc.tdMWuf  ")).text().split("\xa0")[0]
            arrival_airport = safe(fl.css("ul.Rk10dc li.pIav2d .SWFQlc span")[-1]).text()[1:-1]
            arrival_airport_name = safe(fl.css_first("ul.Rk10dc li.pIav2d .FY5t7d.tdMWuf")).text().split("\xa0")[0]
            for item in fl.css("ul.Rk10dc li.pIav2d"):

                # Flight name
                airline_name = safe(item.css_first("span.Xsgmwe")).text()

                # Get departure and arrival times
                departure_arrival = safe(item.css("div[jsname='bN97Pc']"))
                year = 2025  

                dt = datetime.strptime(f"{departure_arrival[0].text()} {year}", "%H:%M on %a %d %b %Y")
                departure_date = [dt.year, dt.month, dt.day]
                departure_time = [dt.hour, dt.minute]

                ar = datetime.strptime(f"{departure_arrival[1].text()} {year}", "%H:%M on %a %d %b %Y")
                arrival_date = [ar.year, ar.month, ar.day]
                arrival_time = [ar.hour, ar.minute]
            
                
                # Get duration
                duration = safe(item.css_first("div.CQYfx")).text().split(": ")
                travel_time = convert_travel_time_to_minutes(duration[1])

                # Get flight stops
                stops = safe(item.css_first(".BbR8Ec .ogfYpf")).text()

                # Get prices
                price = int(safe(item.css_first(".YMlIz.FpEdX")).text()[1:]) or "0"

                # Get plane
                plane = safe(item.css(".Xsgmwe")[3]).text()
    
                # Get emissions
                emissions = int(safe(item.css_first("li.WtSsrd span.gI4d6d")).text()[20:-7])*1000

                # Get flight number
                flight_number = safe(item.css_first(".Xsgmwe.QS0io")).text().replace('\xa0', '')
                airline_code, flight_num = flight_number[:2], flight_number[2:]

                # Get class
                #flight_class = safe(item.css_first("span[jsname='Pvlywd']")).text()

                # Get operator
                operator = safe(item.css_first(".kSwLQc.sSHqwe")).text().split(" ")[4:]
                operator = " ".join(operator) if operator else None

                seat_pitch_short = safe(item.css_first("li.WtSsrd")).text()[-6:-1]

                try:
                    stops_fmt = 0 if stops == "Nonstop" else int(stops.split(" ", 1)[0])
                except ValueError:
                    stops_fmt = "Unknown"

                flights.append(
                    Itinerary(
                        airline_code=airline_code,
                        airline_names=[airline_name],
                        flights=[
                            Flight(
                                airline=airline_code,
                                airline_name=airline_name,
                                flight_number=flight_num,
                                operator=operator,
                                codeshares=None,
                                aircraft=plane,
                                departure_airport=departure_airport,
                                departure_airport_name=departure_airport_name,
                                arrival_airport=arrival_airport,
                                arrival_airport_name=arrival_airport_name,
                                departure_date=departure_date,
                                arrival_date=arrival_date,
                                departure_time=departure_time,
                                arrival_time=arrival_time,
                                travel_time=travel_time,
                                seat_pitch_short=seat_pitch_short,
                                emissions=emissions,
                                seat_type=None,
                                features={},
                            )
                        ],
                        layovers=None,
                        travel_time=travel_time,
                        departure_airport=departure_airport,
                        arrival_airport=arrival_airport,
                        departure_date=departure_date,
                        arrival_date=arrival_date,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        itinerary_summary=ItinerarySummary(
                            flights=flight_number,
                            price=price,
                            currency='EUR'
                        )
                    )
                )

        current_price = safe(parser.css_first("span.gOatQ")).text()
        if not flights:
            raise RuntimeError("No flights found:\n{}".format(r.text_markdown))

        return DecodedResult(raw=[] ,best=flights, other=[])  # type: ignore


def convert_travel_time_to_minutes(text: str) -> int:
    text = text.lower().replace('hrs', 'hr').replace('min', '').strip()
    minutes = 0

    if 'hr' in text:
        parts = text.split(' hr ')
        hours, text = parts
        minutes += int(hours) * 60

    minutes += int(text) 

    return minutes

