# -*- coding: utf-8 -*-
# Importing necessary libraries

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


from typing import List, Literal, Optional, Union, Dict
from selectolax.lexbor import LexborHTMLParser, LexborNode

from google_flights.filter import TFSData
from primp import Client
from datetime import datetime
import copy

from google_flights.decoder import DecodedResult, ResultDecoder, Itinerary, ItinerarySummary, Flight # decoder of the response by kftang
import re
import json
from itertools import chain, islice

DataSource = Literal['html', 'js']

# Function to fetch data from given parameters (filter, language, currency) - serverless
def fetch_search(params: dict):
    client = Client(impersonate="chrome_126", verify=False)
    res = client.get("https://www.google.com/travel/flights", params=params, cookies={
        'SOCS': 'CAISNQgjEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjUwNDIzLjA0X3AwGgJ1ayACGgYIgP6lwAY',
        'OTZ': '8053484_44_48_123900_44_436380',
        'NID': '8053484_44_48_123900_44_436380', # checked from the browser actual
    },
    timeout=15)

    print(res.url)

    if res.status_code == 200:
        return res
    else:
        print(RuntimeError(f"Failed to fetch data: {res.status_code} - {res.text}"))
        return None

# Function to fetch booking data from given parameters (filter, language, currency)
def fetch_booking(params: dict):
    client = Client(impersonate="chrome_126", verify=False)
    res = client.get("https://www.google.com/travel/flights/booking", params=params, cookies={
        'SOCS': 'CAISNQgjEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjUwNDIzLjA0X3AwGgJ1ayACGgYIgP6lwAY',
        'OTZ': '8053484_44_48_123900_44_436380',
        'NID': '8053484_44_48_123900_44_436380', # checked from the browser actual
    })

    if res.status_code == 200:
        return res
    else:
        print(RuntimeError(f"Failed to fetch data: {res.status_code} - {res.text}"))
        return None

# Function to fetch booking data from given parameters (filter, language, currency)
def fetch_booking(params: dict):
    client = Client(impersonate="chrome_126", verify=False)
    res = client.get("https://www.google.com/travel/flights/booking", params=params, cookies={
        'SOCS': 'CAISNQgjEitib3FfaWRlbnRpdHlmcm9udGVuZHVpc2VydmVyXzIwMjUwNDIzLjA0X3AwGgJ1ayACGgYIgP6lwAY',
        'OTZ': '8053484_44_48_123900_44_436380',
        'NID': '8053484_44_48_123900_44_436380', # checked from the browser actual
    })
    if res.status_code == 200:
        return res
    return None


# Function to parse the response and extract flight data from filter
def get_flights_from_filter(
        filter: TFSData,
        currency: Literal['EUR'] = "EUR",
        language: str = "en-GB",
        sort: Literal["top_flight", "price", "departure_time", "duration"] = "price",
        *,
        data_source: DataSource = "js",
        mode: Literal["common", "local"] = "common",
) -> Union[DecodedResult, None]: 
    data = filter.as_b64() # Encoding filter data to base64


    sort_parameter = {
        "top_flight": "EgQIARABIgA",
        "price": "EgQIAhABIgA",
        "departure_time": "EgQIAxABIgA",
        "duration": "EgQIBRABIgA",
    }
    
    params = {
        "tfs": data.decode("utf-8"), # Decoding the base64 data
        "hl": language, # For 24-hour format
        "tfu": sort_parameter.get(sort, "EgQIAhABIgA"), # Sorting parameter
        "curr": currency,
    } 


    if mode == 'common':
        try:
            res = fetch_search(params)
        except Exception as e:
            print(f"Error fetching data: {e}")
            res = local_playwright_fetch(params)
    else: # Local mode for testing 
        from google_flights.local_playwright import local_playwright_fetch
        res = local_playwright_fetch(params)

    try:
        return parse_response(res, data_source, dangerously_allow_looping_last_item=False)
    except RuntimeError as e:
        raise e 
    

def get_booking_url(
        flight_filter: TFSData,
        currency: str = "EUR",
        sort: Literal["top_flight", "price", "departure_time", "duration"] = "price",
        language: str = "en-GB"
) -> str: 

    """
    Function to get the booking URL for a flight based on the filter data (one-way/round-trip).
    """

    data = flight_filter.as_b64() # Encoding filter data to base64

    sort_parameter = {
        "top_flight": "EgQIARABIgA",
        "price": "EgQIAhABIgA",
        "departure_time": "EgQIAxABIgA",
        "duration": "EgQIBRABIgA",
    }
    
    params = {
        "tfs": data.decode("utf-8"), # Decoding the base64 data
        "hl": language, # For 24-hour format
        "tfu": sort_parameter.get(sort, "EgQIAhABIgA"), # Sorting parameter
        "curr": currency,
    } 

    if all(fd.itin_data for fd in flight_filter.flight_data):
        # If all flight data is present, fetch booking URL
        url = fetch_booking(params).url
        return url
    else:
        raise ValueError(
            "Itinerary data is missing for the flight filter."
        )


def get_round_trip_options(
        base_filter: TFSData,
        currency: str = "EUR",
        language: str = "en-GB",
        sort: Literal["top_flight", "price", "departure_time", "duration"] = "price",
        number_of_options: int = 3 # Number of options to return, default is 3
) -> List[Dict]:
    """
    Function to get round-trip flight options based on the base filter.

    Returns a list of dictionaries containing departure and return itinerary, and the booking URL.
    """

    if base_filter.trip != 1: # 1 for round-trip
        raise ValueError(
            "Base filter must be for a round-trip flight."
        )
    
    if len(base_filter.flight_data) != 2:
        raise ValueError(
            "Base filter must contain exactly two flight data entries for round-trip."
        )
    options = []
    outbound_res = get_flights_from_filter(base_filter, currency=currency, language=language, sort=sort)

    if outbound_res.other is None and outbound_res.best is None:
        raise ValueError(
            "No outbound flights found"
        )

    for outbound in islice(chain(outbound_res.best or outbound_res.other), number_of_options):
        # 1) Create a copy of the base filter for return flight and update it with itinerary
        return_filter = copy.deepcopy(base_filter)  # Create a copy of the base filter for return flight
        return_filter.flight_data[0].itin_data = []
        for leg in outbound.flights:
            return_filter.flight_data[0].itin_data.append({
                "departure_airport": leg.departure_airport,
                "arrival_airport":   leg.arrival_airport,
                "departure_date":    f"{leg.departure_date[0]}-"
                                      f"{leg.departure_date[1]:02d}-"
                                      f"{leg.departure_date[2]:02d}",
                "flight_code":       leg.airline,
                "flight_number":     leg.flight_number,
            })

        # 2) Run return-flight search
        return_results = get_flights_from_filter(
            return_filter, currency, language
        )
            
        try:
            return_flight = (return_results.best or return_results.other)[0]
        except TypeError:
            print("No return flights found for the outbound flight.")
            continue

        return_filter.flight_data[1].itin_data = []
        for leg in return_flight.flights:
            return_filter.flight_data[1].itin_data.append({
                "departure_airport": leg.departure_airport,
                "arrival_airport":   leg.arrival_airport,
                "departure_date":    f"{leg.departure_date[0]}-"
                                    f"{leg.departure_date[1]:02d}-"
                                    f"{leg.departure_date[2]:02d}",
                "flight_code":       leg.airline,
                "flight_number":     leg.flight_number,
            })

        try:
            url = get_booking_url(return_filter, currency=currency, language=language)
        except ValueError as e:
            print(f"ValueError: {e}")
            # something went wrong (missing data), skip
            continue
        
        # 3) Append the outbound and return flight options with URL
        options.append({
            "outbound": outbound,
            "return": return_flight,
            "url": url
        })

    
    price_series = outbound_res.price_series
    if price_series:
        return options, price_series
    return options, None


def get_one_way_options(
        base_filter: TFSData,
        currency: str = "EUR",
        language: str = "en-GB",
        sort: Literal["top_flight", "price", "departure_time", "duration"] = "price",
        number_of_options: int = 3  # Number of options to return, default is 3
) -> List[Dict]:
    """
    Function to get one-way flight options based on the base filter.

    Returns a list of dictionaries containing the itinerary and the booking URL.
    """

    if base_filter.trip != 2:  # 2 for one-way
        raise ValueError(
            "Base filter must be for a one-way flight."
        )

    if len(base_filter.flight_data) != 1:
        raise ValueError(
            "Base filter must contain exactly one flight data entry for one-way."
        )

    options = []

    one_way_res = get_flights_from_filter(base_filter, currency=currency, language=language, sort=sort)

    if one_way_res.other is None and one_way_res.best is None:
        raise ValueError(
            "No one-way flights found"
        )
    # Iterate through the best and other flight options, limited by number_of_options
    for outbound in islice(chain(one_way_res.best or one_way_res.other[:number_of_options]), number_of_options):
        # 1) Create a copy of the base filter and update it with itinerary
        flight_filter = copy.deepcopy(base_filter)
        flight_filter.flight_data[0].itin_data  = []
        for leg in outbound.flights:
            flight_filter.flight_data[0].itin_data.append({
                "departure_airport": leg.departure_airport,
                "arrival_airport":   leg.arrival_airport,
                "departure_date":    f"{leg.departure_date[0]}-"
                                      f"{leg.departure_date[1]:02d}-"
                                      f"{leg.departure_date[2]:02d}",
                "flight_code":       leg.airline,
                "flight_number":     leg.flight_number,
            })

        options.append({
            "flight": outbound,
            "url": get_booking_url(flight_filter, currency=currency, language=language, sort=sort)
        })

    price_series = one_way_res.price_series
    if price_series:
        return options, price_series
    return options, None


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
        return ResultDecoder.decode(data) or None
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

