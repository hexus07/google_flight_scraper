import abc
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, List, Generic, Optional, Sequence, TypeVar, Union, Tuple, Dict
from typing_extensions import TypeAlias, override
from enum import Enum
from google_flights.flights_pb_implem import ItinerarySummary

DecodePath: TypeAlias = List[int]
NLBaseType: TypeAlias = Union[int, str, None, Sequence['NLBaseType']]



# Map feature array index to a human-readable key
FEATURE_INDEX_MAP: Dict[int, str] = {
    1:  "in_seat_power_usb",
    3:  "in_seat_power",
    5:  "usb_outlet",
    9:  "on_demand_video",
   10: "streaming_media",
   11: "wifi",
}

AVAIL_MAP: Dict[Optional[int], str] = {
    None: "not_available",
    1:    "included",
    2:    "for_free",
    3:    "for_fee",
}

SEAT_TYPE_MAP: Dict[Optional[int], str] = {
    None:      "unknown",
    1:         "average",
    2:         "below_average",
    3:         "above_average",
    4:         "extra_reclining",
    5:         "lie_flat",
    6:         "indiv_suite",
}


# N(ested)L(ist)Data, this class allows indexing using a path, and as an int to make
# traversal easier within the nested list data
@dataclass
class NLData(Sequence[NLBaseType]):
    data: List[NLBaseType]

    def __getitem__(self, decode_path: Union[int, DecodePath]) -> NLBaseType:
        if isinstance(decode_path, int):
            return self.data[decode_path]
        it = self.data
        #print(f"Decoding path: {it}")
        for index in decode_path:
            assert isinstance(it, list), f'Found non list type while trying to decode {decode_path}'
            assert index < len(it), f'Trying to traverse to index out of range when decoding {decode_path}'
            it = it[index]
        return it
    @override
    def __len__(self) -> int:
        return len(self.data)

# DecoderKey is used to specify the path to a field from a decoder class
V = TypeVar('V')
@dataclass
class DecoderKey(Generic[V]):
    decode_path: DecodePath
    decoder: Optional[Callable[[NLData], V]] = None

    def decode(self, root: NLData) -> Union[NLBaseType, V]:        
        try:
            data = root[self.decode_path]
        except AssertionError as e:
            print(f"Error decoding path {self.decode_path}: {e} - is not present in the data")
            return None
        
        if isinstance(data, list) and self.decoder:
            assert self.decoder is not None, f'decoder should be provided in order to further decode NLData instances'
            return self.decoder(NLData(data))
        return data

# Decoder is used to aggregate all fields and their paths
class Decoder(abc.ABC):
    @classmethod
    def decode_el(cls, el: NLData) -> Mapping[str, Any]:
        decoded: Mapping[str, Any] = {}
        for field_name, key_decoder in vars(cls).items():
            if isinstance(key_decoder, DecoderKey):
                value = key_decoder.decode(el)
                decoded[field_name.lower()] = value
        return decoded

    @classmethod
    def decode(cls, root: Union[list, NLData]) -> ...:
        ...


# Type Aliases
AirlineCode: TypeAlias = str
AirlineName: TypeAlias = str
AirportCode: TypeAlias = str
AirportName: TypeAlias = str
ProtobufStr: TypeAlias = str
Minute: TypeAlias = int

@dataclass
class Codeshare:
    airline_code: AirlineCode
    flight_number: int
    airline_name: AirlineName

@dataclass
class Flight:
    airline: AirlineCode
    airline_name: AirlineName
    flight_number: str
    operator: str
    codeshares: List[Codeshare]
    aircraft: str
    departure_airport: AirportCode
    departure_airport_name: AirportName
    arrival_airport: AirportCode
    arrival_airport_name: AirportName
    emissions: int
    departure_date: Tuple[int, int, int]
    arrival_date: Tuple[int, int, int]
    departure_time: Tuple[int, int]
    arrival_time: Tuple[int, int]
    travel_time: int
    seat_pitch_short: str
    seat_type: Optional[str]
    features: Dict[str, str]
    
    # seat_pitch_long: str

@dataclass
class Layover:
    minutes: Minute
    departure_airport: AirportCode
    departure_airport_name: AirportName
    departure_airport_city: AirportName
    arrival_airport: AirportCode
    arrival_airport_name: AirportName
    arrival_airport_city: AirportName

@dataclass
class Itinerary:
    airline_code: AirlineCode
    airline_names: List[AirlineName]
    flights: List[Flight]
    layovers: List[Layover]
    travel_time: int
    departure_airport: AirportCode
    arrival_airport: AirportCode
    departure_date: Tuple[int, int, int]
    arrival_date: Tuple[int, int, int]
    departure_time: Tuple[int, int]
    arrival_time: Tuple[int, int]
    itinerary_summary: ItinerarySummary

@dataclass
class DecodedResult:
    # raw unparsed data
    raw: list

    best: List[Itinerary]
    other: List[Itinerary]

    # airport_details: Any
    # unknown_1: Any

class CodeshareDecoder(Decoder):
    AIRLINE_CODE: DecoderKey[AirlineCode] = DecoderKey([0])
    FLIGHT_NUMBER: DecoderKey[str] = DecoderKey([1])
    AIRLINE_NAME: DecoderKey[List[AirlineName]] = DecoderKey([3])

    @classmethod
    @override
    def decode(cls, root: Union[list, NLData]) -> List[Codeshare]:
        return [Codeshare(**cls.decode_el(NLData(el))) for el in root]

class FlightDecoder(Decoder):
    OPERATOR: DecoderKey[AirlineName] = DecoderKey([2])
    DEPARTURE_AIRPORT: DecoderKey[AirportCode] = DecoderKey([3])
    DEPARTURE_AIRPORT_NAME: DecoderKey[AirportName] = DecoderKey([4])
    ARRIVAL_AIRPORT: DecoderKey[AirportCode] = DecoderKey([6])
    ARRIVAL_AIRPORT_NAME: DecoderKey[AirportName] = DecoderKey([5])
    EMISSIONS: DecoderKey[int] = DecoderKey([31])
    DEPARTURE_TIME: DecoderKey[Tuple[int, int]] = DecoderKey([8])
    ARRIVAL_TIME: DecoderKey[Tuple[int, int]] = DecoderKey([10])
    TRAVEL_TIME: DecoderKey[int] = DecoderKey([11])
    SEAT_PITCH_SHORT: DecoderKey[str] = DecoderKey([14])
    AIRCRAFT: DecoderKey[str] = DecoderKey([17])
    DEPARTURE_DATE: DecoderKey[Tuple[int, int, int]] = DecoderKey([20])
    ARRIVAL_DATE: DecoderKey[Tuple[int, int, int]] = DecoderKey([21])
    AIRLINE: DecoderKey[AirlineCode] = DecoderKey([22, 0])
    AIRLINE_NAME: DecoderKey[AirlineName] = DecoderKey([22, 3])
    FLIGHT_NUMBER: DecoderKey[str] = DecoderKey([22, 1])
    
    CODESHARES: DecoderKey[List[Codeshare]] = DecoderKey([15], CodeshareDecoder.decode)
    SEAT_TYPE: DecoderKey[str] = DecoderKey(
        [],
        lambda nl: SEAT_TYPE_MAP.get(nl.data[13] if isinstance(nl.data, list) and len(nl.data) > 13 else None, SEAT_TYPE_MAP[None])
    )
    
    FEATURES: DecoderKey[Dict[str, str]] = DecoderKey(
        [12],
        lambda nl: {
            FEATURE_INDEX_MAP[idx]: AVAIL_MAP.get(val)
            for idx, val in enumerate(nl.data)
            if idx in FEATURE_INDEX_MAP
        }
    )



    @classmethod
    @override
    def decode(cls, root: Union[list, NLData]) -> List[Flight]:
        return [Flight(**cls.decode_el(NLData(el))) for el in root]

class LayoverDecoder(Decoder):
    MINUTES: DecoderKey[int] = DecoderKey([0])
    DEPARTURE_AIRPORT: DecoderKey[AirportCode] = DecoderKey([1])
    DEPARTURE_AIRPORT_NAME: DecoderKey[AirportName] = DecoderKey([4])
    DEPARTURE_AIRPORT_CITY: DecoderKey[AirportName] = DecoderKey([5])
    ARRIVAL_AIRPORT: DecoderKey[AirportCode] = DecoderKey([2])
    ARRIVAL_AIRPORT_NAME: DecoderKey[AirportName] = DecoderKey([6])
    ARRIVAL_AIRPORT_CITY: DecoderKey[AirportName] = DecoderKey([7])

    @classmethod
    @override
    def decode(cls, root: Union[list, NLData]) -> List[Layover]:
        return [Layover(**cls.decode_el(NLData(el))) for el in root]

class ItineraryDecoder(Decoder):
    AIRLINE_CODE: DecoderKey[AirlineCode] = DecoderKey([0, 0])
    AIRLINE_NAMES: DecoderKey[List[AirlineName]] = DecoderKey([0, 1])
    FLIGHTS: DecoderKey[List[Flight]] = DecoderKey([0, 2], FlightDecoder.decode)
    DEPARTURE_AIRPORT: DecoderKey[AirportCode] = DecoderKey([0, 3])
    DEPARTURE_DATE: DecoderKey[Tuple[int, int, int]] = DecoderKey([0, 4])
    DEPARTURE_TIME: DecoderKey[Tuple[int, int]] = DecoderKey([0, 5])
    ARRIVAL_AIRPORT: DecoderKey[AirportCode] = DecoderKey([0, 6])
    ARRIVAL_DATE: DecoderKey[Tuple[int, int, int]] = DecoderKey([0, 7])
    ARRIVAL_TIME: DecoderKey[Tuple[int, int]] = DecoderKey([0, 8])
    TRAVEL_TIME: DecoderKey[int] = DecoderKey([0, 9])
    # UNKNOWN: DecoderKey[int] = DecoderKey([0, 10])
    LAYOVERS: DecoderKey[List[Layover]] = DecoderKey([0, 13], LayoverDecoder.decode)
    # first field of protobuf is the same as [0, 4] on the root? seems like 0,4 is for tracking
    # contains a summary of the flight numbers and the price (as a fixed point sint)
    ITINERARY_SUMMARY: DecoderKey[ItinerarySummary] = DecoderKey([1], lambda data: ItinerarySummary.from_b64(data[1]))
    # contains Flight(s), the price, and a few more
    # FLIGHTS_PROTOBUF: DecoderKey[ProtobufStr] = DecoderKey([8])
    # some struct containing emissions info
    # EMISSIONS: DecoderKey[Emissions] = DecoderKey([22])

    @classmethod
    @override
    def decode(cls, root: Union[list, NLData]) -> List[Itinerary]:
        return [Itinerary(**cls.decode_el(NLData(el))) for el in root]


class ResultDecoder(Decoder):
    BEST: DecoderKey[Optional[List[Itinerary]]] = DecoderKey(
        [2, 0],
        ItineraryDecoder.decode)

    OTHER: DecoderKey[List[Itinerary]] = DecoderKey([3, 0], ItineraryDecoder.decode)

    @classmethod
    @override
    def decode(cls, root: Union[list, NLData]) -> DecodedResult:
        assert isinstance(root, list), 'Root data must be list type'

        # Decode elements and handle missing or null fields
        decoded_data = cls.decode_el(NLData(root))
        return DecodedResult(
            best=decoded_data.get("best", []),  # Default to an empty list if BEST is missing
            other=decoded_data.get("other", []),  # Default to an empty list if OTHER is missing
            raw=root
        )
