"""
The following is based on: https://stackoverflow.com/a/46589405 
"""
import requests 
from shapely.geometry import mapping, shape
from shapely.prepared import prep
from shapely.geometry import Point

def get_locations()->dict: 
    """
    The following prepares GEO location information. 
    Unlike other formats the information is extracted via a preset document that doesn't require API access 
    :param: 
        file_data:dict - JSON information coorelating countries to locations 
        geom:dict - coordinate locations 
        country:str - country name(s) for location  
        geo_locations:dict - coorelation between country (key) and geom coordinates (value)  
    :return: 
        geo_locations
    """
    geo_locations = {} 
    # Get general country/coordinates file 
    file_data = requests.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()
    for feature in file_data['features']:
        geom = feature['geometry'] 
        country = feature["properties"]["ADMIN"] 
        geo_locations[country] = prep(shape(geom)) 
    return geo_locations 

def get_blockchain_locations(conn:str)->dict: 
    """
    From AnyLog get coordiantes 
    :args:
       conn:str - Connection IP & Port 
    :param: 
       query:str - Blockchain query statement that includes node name & coordinates 
       data:dict - data from blockchain 
    :return: 
       data 
    """
    query = "blockchain get %s bring [%s][name] : [%s][loc] separator=' '"
    data = {'master': {}, 'operator': {}, 'publisher': {}, 'query': {}} 
    for node in data: 
        coordinates = {} 
        r = requests.get('http://%s' % conn, headers={'type': 'info', 'details': query % (node, node, node)})
        for output in r.json()['Blockchain data'].replace(', ', ',').replace("'", "").split(' '):
            coordinates[output.split(':')[0]] = output.split(':')[1].replace(',', ', ') 
        data[node] = coordinates 
    return data 

def get_country(geo_locations, lon:float, lat:float): 
    """
    Given that lon & lat from blockchain get country location 
    :args: 
       geo_locations:dict - coordinate/country location info
       lon:float - longatitude
       lat:float - latitude 
    :param: 
        point:shapely.geometry.point.Point - combination of lon & lat 
        country:str - from geo_locations list of countries
        geom:shapely.prepared.PreparedGeometry - list(s) of coordinates to check through 
    :return: 
        country - if unable to find country 'Unknown' 
    """
    point = Point(lon, lat)
    for country, geom in geo_locations.items(): 
        if geom.contains(point): 
            return country
    return 'Unknown'

def main()->dict: 
    """
    The following extracts the location informaiton from the blockchain (based on IP & Port) and returns a country
    :param: 
        geo_locations:dict - coordinate/country location info
        conn:str - connection info to blockchain
        blockchain_location_info:dict - for each node type a list of the different locations 
        countries:dict - a copy of blockchain_location_info but with country names rather than coordinates
        data:dict - for blockchain_location_info add country name
    :return: 
        data 
    """
    geo_locations = get_locations()
    data = {'master': {}, 'operator': {}, 'publisher': {}, 'query': {}} 
    conn = input('Connection Info (IP:Port): ') 
    blockchain_locations = get_blockchain_locations('23.239.12.151:2049')
    for node in blockchain_locations: 
        for name in blockchain_locations[node]: 
            lat, lon = blockchain_locations[node][name].split(', ') 
            country = get_country(geo_locations, float(lon), float(lat))
            data[node][name] = {'country': country, 'loc': blockchain_locations[node][name]}
    return data 
            
    

if __name__ == '__main__':
    print(main())
