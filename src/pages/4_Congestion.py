# Dependencies.
import geopandas as gpd
import pandas as pd
import streamlit as st
from keplergl import KeplerGl
from streamlit.runtime.uploaded_file_manager import UploadedFile  # For type checking.
from streamlit_keplergl import keplergl_static

# Local.
from util.texts import ABOUT_CONGESTION_PAGE, KEPLER_WORKAROUND, INFO_ICON, UPLOAD_INFO


# Functions.
@st.cache_data
def get_default_geojson() -> gpd.GeoDataFrame:
    demo_paths_dict = st.session_state.demo_data
    ret_df = gpd.read_file(demo_paths_dict["network"])
    return ret_df


@st.cache_data
def get_default_traffic_data() -> pd.DataFrame:
    demo_paths_dict = st.session_state.demo_data
    ret_df = pd.read_csv(demo_paths_dict["edge_csv"], delimiter=";")
    return ret_df


@st.cache_data
def get_geojson_from_file(file: UploadedFile) -> gpd.GeoDataFrame:
    ret_df = gpd.read_file(file)
    return ret_df


@st.cache_data
def get_traffic_from_csv(file: UploadedFile) -> pd.DataFrame:
    ret_df = pd.read_csv(file, delimiter=";")
    return ret_df


# Streamlit.
with st.container():
    st.title("Road congestion analysis")
    st.write(ABOUT_CONGESTION_PAGE)
    st.divider()

geo_df: gpd.GeoDataFrame | None = None
traffic_df: pd.DataFrame | None = None

# Allow the user to upload their own file, if they want to.
# Otherwise, use the default file (in the config) for demo purposes.
st.write(UPLOAD_INFO)
use_demo_files_4: bool = st.checkbox("Try out the demo files", value=False)

if use_demo_files_4:  # Use config! Config is embedded into the session state.
    geo_df = get_default_geojson()
    traffic_df = get_default_traffic_data()
else:  # User files needed.
    st.header("File upload")
    st.write("Please select the files you want to visualise.")
    geojson_file: UploadedFile = st.file_uploader(
        "Upload your network .geojson file here", type="geojson"
    )
    # TODO: Eventually support both CSV and XML.
    csv_file: UploadedFile = st.file_uploader("Upload the edge traffic data here", type="csv")
    if geojson_file and csv_file:
        geo_df = get_geojson_from_file(geojson_file)
        traffic_df = get_traffic_from_csv(csv_file)
    elif geojson_file:  # But not csv file.
        st.info("Traffic file missing")
    elif csv_file:  # But not geojson_file
        st.info("geojson file missing")
    else:
        st.info("Both files missing")


# Try to create map if both files are loaded.
if isinstance(geo_df, gpd.GeoDataFrame) and isinstance(traffic_df, pd.DataFrame):
    # Ask the user what they would like to filter the data on.
    st.header("Data filters")
    # [6:] filters out the first few columns (which includes timestamps and edge IDs).
    column_filter = st.selectbox(label="Column to visualise", options=list(traffic_df.columns[6:]))

    # Merge the data. General procedure:
    # 1. Allow the user to set the time (as `time_slide`):
    #   min(interval_begin) <= time_slide <= max(interval_end).
    assert "interval_begin" in traffic_df.columns
    assert "interval_end" in traffic_df.columns
    time_min = int(traffic_df.interval_begin.min())
    time_max = int(traffic_df.interval_begin.max())

    st.write("Use the slider below to adjust the time.")
    time_slide: int = st.slider(
        label="Timestamp", min_value=time_min, max_value=time_max, value=time_min
    )
    # 2. Filter traffic_df based on `time_slide` and `column_filter`.
    # Helped by: https://gis.stackexchange.com/a/349253
    filtered_traffic = traffic_df.query("interval_begin <= @time_slide <= interval_end")
    filtered_traffic = filtered_traffic.filter(items=["edge_id", column_filter])

    # Allow the user to inspect the data (to be sure).
    with st.container():
        st.subheader("Data inspection")
        col1, col2, col3 = st.columns(3)
        col1.metric("Traffic #", len(traffic_df))
        col2.metric("Geojson #", len(geo_df))
        col3.metric("Timestamp #", len(filtered_traffic))
        with st.expander("See the filtered column's contents"):
            st.write(filtered_traffic)

    # 3. Merge the filtered data INTO the GeoDataFrame.
    assert "edge_id" in filtered_traffic.columns
    __merged_df: pd.DataFrame = geo_df.merge(
        filtered_traffic, left_on="id", right_on="edge_id", how="left"
    )
    merged_gdf: gpd.GeoDataFrame = gpd.GeoDataFrame(__merged_df)
    del __merged_df  # Save some space in memory.

    # Load and display the map.
    map_1: KeplerGl = KeplerGl(height=600)
    map_1.add_data(merged_gdf, "Traffic data")
    with st.container():
        st.header("Map")
        keplergl_static(map_1, center_map=True)
        st.info(KEPLER_WORKAROUND.format(col=column_filter), icon=INFO_ICON)

else:
    with st.container():
        st.header("Visualisation")
        st.info("Nothing uploaded. Please load a file to run the visualisations.", icon=INFO_ICON)
