# Google Flights Scraper ✈️
<div align="center">
  
Fast flight data scraper from Google Flights which fetches and decodes flight information based on user's filters. Based on a Base64-encoded Protobuf URL string.

 [Issues](https://github.com/hexus07/google_flight_scraper/issues) • [PyPi](https://pypi.org/project/google-flights/)

</div>

## Features
- 🏷️ **Filter Creation**: Define custom filters for flights ( departure/arrival airports, airlines, dates, trip type, passengers, seat type, and maximum stops)
- ⚙️ **Data Fetching**: Fetch flight data from Google Flights for one-way or round-trip options.
- 🔓 **Decoding**: Decode the fetched flight data into structured objects for easy processing.
- 🏷️ **Creating Booking URL**: Booking URL for each itinerary which can be used directly. 


## Installation

```bash
  pip install google-flights
```

or if you want to run it locally (with Playwright):

```bash
  pip install google-flights[local]
```
   
## Usage/Examples

1. Create a Filter
* Define the search criteria for flights using the create_filter (for ?tfs=) to perform a request. Then, add flight_data, trip, seat, and passengers to use the API directly.

```python
from google_flights import create_filter, Passengers, FlightData, search_airline, search_airport

flight_filter = create_filter(
    flight_data=[
        FlightData(
            airlines=['FR'],  # Airline codes - "FR" and "RK" - can be passed as list ["FR","RK"]
            date="2025-07-20",      # Date of departure
            from_airport=["KUN"]  # Departure airport ["KUN"]
            to_airport=["MAD"],  # Arrival airports
        ),
    ],
    trip="one-way",  # Trip type
    passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
    seat="economy",  # Seat type
    max_stops=1,     # Maximum number of stops
)
```

2. Fetch Flight Data

* Fetch flight data using the get_one_way_options
```python
from google_flights import get_one_way_options

flight_data = get_one_way_options(flight_filter, currency="UAH", language="uk", number_of_options=2)
```

3. Result 
- The following parameters would be included in the API result:

✈️ Airline (code & name)

🔢 Flight number

🛫 Departure airport (code & name) & departure time

🛬 Arrival airport (code & name) & arrival time

📅 Departure date

⏱️ Travel duration

🛡️ Aircraft type

💺 Seat class (including seat pitch)

🌱 CO₂ emissions (grams)

💶 Price (EUR or other currency)

🔄 Layovers (direct or stops)

✨ Features (Wi‑Fi, in‑seat power, video, media streaming, etc.)

✈️ Booking URL

## Contributing

I'll work with this project more in future, as I have plans for it. So contributions are always welcome!


## Roadmap

- Additional bug checking

- Add more possibilities, as finding the shortest and economic path


## 💡Idea
It all started with a simple thought: “When is the best time to purchase a flight ticket?” and I found this website:
> https://www.airhint.com/about

It actually offers pretty decent information, even predictions on whether to wait or buy now.  However, their training data was already outdated, resulting in false predictions. So, I decided to build my own version. What did I need? 

A scraper!


Since Google doesn't provide a public API, we, simple people who don't want to pay - are creating our own scraper.

The idea is straightforward: build a scraper that returns all results based on your filters.

Initially, I tried Playwright. It worked (and remains in the project as an alternative). We need smth different, which is faster and stable. 

Then I examined the Google Flights URL: 
https://www.google.com/travel/flights?tfs=GisSCjIwMjUtMDctMjUoATICQlQyAkZSagUSA01BRHIFEgNLVU5yBRIDVk5PQgEBSAGYAQI%3D

Notice the tfs parameter:```tfs=GisSCjIwMjUtMDctMjUoATICQlQyAkZSagUSA01BRHIFEgNLVU5yBRIDVk5PQgEBSAGYAQI%3D```, which looks like base64. We need to decode it! How?  

But raw decoding yields too much noise. Which protocol does Google use?  -  Correctly Protobuf! 
And what we can see here: 
![Screenshot 2025-04-28 001211](https://github.com/user-attachments/assets/4790f16c-4e5a-49f5-8e4e-ddb1c3896ee8)

That's our data! Half of the object is done. Next we need to parse, and get results.

Using data embedded in the response's script tag (```<script class="ds:1">```), I'm able to get much more data than what is parsed from the HTML. 
There are a few challenges: some fields require hardcoding. For example, features (in-seat power, etc.) are coded as: ```[null, null, null, null, null, null, null, null, null, null, null, 3]```

You can see the features array is [… , 3] with that 3 sitting in slot 11 (zero-based).

We know slot 11 maps to Wi-Fi, and the code 3 means “for a fee” (whereas 2 would be "for free", and null means “not available”). With the same logic every else, which you need to find by yourself.

However, this approach is much faster than Playwright and provides richer data than pure HTML scraping!

## 🚀 About Me
I'm a Python developer with a deep passion for Data Science and ML Engineering. 

I’m constantly exploring new techniques and tools to enhance my skills and dive into solving real-world problems through data-driven insights. Whether it's building models or optimizing data pipelines or analyzing data 


## 🔗 Links
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/daniil-chuhai/)

[![github](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=fff&style=for-the-badge)](https://github.com/hexus07)

