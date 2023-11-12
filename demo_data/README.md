# Demonstration data

## About this directory
To showcase the functioning of the dashboard, each page needs some dedicated sample data. 
To prevent users having to configure repositories or otherwise tweak configuration files to get sample data to work,
 the repository contains some (relatively small) demo data. 
The total size of this directory should be around ~50MB. 

## About the data

Most of the data is taken from the [sumo-calibration](https://github.com/vishalmhjn/sumo-calibration) repository by [@vishalmhjn](https://github.com/vishalmhjn), which orients around the German city of Munich.
The license in `LICENSE-sumo-calibration` applies to these files.
Some other data is related to that repository, but not published in there. 
Any data present on the aforementioned repository is marked with a ‡.
 

- `geojson_files/network.geojson` • The network used for simulations. ‡
- `geojson_files/traffic_analysis_zones.geojson` • A file containing all TAZs. Named `munich_zones.json` on the `sumo-calibration` repository. ‡
- `od_matrix/*.txt` • Origin/Destination matrices in text format. ‡
- `xml_files/edge_data_3600.{csv,xml}` • Aggregate statistics about traffic on edges in specific time ranges. The files contain the same data, just in a different format.
- `xml_files/route_sample.xml` • A sample of 2826 routes taken from a large simulation on the network. This data includes which edges a vehicle traversed.
- `xml_files/route_sample_small.xml` • Idem, but with only 10 routes (of which two have replaced routes).
- `xml_files/trips.trips.xml` • A collection of trips (without routes), tagged with their departure location and destination location (edge and TAZ).