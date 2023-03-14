#!/usr/bin/python3
import pandas as pd
import sys
import json
from datetime import date

# This Script Should Be Called Like: 
# python3 climber_mapper.py <state> "<area>" "<route 1>" "<route 2>" ...
# The quotes are required if your area or route names have spaces in them

# The script outputs a human-readable table of the routes it finds
# It also outputs a file that looks like <area>_todays-date_coordinates.json
# This json file is geojson data which can be imported into mapper programs (like caltopo)

# Some default input arguments in case the user doesn't input any
state = "co"
parent_area = "Eldorado"
input_routes = [ "Rewritten", "Bastille", "Rebuffat's Arete" ]

# Parse command-line arguments
num_args = len(sys.argv)
if (num_args > 1):
    state = sys.argv[1]

if (num_args > 2):
    parent_area = sys.argv[2]

if (num_args > 3):
    # Interpret all remaining arguments as a list of route names
    input_routes = sys.argv[3:]

# Construct file path
area_source = "all_routes/" + state + "-areas.jsonlines"
route_source = "all_routes/" + state + "-routes.jsonlines"

# Read json files, note that they are multi-line JSON files
areas = pd.read_json(area_source, lines=True)
routes = pd.read_json(route_source, lines=True)

# There are better ways for pandas to extract nested JSON
# But since I couldn't figure that out we can just have pandas parse the nested data seperately
# and add that data as new columns (area, lnglat, us_grade)

# Pull out the metadata JSON field as a list, then have pandas turn it into a dataframe
metadata = pd.DataFrame(routes.metadata.values.tolist())

# Pull out the grade JSON field and interpret it as a new dataframe
grade = pd.DataFrame(routes.grade.values.tolist())

# Extract route area from metadata
routes['area'] = metadata.parent_sector

# Extract [ longitude, latitude ] field from metadata
routes['lnglat']=metadata.parent_lnglat

# Yosemete and V-scale grades are both stored in YDS field, depending on if boulder or not
routes['us_grade']=grade.YDS
#print(routes)

# Use parent_area to filter all areas down to just the ones we want
# I have no idea what squeeze() does, but it allows me to use "contains()" to search the data
# areas_filtered is every area that contains parent_area as a substring
# (e.g. "Joshua Tree" matches "Joshua Tree National Park")
areas_filtered = areas[areas['path'].squeeze().str.contains(parent_area)]
areas_in_parent = areas_filtered['area_name']

# Use areas in parent to filter all routes down to just the ones we want
routes_in_parent = routes[routes['area'].isin(areas_in_parent.tolist())]
#print(routes_in_parent)

# Get list of all routes with names containing our queries
route_names = [] # empty list
for r in input_routes:
    # For example "Lurking" would match "Lurking Fear"
    route_names += routes_in_parent[routes_in_parent['route_name'].squeeze().str.contains(r)]['route_name'].tolist()

# Query remaining routes for the routes we are interested in
# Use loc[:] to copy the data instead of just referencing it (squashes a warning)
result_routes = routes_in_parent[routes_in_parent['route_name'].isin(route_names)].loc[:]

# Pull 'lnglat' out into latitude and longitude, since we eventually want to present the data as [ lat, lon ] (the normal way to read coordinates)
# Using pandas's 'str' here is a bit of a hack but it works
longitudes = result_routes.loc[:,'lnglat'].str[1]
latitudes = result_routes.loc[:,'lnglat'].str[0]

# Turn latitude and longitude into a list of [longitude, latitude] tuples
result_routes['coordinates'] = list(zip(longitudes.tolist(), latitudes.tolist()))

#print(result_routes)
results = result_routes.loc[:, ['route_name', 'area', 'coordinates', 'us_grade']]
print(results.to_string(index=False))


######## CONSTRUCT JSON DATA #############
# We want to be able to import these coordinates into a map
# So lets construct geojson data

geojson = {} # Container for json
geojson['type'] = "FeatureCollection"
features = [] # Empty list of features

# TODO: right now we have one point per route
# but if routes have the same coordinate (same area) it would be cool to combine them
# into one point

for index, row in result_routes.iterrows():
    # Set up required fields
    feature = {}
    feature['type'] = "Feature"
    feature['geometry'] = {}
    feature['properties'] = {}

    feature['geometry']['type'] = "Point"
    feature['geometry']['coordinates'] = row.lnglat

    feature['properties']['marker-symbol'] = "point"
    feature['properties']['description'] = row.route_name + " " + row.us_grade
    feature['properties']['title'] = row.area
    feature['properties']['marker-color'] = "FF0000"
    # TODO: routes data has trad/boulder/sport info
    # we should pull that data out differentiate these by color

    # Append this point to list of features in json
    features.append(feature)

geojson['features'] = features


geojson_results = json.dumps(geojson, indent=4)

# Output json to a file
filename = parent_area + "_" + date.today().strftime("%Y-%m-%d") + "_coordinates.json"
with open(filename, "w") as outfile:
    outfile.write(geojson_results)
