# Standard library.
import datetime as dt
import json

# Dependencies
import matplotlib.pyplot as plt  # Needed to create density plot.
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as p_go
import seaborn as sns  # Needed to create density plot.
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile  # For type checking.

# Local.
from util.geo_bounds import get_gdf_centroid
from util.texts import INFO_ICON, UPLOAD_INFO, XML_SLOW_INFO, ABOUT_TRIPS_PAGE


# Functions.
@st.cache_data
def get_trips_xml_from_config() -> pd.DataFrame:
    """Load the config's xml file into a DataFrame"""
    demo_paths_dict = st.session_state.demo_data
    fp = demo_paths_dict["trips"]
    df_to_return = pd.read_xml(fp)
    return df_to_return


@st.cache_data
def get_trips_xml_from_upload(file: UploadedFile) -> pd.DataFrame:
    """Get the Trips from a user-uploaded xml file, then put it in a DataFrame"""
    df_to_return = pd.read_xml(file)
    return df_to_return


@st.cache_data
def get_geojson_from_file(file: UploadedFile) -> dict:
    geo_dict = json.load(file)
    return geo_dict


@st.cache_data
def get_geojson_from_config() -> dict:
    demo_paths_dict = st.session_state.demo_data
    with open(demo_paths_dict["taz"]) as geo_f:
        geo_dict = json.load(geo_f)
    return geo_dict


@st.cache_data
def get_zones_from_file(file: UploadedFile) -> gpd.GeoDataFrame:
    geo_df = gpd.read_file(file)
    return geo_df


@st.cache_data
def get_zones_from_config() -> gpd.GeoDataFrame:
    demo_paths_dict = st.session_state.demo_data
    geo_df = gpd.read_file(demo_paths_dict["taz"])
    return geo_df


def get_map_obj(series: pd.Series, geo_df: gpd.GeoDataFrame, geojson: dict) -> p_go.Figure:
    """
    Create a map for the TAZ volume

    Parameters
    ----------
    series
        The volume data by TAZ, with as keys the TAZ IDs, and as value the volume.
    geo_df
        A GeoDataFrame containing the TAZs. Used to find a central point.
    geojson
        The original Geojson dictionary for the TAZs. Used for creating the map itself.

    Returns
    -------
    p_go.Figure
        a Choropleth map compatible with the Streamlit Mapbox functionality.

    """
    ret_fig = p_go.Figure(
        p_go.Choroplethmapbox(
            geojson=geojson,
            locations=series.index,  # The index of the values in the series.
            z=series.values,  # The values in the series to plot
            featureidkey="properties.NO",
            colorscale="sunset",
            # zmin=0,
            # zmax=500000,
            marker_opacity=0.5,
            marker_line_width=0,
        )
    )
    x_coor, y_coor = get_gdf_centroid(geo_df)
    ret_fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=9,  # TODO: Find a way to automatically determine zoom level.
        mapbox_center={"lat": y_coor, "lon": x_coor},
        width=800,
        height=1000,
    )
    return ret_fig


# Plot configuration.
sns.set_style("whitegrid")

# Streamlit.
state = st.session_state

with st.container():
    st.title("SUMO Trip analysis")

# Try to visualise xml file.
# Columns: id, depart, departLane, departSpeed, from, fromTaz, to, toTaz
xml_df: pd.DataFrame | None = None
taz_gdf: gpd.GeoDataFrame | None = None
geojson_dict: dict | None = None

# Allow the user to upload their own files, if they want to.
# Otherwise, use the default files (in the config) for demo purposes.
with st.container():
    st.write(ABOUT_TRIPS_PAGE)
    st.divider()
    st.write(UPLOAD_INFO)
    use_demo_files_2: bool = st.checkbox("Try out the demo files", value=False)

if use_demo_files_2:  # Use config! Config is embedded into the session state.
    xml_df = get_trips_xml_from_config()
    geojson_dict = get_geojson_from_config()
    taz_gdf = get_zones_from_config()
else:  # User files needed.
    st.header("File upload")
    st.write("Please select the files you want to visualise.")
    st.info(XML_SLOW_INFO, icon=INFO_ICON)
    xml_file: UploadedFile = st.file_uploader("Upload your trips file here", type="xml")
    geojson_file: UploadedFile = st.file_uploader(
        "Upload your **TAZ** `.geojson` file here", type="geojson"
    )
    if xml_file:
        xml_df = get_trips_xml_from_upload(xml_file)
    if geojson_file:
        geojson_dict = get_geojson_from_file(geojson_file)
        taz_gdf = get_zones_from_file(geojson_file)


if xml_df is not None:
    st.header("Trip data")
    # Raw data.
    with st.container():
        st.subheader("A look at the raw data")
        with st.expander("Click to inspect the raw data layout"):
            st.write("This is what the 'head' of the raw data looks like:")
            st.dataframe(xml_df.head().style.format(thousands=None, precision=0))

    # Trip summary data.
    with st.container():
        st.subheader("Summary data")
        st.write("Timeframe")
        col1, col2, col3 = st.columns(3)
        first_t = xml_df.depart.min()
        last_t = xml_df.depart.max()
        # int() rounds down the value; +1 forces a round-up.
        total_seconds = int(last_t - first_t) + 1
        col1.metric("Duration", str(dt.timedelta(seconds=total_seconds)))
        col2.metric("Earliest timestamp", first_t)
        col3.metric("Latest timestamp", last_t)
    with st.container():
        st.write("Trip dimensions")
        col1, col2, col3 = st.columns(3)
        col1.metric("Trip count", len(xml_df))
        col2.metric("Origin TAZs", xml_df.fromTaz.nunique())
        col3.metric("Destination TAZs", xml_df.toTaz.nunique())

    # Departure density.
    with st.container():
        fig: plt.Figure = plt.figure(figsize=(9, 7))
        st.subheader("Departure time density plot")
        st.write("Use the slider below to adjust the bandwidth.")
        bw: float = st.slider(label="Bandwidth", min_value=0.01, max_value=5.0, value=2.5)
        plt.title("Departure time density")
        density_plot = sns.kdeplot(xml_df.depart, bw_adjust=bw)
        st.pyplot(fig)

    # TAZ analysis.
    with st.container():
        st.subheader("TAZ counts")
        # do_sort: bool = st.checkbox("Sort by count", value=False)
        st.write("By origin")
        from_counts: pd.Series = xml_df.fromTaz.value_counts()
        st.bar_chart(from_counts)
        st.write("By destination")
        to_counts: pd.Series = xml_df.toTaz.value_counts()
        st.bar_chart(to_counts)

# Only plot maps if geojson dict is uploaded.
if xml_df is not None and taz_gdf is not None:
    assert geojson_dict is not None, "taz_gdf and geo_json dict should both exist!"
    with st.container():
        st.subheader("TAZ heatmap")
        st.write(
            "The plots below show a heatmap of the zones and the trips that "
            "start (=Origin) or end (=Destination) there. "
            "Please note that the map will only render with an internet connection."
        )
        tab1, tab2 = st.tabs(["Origin", "Destination"])
        with tab1:
            geo_o = get_map_obj(from_counts, taz_gdf, geojson_dict)
            st.plotly_chart(geo_o)
        with tab2:
            geo_d = get_map_obj(to_counts, taz_gdf, geojson_dict)
            st.plotly_chart(geo_d)
elif xml_df is not None:  # Only show the .geojson warning if an XML file is uploaded.
    st.header("Heatmaps")
    st.warning(
        "You have not uploaded a `.geojson` file! If you wish to see heatmaps, please upload one."
    )
else:
    pass
