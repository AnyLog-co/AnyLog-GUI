"""
The following is based on: https://stackoverflow.com/a/46589405 
"""
import requests 
from shapely.geometry import mapping, shape
from shapely.prepared import prep
from shapely.geometry import Point

         
def __get_world_locations()->dict: 
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

def __get_state_locations()->dict: 
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
    file_data = requests.get("https://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_20m.json").json()
    for feature in file_data['features']:
        geom = feature['geometry'] 
        country = feature["properties"]["NAME"] 
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

def get_location(geo_locations, lon:float, lat:float): 
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
            print(country)
            exit(1) 
    return 'Unknown'

def main(conn:str)->dict: 
    """
    The following extracts the location informaiton from the blockchain (based on IP & Port) and returns a country
    :args: 
        conn:str - AnyLog REST connection info 
        data_dir:str - Directory containing countries & states geolocation coordinates 
    :param: 
        geo_locations:dict - coordinate/country location info
        conn:str - connection info to blockchain
        blockchain_location_info:dict - for each node type a list of the different locations 
        countries:dict - a copy of blockchain_location_info but with country names rather than coordinates
        data:dict - for blockchain_location_info add country name
    :return: 
        data 
    :sample output: 
    {
        node-type: { 
            node-name: {
                country: name,
                loc: coordinates,
                state: if country is USA
            }
        }
    }
    """
    world_geo_locations = __get_world_locations()
    state_geo_locations = __get_state_locations()
    data = {'master': {}, 'operator': {}, 'publisher': {}, 'query': {}} 
    blockchain_locations = get_blockchain_locations(conn)
    for node in blockchain_locations: 
        for name in blockchain_locations[node]: 
            lat, lon = blockchain_locations[node][name].split(', ') 
            country = get_location(world_geo_locations, float(lon), float(lat))
            data[node][name] = {'country': country, 'loc': blockchain_locations[node][name]}
            if country == 'United States of America': 
                state = get_location(state_geo_locations, float(lon), float(lat))
                data[node][name]['state'] = state 
    return data 
            
    

if __name__ == '__main__':
    import argparse 
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter) 
    parser.add_argument('conn',             type=str, default='23.239.12.151:2049',           help='AnyLog REST connection info') 
    args = parser.parse_args()

    print(main(args.conn))
