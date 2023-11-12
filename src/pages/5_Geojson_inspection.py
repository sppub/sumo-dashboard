# Dependencies.
import geopandas as gpd
import streamlit as st
from keplergl import KeplerGl
from streamlit.runtime.uploaded_file_manager import UploadedFile  # For type checking.
from streamlit_keplergl import keplergl_static

# Local.
from util.texts import ABOUT_INSPECTION_PAGE, INFO_ICON, UPLOAD_INFO


# Functions.
@st.cache_data
def get_default_geojson() -> gpd.GeoDataFrame:
    demo_paths_dict = st.session_state.demo_data
    # Assert that the right values is in config.
    ret_df = gpd.read_file(demo_paths_dict["network"])
    return ret_df


@st.cache_data
def get_geojson_from_file(file: UploadedFile) -> gpd.GeoDataFrame:
    ret_df = gpd.read_file(file)
    return ret_df


# Streamlit.
with st.container():
    st.title("GeoJSON inspection using Kepler")
    st.write(ABOUT_INSPECTION_PAGE)
    st.divider()

geo_df: gpd.GeoDataFrame | None = None

# Allow the user to upload their own file, if they want to.
# Otherwise, use the default file (in the config) for demo purposes.
st.write(UPLOAD_INFO)
use_demo_files_5: bool = st.checkbox("Try out the demo files", value=False)

if use_demo_files_5:  # Use config! Config is embedded into the session state.
    geo_df = get_default_geojson()
else:  # User files needed.
    st.header("File upload")
    st.write("Please select the files you want to visualise.")
    geojson_file: UploadedFile = st.file_uploader(
        "Upload your network .geojson file here", type="geojson"
    )
    if geojson_file:
        geo_df = get_geojson_from_file(geojson_file)


# Try to create map if a GeoDataFrame is loaded.
if isinstance(geo_df, gpd.GeoDataFrame):
    # Show some basic data about the dataframe.
    with st.container():
        st.header("Data inspection")
        st.subheader("What the data looks like")
        st.write(
            "The data is converted to a GeoDataFrame, which makes it easier to inspect and process."
        )
        # Sadly, this is not (yet) possible to show using st.dataframe() or st.table().
        # See: https://github.com/streamlit/streamlit/issues/1002
        st.write(geo_df.head())
        st.subheader("Some basic properties")
        st.write(f"- Amount of items in file: **{len(geo_df)}**")
        if "type" in geo_df:
            st.write(
                "- Geo types in file:\n"
                + "\n".join(f"    - `{t}`" for t in sorted(set(geo_df["type"])))
            )

    map_1: KeplerGl = KeplerGl(height=600)
    map_1.add_data(geo_df, "Network")
    with st.container():
        st.header("Visualisation")
        keplergl_static(map_1, center_map=True)

else:
    with st.container():
        st.header("Visualisation")
        st.info("Nothing uploaded. Please load a file to run the visualisations.", icon=INFO_ICON)
