# Standard library.
import os.path

# Dependencies
import streamlit as st

# Local.
from util.texts import ABOUT_HOMEPAGE

# Setup.
# Load the demo data dir into the session state.
st.session_state.demo_data = {
    "network": os.path.join(".", "demo_data", "geojson_files", "network.geojson"),
    "taz": os.path.join(".", "demo_data", "geojson_files", "traffic_analysis_zones.geojson"),
    "od_matrix_dir": os.path.join(".", "demo_data", "od_matrix"),  # To traverse all sample files.
    "edge_csv": os.path.join(".", "demo_data", "xml_files", "edge_data_3600.csv"),
    "edge_xml": os.path.join(".", "demo_data", "xml_files", "edge_data_3600.xml"),  # Unused.
    "routes": os.path.join(".", "demo_data", "xml_files", "routes_sample.xml"),
    "trips": os.path.join(".", "demo_data", "xml_files", "trips.trips.xml"),
}

# The actual streamlit page!
# Set a page title.
st.set_page_config(
    page_title="SUMO Visualisation dashboard!",
    page_icon=":blue_car:",
    # layout="wide",
)

# Static information. The container makes it an isolated "section".
with st.container():
    st.title("SUMO Online dashboard")
    st.subheader("Homepage")

# Homepage info.
st.write(ABOUT_HOMEPAGE)
