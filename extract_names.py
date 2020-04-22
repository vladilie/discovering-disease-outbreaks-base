import re
import geonamescache
from unidecode import unidecode
import pandas as pd

gc = geonamescache.GeonamesCache()

whitespace = '\s'
endswith_pattern='(?:\s|^[^a-zA-Z]+|\?|,|$)'
cities = gc.get_cities()
city_names = list(map(lambda key: cities[key]['name'].replace(' ', whitespace), cities))
city_names_ended = list(map(lambda city: city + endswith_pattern, city_names))
city_names_regexp = f"{'|'.join(city_names_ended)}"
city_regex = re.compile(city_names_regexp)

startwith_city_names_regexp = f"^({'|'.join(city_names)})"
startwith_regex = re.compile(startwith_city_names_regexp)

countries = gc.get_countries()
country_names = list(map(lambda key: countries[key]['name'].replace(' ', whitespace), countries))
country_names = list(map(lambda country: country + endswith_pattern, country_names))
country_names_regexp = f"{'|'.join(country_names)}"
country_regex = re.compile(country_names_regexp)

before_interjections = "( ruining | reaches | at | is | strikes | reach | in | to | visiting )"
cityname_after_string = f"{before_interjections}([A-Z][a-z'.]*)(\s[A-Z][a-z'.]*)*"
cityname_after_regexp = re.compile(cityname_after_string, flags=re.IGNORECASE)

after_interjections = "( plans | Struck | is\sinfested | residents | Cholera | Outbreak | Patient | lab | team | experts | Health |’s\sfirst\sZika | Zika | Hairstyle | now | reports | teen | scientists | takes | patient | man | woman | uses | confirms | fighting | Addressing | Deals | Tourism | Woman | Establishes | resident | tries | under | Reports | hit | takes\sa\shit | sets | volunteers | authorities | Residents | Experiences | Encounters | tests | all\sover| through | hits | Hits | help | Left | over )"
cityname_before_string = f"([A-Z][a-z'.]*)(\s[A-Z][a-z'.]*)*{after_interjections}"
cityname_before_regexp = re.compile(cityname_before_string, flags=re.IGNORECASE)
possible_regexp = [cityname_after_regexp, cityname_before_regexp]

count = 0
panda_data = []
with open('data/headlines.txt', 'r') as f:
    for line in f:
        line = line.strip()
        city_result = city_regex.search(line)
        country_result = country_regex.search(line)

        if city_result is None:
            city = None
            start_result = startwith_regex.search(line)
            if start_result is None:
                result = next(filter(lambda r: r is not None, map(lambda r: r.search(line), possible_regexp)), None)
                if result is not None:
                    matching_items = result.groups()
                    matching_items = list(filter(lambda x: x is not None, matching_items))
                    matching_items = list(map(lambda x: str(x).strip(), matching_items))
                    matching_items = list(filter(lambda x: x not in before_interjections, matching_items))
                    matching_items = list(filter(lambda x: x not in after_interjections, matching_items))

                    second_try_city = " ".join(matching_items)
                    if city is None:
                        city = second_try_city
                    elif city in second_try_city:
                        city = second_try_city
            else:
                city = start_result.group()
        else:
            city = city_result.group()

        if country_result is None:
            country = None
        else:
            country = country_result.group()

        if city is not None:
            panda_data.append([line, country, city])
        else:
            print(line)

column_names = ['headline', 'countries', 'cities']
df = pd.DataFrame(panda_data, columns=column_names, dtype=str)

df.to_pickle('city_names_panda.dataframe')

with open('city_names_panda.csv', 'w') as f:
    f.write(','.join(column_names))
    for row in panda_data:
        f.write(str(row[0]) + ',' + str(row[1]) + ',' + str(row[2]) +'\n')

