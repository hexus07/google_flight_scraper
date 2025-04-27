import re 
import requests
from typing import List, Optional, Union


def search_airline(name: str) -> Union[List[str], None]:
    """
    Search for airline by name.
    """

    url = (f"https://www.iata.org/PublicationDetails/Search/?currentBlock=314383&currentPage=12572&airline.search={name}")


    headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru;q=0.6,lt;q=0.5,pl;q=0.4",
    "referer": "https://www.iata.org/en/publications/directories/code-search/?airline.search=Ryanair",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers)

    return parse_result(response)
    

def search_airport(name: str) -> Union[List[str], None]:
    """
    Search for airport by name.
    """

    url = (f"https://www.iata.org/PublicationDetails/Search/?currentBlock=314384&currentPage=12572&airport.search={name}")


    headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru;q=0.6,lt;q=0.5,pl;q=0.4",
    "referer": "https://www.iata.org/en/publications/directories/code-search/?airline.search=Ryanair",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers)

    return parse_result(response)

def parse_result(
    data_source: str,
) -> Union[List[str], None]:
    """
    Parse the response from the server.
    """
    

    pattern = r'<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>'

    # Use re.findall to extract all matching rows
    matches = []
    try:
        found_matches = re.findall(pattern, data_source.text)[1:]
        if found_matches:
            matches = [match[2] for match in found_matches]
            return matches
    except Exception as e:
        print (f"Error parsing response: {e}")
    
    return None
