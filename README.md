# SUMO visualisation dashboard

A proof-of-concept Streamlit dashboard to visualise traffic simulation output without
having to run SUMO itself.


## Purpose

The SUMO toolkit enables a lot of possibilities to simulate traffic data. However, its particular file formats 
are not particularly friendly for further usage outside the SUMO ecosystem. This repository tries to achieve two purposes:
1. Convert the data into formats that can be easily used in other tools, such as Pandas DataFrames.
2. Provide an ad-hoc ("plug and play") visualisation tool using Streamlit. 
This allows a user to visualise SUMO output without the need to open SUMO itself.

### Supported simulation output types
This repository currently supports some of the most common outputs of SUMO. These include:
- **Origin-Destination (O/D) matrix:** "This many people went from `a` to `b`."
- **Trips:** "`x` went from `a` to `b`, and departed at `t`."
- **Routes:** "`x` took specific edges to get from `a` to `b`. The total duration was `t`."
- **Edges:** "At any point of time `t`, how busy is edge `e`?"

In the future, hopefully the following will be supported as well. However, the often huge file sizes are causing issues:
- **Floating car data (FCD):** "At any point of time `t`, where was `x`?"

### Data inspection
Beyond visualising SUMO data, the dashboard also has some "data inspection" features. 
For example, one can check whether a network `.geojson` file is working by uploading the file to a dedicated page on the dashboard.
Furthermore, the individual visualisation pages usually also have a section where one can inspect what the raw data looks like.

### Utilities
The repository also contains a few utilities which can in theory also be used independently of the dashboard.
- The [`geo_bounds`](./src/util/geo_bounds.py) utility computes a centroid coordinate for a GeoDataFrame, such that it can any maps using this GeoDataFrame can easily be centred. Files in the `.geojson` format can easily be converted into a GeoDataFrame, which thus makes it convenient to use inside the dashboard.
- The [`sumo_conversions`](./src/util/texts.py) utility allows a SUMO O/D matrix and trip to be represented as a Python object. These methods also make "pretty" printing the properties of the objects possible.


## Usage

### Python requirements
#### Version
This project is built and tested using **Python 3.11**. 
The dashboard is also tested to work on Python 3.10, 
but this is not guaranteed. Due to a strong use of typing throughout the code,
older versions of Python are definitely not supported.

#### Use a virtual environment
This project is best used with a virtual environment. 
A virtual environment allows you to isolate all required modules for this tool from required modules that any other tools might need.
This can prevent issues in case another script you use has another required version of a dependency, 
and also prevents this tool from accidentally interfering with your base Python installation (which is especially important for Linux users).

For a detailed description on how to best install virtual environments on your operating system,
please check the [Streamlit installation guide](https://docs.streamlit.io/library/get-started/installation).
Note that this dashboard has a few additional requirements on top to run properly (see below), and mandates the use of Python 3.10 or newer. 

Alternatively, you can read more about virtual environments in the [official Python documentation](https://docs.python.org/3/library/venv.html).

### Install all dependencies
Once you have created a virtual environment, have activated it, and you have opened Bash in the root folder of this project, you can install all dependencies for this project using:
```bash
pip install -r requirements.txt
```

### Launch the dashboard
After having created installed all dependencies, you can run the tool by running the following Bash command:
```bash
streamlit run ./src/Home.py &
```
To explain what this command does:
- `streamlit run` is the command that runs the dashboard
- `./src/Home.py` instructs streamlit to run the `Home.py` file, which is located in `./src` (the `src` folder that is in the current directory `.`).
- `&` ensures that your terminal can run other commands without immediately closing the dashboard. You can omit the `&` if you want to be able to shut it down easily.

Upon launching the dashboard, the homepage should load automatically. 
From there onwards, the rest should be straightforward!

## About the project

The project is made by me for a project at the Technical University of Munich (TUM),
in collaboration with the [Chair of Transportation Systems Engineering](https://www.mos.ed.tum.de/en/vvs/home/).
Upon completion of the project, we decided to make it public to see if others could make good use of it! :)

### Coding style
Most functions in this module are type-hinted and use numpy-style docstrings. 
This should make the code easily reusable, expandable, and maintainable.

Furthermore, the code is formatted using [Black](https://github.com/psf/black),
which enforces a strict variant of the [PEP-8 style guide](https://peps.python.org/pep-0008/). 
The default settings are used, except for the maximum line length which is set to 100 characters (through the `pyproject.toml` file).

### Contributing
As mentioned above, this code was originally by just one person,
but people are always welcome to extend the project and make additions to it.



## Example data

This repository contains some demo data that can be used in the dashboard for testing purposes.
A user can either tick a box inside the dashboard that automatically loads the files, or "upload" those files themselves (to test the upload functionality).

For more information on this data, please read the [README.md](./demo_data/README.md) inside the `demo_data` directory.


## Limitations

### General performance
The entire repository is based on a Python framework. Although Python allows for fast prototyping, it is not quite an efficient language.
Some of the functionalities in this dashboard require heavy data processing, and for performance reasons a lower-level (compiled) language is usually better suited for that.


### Kepler
[Kepler](https://kepler.gl/) is a great library for visualising maps in a dynamic way. 
However, it is mainly written for JavaScript, and hence support inside Streamlit is limited.

More specifically, the support inside Streamlit is currently made possible by the 3rd-party [streamlit-keplergl](https://pypi.org/project/streamlit-keplergl/) module.
However, it only supports "static" components, 
meaning that any changes made inside the Kepler map cannot be 'seen' by the Streamlit dashboard.
Because of this, some Kepler-related features (such as saving the map configuration) are limited in this dashboard. 

### Robustness

Although the code has been tested on the demonstation data (and some similar data), 
it is very likely that there is variations of input for which the dashboard does not (yet) work as intended. 
For the most part this is simply because this project was meant as a proof-of-concept.
However, if you encounter an issue and can figure what causes it and how to resolve it, you are always welcome to open a Pull Request!

Over time, this process should hopefully make the dashboard more robust :)


## Related repositories

### Code
This code on this repository uses the following modules:

- [geopandas](https://github.com/geopandas/geopandas)
- [pandas](https://github.com/pandas-dev/pandas)
- [plotly](https://github.com/plotly/plotly.py)
- [seaborn](https://github.com/mwaskom/seaborn)
- [streamlit](https://github.com/streamlit/streamlit)
- [streamlit-keplergl](https://pypi.org/project/streamlit-keplergl/) 

### SUMO
- [Eclipse SUMO](https://github.com/eclipse/sumo): **S**imulation of **U**rban **MO**bility, the tool around which this repo is oriented. 
- [sumo-calibration](https://github.com/vishalmhjn/sumo-calibration): Some data from this project is used as demo data inside this dashboard, read [here](./demo_data/README.md) for more info.
- [SumoNetVis](https://github.com/patmalcolm91/SumoNetVis): Another visualisation tool, which combines SUMO net files and trajectories to visualise networks.
- [sumo-output-parsers](https://github.com/Kensuke-Mitsuzawa/sumo-output-parsers): Some parsers that can be used to ease further development on this dashboard.
