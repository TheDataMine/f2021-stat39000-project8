import datetime
from typing import Union, Optional

from pydantic import BaseModel
from pydantic.validators import str_validator


def empty_to_none(v: str) -> Optional[str]:
    if v == '':
        return None
    return v


class EmptyStrToNone(str):
    @classmethod
    def __get_validators__(cls):
        yield str_validator
        yield empty_to_none
        

class Station(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float


class Observation(BaseModel):
    id: str
    station_id: int
    observation_time: datetime.datetime
    temperature_average: Union[int, None, EmptyStrToNone]
    temperature_high: Union[int, None, EmptyStrToNone]
    temperature_low: Union[int, None, EmptyStrToNone]
    humidity_average: Union[int, None, EmptyStrToNone]
    barometric_pressure: Union[float, None, EmptyStrToNone]
    wind_speed_average: Union[int, None, EmptyStrToNone]
    wind_speed_high: Union[int, None, EmptyStrToNone]
    wind_direction_high: Union[float, None, EmptyStrToNone]
    wind_direction_average: Union[float, None, EmptyStrToNone]
    radiation_average: Union[int, None, EmptyStrToNone]
    radiation_high: Union[int, None, EmptyStrToNone]
    rain: Union[int, None, EmptyStrToNone]
    rain_last_hour: Union[int, None, EmptyStrToNone]
    temperature_soil_2: Union[int, None, EmptyStrToNone]
    temperature_soil_5: Union[int, None, EmptyStrToNone]
    temperature_soil_10: Union[int, None, EmptyStrToNone]
    temperature_soil_15: Union[int, None, EmptyStrToNone]
    moisture_soil_2: Union[int, None, EmptyStrToNone]
    moisture_soil_5: Union[int, None, EmptyStrToNone]
    moisture_soil_10: Union[int, None, EmptyStrToNone]
    moisture_soil_15: Union[int, None, EmptyStrToNone]


