# Emoji.
INFO_ICON = "ℹ️"  # :information_source:
WARNING_ICON = "⚠️"  # :warning:

# Information at the start of each page.
ABOUT_HOMEPAGE = """
Welcome! This is a visualisation dashboard for [SUMO](https://sumo.dlr.de/docs/index.html).

The goal of this website is to have **one** tool for the most used SUMO visualisations, 
all in one place! 
__No__ need to launch SUMO just to show some graphs, __no__ separate scripts for each graph!


## How to use

On the sidebar (to the left) there are several types of visualisations available for you. 
Simply select the category of interest, upload the relevant files, and that's it!

### Available tools:
1. O/D Matrix inspection: A simple page on which you can see what data is 'fed' into the model. 
Peek at the Origin-Destination Matrix, right in here, without the need to open any other program!

2. Trips: See stats about trip distribution over time, and 
check how many people depart/arrive from a TAZ.

3. Routes: Inspect individual routes taken by agents.

4. Congestion: Check the congestion of individual edges in the network, 
as well as network-wide for a given timestamp.

5. Geojson inspection: Before using any of the visualisation pages, you can 
upload your `.geojson` files on this page to check whether you selected the correct file, and 
whether the file works.
"""

ABOUT_INPUT_PAGE = """
    The Origin-Destination matrix depicts the amount of trips between two TAZs that will be fed
    into the simulation. This file allows you to see summary data of the OD-file, 
    as well as a map of the flows.  
"""

ABOUT_TRIPS_PAGE = """
    This page allows you to inspect aggregate data about trips,  
    for example how many trips start or end at a certain TAZ. 
    There is two types of files needed for this analysis:
    1. A `.xml` file with all the trips to consider in the analysis;
    2. A `.geojson` file containing all the TAZs.
"""

ABOUT_ROUTES_PAGE = """
    On this page, you can take a deep dive into specific routes. 
    Which edges are traversed, and are there any re-computations performed during the trip?
    
    As on the other pages, there is the chance to inspect the "raw" data of each file.
    Furthermore, you can also see some general characteristics about the route, 
    for example in which TAZ the route started.

    This page requires two types of files to be uploaded:
    1. A `.xml` file with one or more routes to inspect;
    2. A `.geojson` file containing the network of the simulation.
"""

ABOUT_CONGESTION_PAGE = """
    On this page, you can visualise congestion using several metrics across a timespan.
    For that, you need only two files:
    1. A `.geojson` file of the network which is visualised;  
    2. A `.csv` file data about the edges in the network.
    
    After uploading the files, you can then choose which metric you wish to visualise.
    Whether it is average speed or the lane density, 
     you can choose the column and scroll through the time.
"""

ABOUT_INSPECTION_PAGE = """
    This page allows you to inspect a geojson file before using it on other pages. 
    That way, you can be sure that the file is valid, and see some of its basic properties.
    For further analysis, please use the other pages with a working geojson file!
"""

# Other notices.
UPLOAD_INFO = """
    Below, you can upload the files you want to visualise.
    If you're just here for a demonstration, check the following box.
"""

UPLOAD_INFO_OD = """
    Below, you can upload the O/D matrix you want to visualise.
    If you're just here for a demonstration, check the following box.
    This will allow you visualise several different O/D matrices on the same network,
    which also showcases the flexibility of the dashboard. 
"""


XML_SLOW_INFO = "It may take a while for the XML data to load (due to parsing). Just be patient!"

KEPLER_WORKAROUND = """
    To give the edges the colour based on your filters, please do the following:
    
    1. Click the `>` button in the top-left of the map.
    2. Expand the *Traffic data* layer (right above the *Add Layer* button).
    3. Click on the three dots next to *Stoke Color*.
    4. Under *Stroke Color Based On*, select "`{col}`" (the column you filtered).
    
    Due to a Kepler limitation, this can currently not be automated.
"""
