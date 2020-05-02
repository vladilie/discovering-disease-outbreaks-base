import pandas as pd
import geonamescache
import re

df = pd.read_pickle("city_names_panda.dataframe")
gc = geonamescache.GeonamesCache()

panda_data=[]
for d in df.to_dict('records'):
    city = d['cities']
    country = d['countries']
    headline = d['headline']

    city = re.sub(r'\W+ ', '', city)
    panda_data_item = [headline, city, country]

    city_lookup = gc.get_cities_by_name(city)
    if len(city_lookup) == 0:
        panda_data_item.append(0)
        panda_data_item.append(0)
    else:
        cached_city = list(max(city_lookup, key=lambda x: list(x.values())[0]['population']).values())[0]
        lat = cached_city['latitude']
        long = cached_city['longitude']
        panda_data_item.append(lat)
        panda_data_item.append(long)
        panda_data.append(panda_data_item)


column_names = ['headline', 'countries', 'cities', 'lat', 'long']
df = pd.DataFrame(panda_data, columns=column_names, dtype=str)

df.to_pickle('lat_long_city_names_panda.dataframe')