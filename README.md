# Climber Mapper
A tool to quickly add rock climbs to a map

# This Script Should Be Called Like:
python3 climber_mapper.py <state> "<area>" "<route 1>" "<route 2>" ...

(The quotes are required if your area or route names have spaces in them)

The script outputs a human-readable table of the routes it finds

It also outputs a file that looks like <area>_todays-date_coordinates.json

This json file is geojson data which can be imported into mapper programs (like caltopo)

# Data Source
This project uses open source data from [OpenBeta](https://openbeta.io/)

[This Repository](https://github.com/OpenBeta/climbing-data) contains the json file necessary to run the Climber Mapper script

TODO: Need to import the OpenBeta climbing data as a sub-repo so we can easily get updates
