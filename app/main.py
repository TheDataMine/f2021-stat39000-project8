import io
import pandas as pd
import aiosql
import sqlite3
import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.schemas import Observation, Station

from .database import queries, database_path
from .exceptions import BadQueryParameterException, NotFoundException, responses
from .exception_handlers import bad_query_parameter_exception_handler, not_found_exception_handler

app = FastAPI()
templates = Jinja2Templates(directory='templates/')

# Add exception handlers to exceptions
app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(BadQueryParameterException, bad_query_parameter_exception_handler)


@app.get("/")
async def root():
    """
    Returns a simple message, "Hello World!"

    Returns:
        dict: The response JSON.
    """
    return {"message": "Hello World"}


@app.get(
    "/weather", 
    response_model=list[Observation], 
    responses=responses,
    summary="Get and filter weather observations",
    response_description="A list of (possibly filtered) weather observations"
)
async def weather(starting_after: str = None, created: datetime.date = None, limit: int = 10):
    """
    # Get and filter weather observations.
    
    ## limit
        
    The maximum number of observations to return.  
    If not provided, the first 10 observations will be returned.  
    Maximum of 100 observations, minimum of 1 observation.
    This is the _last_ filter applied when mixed with `created` and `starting_after`.
    
    ### Example(s)
    
    - `http://localhost:8000/weather`: Return the first 10 observations.  
    - `http://localhost:8000/weather?limit=5`: Return the first 5 observations.  
    - `http://localhost:8000/weather?limit=100`: Return the _maximum_ of 100 observations.  
    - `http://localhost:8000/weather?limit=101`: Return a 422 bad parameter error. Limit must _not_ be > 100.  
        
    ## created
    
    Filter observations by date, after which we will return `limit` observations.  
    If not provided, the first `limit` observations will be returned.  
    Dates must be in the format YYYY-MM-DD.  
    Maximum of 100 observations.  
    This is the _first_ filter applied when mixed with `starting_after` and `limit`.  
    
    ### Example(s)
    
    - `http://localhost:8000/weather?created=2019-07-11`: Return the first 10 observations that were created on 2019-07-11.  
    - `http://localhost:8000/weather?created=2019-07-11&limit=20`: Return the first 20 observations that were created on 2019-07-11.  
    - `http://localhost:8000/weather?created=2019-07-11&limit=101`: Return a 422 bad parameter error. Limit must _not_ be > 100.  
    - `http://localhost:8000/weather?created=2021-07-31`: Return a 404 error. There are no observations created on 2021-07-31.  
    - `http://localhost:8000/weather?created=2019-07-11&starting_after=obs_1NqrK3mraUzaj2j7hg6VcB23RjJ&limit=20`:  
        - First filters out all observations that did _not_ happen on 2019-07-11.  
        - Then, skips over the observations before the observation with id `obs_1NqrK3mraUzaj2j7hg6VcB23RjJ`.  
        - Return the first 20 observations from that point.  
    
    ## starting_after
    
    The ID of the observation, after which we will return `limit` observations.  
    If not provided, the first `limit` observations will be returned.  
    This filter is always applied _after_ `created` but _before_ `limit`.  
    
    ### Example(s)
    
    - `http://localhost:8000/weather?starting_after=obs_1NqnftCklLZHBCHyykvcuc8QvE9`:  
        - Return the first 10 observations starting immediately _after_ the observation with id `obs_1NqnftCklLZHBCHyykvcuc8QvE9`.
    - `http://localhost:8000/weather?starting_after=obs_1NqnftCklLZHBCHyykvcuc8QvE9?limit=22`:
        - Return the first 22 observations starting immediately _after_ the observation with id `obs_1NqnftCklLZHBCHyykvcuc8QvE9`.
    - `http://localhost:8000/weather?created=2019-07-11&starting_after=obs_1NqrK3mraUzaj2j7hg6VcB23RjJ&limit=20`:  
        - First filters out all observations that did _not_ happen on 2019-07-11.  
        - Then, skips over the observations before the observation with id `obs_1NqrK3mraUzaj2j7hg6VcB23RjJ`.  
        - Return the first 20 observations from that point.  

    \f
    Args:
        starting_after (str, optional): [description]. Defaults to None.
        created (datetime.date, optional): [description]. Defaults to None.
        limit (int, optional): [description]. Defaults to 10.

    Raises:
        BadQueryParameterException: [description]
        NotFoundException: [description]

    Returns:
        [type]: [description]
    """
    
    # if the limit requested is > 100, or < 1, raise a BadQueryParameterException
    if limit > 100 or limit < 1:
        raise BadQueryParameterException()
    
    conn = sqlite3.connect(database_path)
    
    # if both query parameters are provided, filter first by `created`, and then by `starting_after`. Limit output to `limit`.
    if starting_after and created:
        results = queries.get_observations_created_at_starting_after(conn, limit=limit, created_at=created, id=starting_after)
    
    # otherwise, if `starting_after` is the only parameter provided, filter by `starting_after`. Limit output to `limit`.
    elif starting_after:
        results = queries.get_observations_starting_after(conn, limit=limit, id=starting_after)
        
    # otherwise, if `created` is the only parameter provided, filter by observations occuring on the provided date. Limit output to `limit`.
    elif created:
        results = queries.get_observations_created_at(conn, limit=limit, created_at=created)
        
    # otherwise, just return the first `limit` observations
    else:
        results = queries.get_observations(conn, limit=limit)
        
    conn.close()
        
    if not results:
        raise NotFoundException()
    
    observations = []
    for observation in results:
        observations.append(Observation(**{key: observation[i] for i, key in enumerate(Observation.__fields__.keys())}))
    
    return observations


@app.get(
    "/stations", 
    response_model=list[Station],
    responses=responses,
    summary="Get a list of all of the stations",
    response_description="A list of the stations"
)
async def get_stations():
    """
    Return a list of all of the stations.
    """
    conn = sqlite3.connect(database_path)
    results = queries.get_stations(conn)
    conn.close()
    stations = []
    for station in results:
        stations.append(Station(**{key: station[i] for i, key in enumerate(Station.__fields__.keys())}))
        
    return stations


@app.get(
    "/stations/{id}", 
    response_model=Station, 
    responses=responses,
    summary="Get the station with the given id",
    response_description="The station with the given id"
)
async def get_station(id: int):
    """
    Return the station with the given id.
    \f
    Args:
        id (int): The id of the station to return.

    Raises:
        NotFoundException: If the station with the given id does not exist.
    """
    conn = sqlite3.connect(database_path)
    station = queries.get_station(conn, id=id)
    conn.close()
    if station:
        station = Station(**{key: station[i] for i, key in enumerate(Station.__fields__.keys())})
        return station
    else:
        raise NotFoundException()
    

@app.get(
    "/stations/{id}/weather", 
    response_model=list[Observation], 
    responses=responses,
    summary="Get and filter weather observations for the specified station",
    response_description="A list of (possibly filtered) weather observations for teh specified station"
)
async def weather(id: int, starting_after: str = None, created: datetime.date = None, limit: int = 10):
    """
    # Get and filter weather observations for a station with the given ID.
    
    ## Path parameter
    
    ### id
    
    The id of the station from which to retrieve weather observations. This parameter takes precedence over all other filters.
    
    ## Query parameters
    
    ### limit
        
    The maximum number of observations to return.  
    If not provided, the first 10 observations will be returned.  
    Maximum of 100 observations, minimum of 1 observation.
    This is the _last_ filter applied when mixed with `created` and `starting_after`.
    
    #### Example(s)
    
    - `http://localhost:8000/stations/1/weather`: Return the first 10 observations for station 1.  
    - `http://localhost:8000/stations/1/weather?limit=5`: Return the first 5 observations for station 1.  
    - `http://localhost:8000/stations/1/weather?limit=100`: Return the _maximum_ of 100 observations for station 1.  
    - `http://localhost:8000/stations/1/weather?limit=101`: Return a 422 bad parameter error. Limit must _not_ be > 100.  
        
    ### created
    
    Filter observations by date, after which we will return `limit` observations.  
    If not provided, the first `limit` observations will be returned.  
    Dates must be in the format YYYY-MM-DD.  
    Maximum of 100 observations.  
    This is the _first_ filter applied when mixed with `starting_after` and `limit`.  
    
    #### Example(s)
    
    - `http://localhost:8000/stations/1/weather?created=2019-07-11`: Return the first 10 observations that were created on 2019-07-11 for station 1.  
    - `http://localhost:8000/stations/1/weather?created=2019-07-11&limit=20`: Return the first 20 observations that were created on 2019-07-11 for station 1.  
    - `http://localhost:8000/stations/1/weather?created=2019-07-11&limit=101`: Return a 422 bad parameter error. Limit must _not_ be > 100.  
    - `http://localhost:8000/stations/1/weather?created=2021-07-31`: Return a 404 error. There are no observations created on 2021-07-31.  
    - `http://localhost:8000/stations/1/weather?created=2019-07-11&starting_after=obs_1NqrK3mraUzaj2j7hg6VcB23RjJ&limit=20`:  
        - First, filter out all observations that _aren't_ for station with id 1.
        - Then, filters out all observations that did _not_ happen on 2019-07-11.  
        - Then, skips over the observations before the observation with id `obs_1NqrK3mraUzaj2j7hg6VcB23RjJ`.  
        - Return the first 20 observations from that point.  
    
    ### starting_after
    
    The ID of the observation, after which we will return `limit` observations.  
    If not provided, the first `limit` observations will be returned.  
    This filter is always applied _after_ `created` but _before_ `limit`.  
    
    #### Example(s)
    
    - `http://localhost:8000/stations/1/weather?starting_after=obs_1NqnftCklLZHBCHyykvcuc8QvE9`:  
        - Return the first 10 observations starting immediately _after_ the observation with id `obs_1NqnftCklLZHBCHyykvcuc8QvE9` for station with id 1.
    - `http://localhost:8000/stations/1/weather?starting_after=obs_1NqnftCklLZHBCHyykvcuc8QvE9?limit=22`:
        - Return the first 22 observations starting immediately _after_ the observation with id `obs_1NqnftCklLZHBCHyykvcuc8QvE9` for station with id 1.
    - `http://localhost:8000/stations/1/weather?created=2019-07-11&starting_after=obs_1NqrK3mraUzaj2j7hg6VcB23RjJ&limit=20`:  
        - First, filter out all observations that _aren't_ for station with id 1.
        - Then, filters out all observations that did _not_ happen on 2019-07-11.  
        - Then, skips over the observations before the observation with id `obs_1NqrK3mraUzaj2j7hg6VcB23RjJ`.  
        - Return the first 20 observations from that point.  

    \f
    Args:
        id (int): The id of the station from which to retrieve weather observations.
        starting_after (str, optional): [description]. Defaults to None.
        created (datetime.date, optional): [description]. Defaults to None.
        limit (int, optional): [description]. Defaults to 10.

    Raises:
        BadQueryParameterException: [description]
        NotFoundException: [description]

    Returns:
        [type]: [description]
    """
    
    # if the limit requested is > 100, or < 1, raise a BadQueryParameterException
    if limit > 100 or limit < 1:
        raise BadQueryParameterException()
    
    conn = sqlite3.connect(database_path)
    
    # NOTE: The first filter applied below, regardless of query parameter, is the filter on station id. 
    # Before all other filters, observations are first pared down to those that match the station id.
    
    # if both query parameters are provided, filter first by `created`, and then by `starting_after`. Limit output to `limit`.
    if starting_after and created:
        results = queries.get_observations_for_station_created_at_starting_after(conn, limit=limit, station_id=id, created_at=created, id=starting_after)
    
    # otherwise, if `starting_after` is the only parameter provided, filter by `starting_after`. Limit output to `limit`.
    elif starting_after:
        results = queries.get_observations_for_station_starting_after(conn, limit=limit, station_id=id, id=starting_after)
        
    # otherwise, if `created` is the only parameter provided, filter by observations occuring on the provided date. Limit output to `limit`.
    elif created:
        results = queries.get_observations_for_station_created_at(conn, limit=limit, station_id=id, created_at=created)
        
    # otherwise, just return the first `limit` observations
    else:
        results = queries.get_observations_for_station(conn, limit=limit, station_id=id)
        
    conn.close()
        
    if not results:
        raise NotFoundException()
    
    observations = []
    for observation in results:
        observations.append(Observation(**{key: observation[i] for i, key in enumerate(Observation.__fields__.keys())}))
    
    return observations