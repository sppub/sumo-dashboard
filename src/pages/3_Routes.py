# Dependencies.
import geopandas as gpd
import pandas as pd
import streamlit as st
from keplergl import KeplerGl
from streamlit_keplergl import keplergl_static
from streamlit.runtime.uploaded_file_manager import UploadedFile  # For type checking.

# Local.
from util.texts import WARNING_ICON, ABOUT_ROUTES_PAGE, UPLOAD_INFO


# Functions.
def get_edge_list(df_in: pd.DataFrame, index: int) -> list[str]:
    """
    Convert a route in a DataFrame in a list of strings.

    Parameters
    ----------
    df_in
      The DataFrame out of which to obtain the route. Must have a column named 'edges'.
    index
     The index of the route of interest

    Returns
    -------
    list[str]
        the list of str corresponding to the edge IDs, in the order they are traversed in the route.
    """
    assert index in df_in.index, f"Index {index} not present in DataFrame!"
    assert "edges" in df_in.columns, "No 'edges' column in DataFrame!"
    # Get the chosen route from the DataFrame.
    chosen_route = df_in.iloc[index]
    route_str: str = chosen_route.edges  # Format: "366601213 366601213-AddedOffRampEdge 79395068"
    # Split route by spaces to get an array.
    route_list = route_str.split()
    return route_list


@st.cache_data
def get_geojson_from_config() -> gpd.GeoDataFrame:
    demo_paths_dict = st.session_state.demo_data
    ret_df = gpd.read_file(demo_paths_dict["network"])
    return ret_df


@st.cache_data
def get_geojson_from_file(file: UploadedFile) -> gpd.GeoDataFrame:
    ret_df = gpd.read_file(file)
    return ret_df


@st.cache_data
def get_routes_from_config(xpath: str | None) -> pd.DataFrame:
    """
    Get the routes from config, and convert them into a GeoDataFrame
    """
    demo_paths_dict = st.session_state.demo_data
    xml_fp = demo_paths_dict["routes"]
    # The code currently forces the 'route' inside the XML using an XPath query.
    ret_df = pd.read_xml(xml_fp, xpath=xpath) if xpath else pd.read_xml(xml_fp)
    return ret_df


@st.cache_data
def get_routes_from_file(file: UploadedFile, xpath: str | None) -> pd.DataFrame:
    """
    Get the routes from config, and convert them into a GeoDataFrame
    """
    # The code currently forces the 'route' inside the XML using an XPath query.
    ret_df = pd.read_xml(file, xpath=xpath) if xpath else pd.read_xml(file)
    return ret_df


# Streamlit.
state = st.session_state

with st.container():
    st.title("Individual route analysis")
    st.write(ABOUT_ROUTES_PAGE)
    st.divider()
    st.write(UPLOAD_INFO)
    use_demo_files_3: bool = st.checkbox("Try out the demo files", value=False)

base_network_gj: gpd.GeoDataFrame | None = None
route_header_df: pd.DataFrame | None = None
if use_demo_files_3:
    base_network_gj = get_geojson_from_config()
    # Heavy instruction.
    # 'set_index("id")' sets the IDs in the .xml file as the DataFrame index.
    route_header_df = get_routes_from_config(xpath=None).set_index("id")
    assert base_network_gj is not None
    assert route_header_df is not None
else:
    with st.container():
        st.header("File upload")
        st.warning(
            "**WARNING:** The (xml) files that are processed on this page are usually *large*, "
            "which also means that processing these files can take up a lot of memory. \n\n"
            "Please verify that your available memory is several times larger than the "
            "file you are trying to process!",
            icon=WARNING_ICON,
        )
        st.write("Please select the files you want to visualise.")
        xml_file: UploadedFile = st.file_uploader("Upload your trips file here", type="xml")
        geojson_file: UploadedFile = st.file_uploader(
            "Upload your **network** `.geojson` file here", type="geojson"
        )
    if xml_file:
        # Heavy instruction.
        # 'set_index("id")' sets the IDs in the .xml file as the DataFrame index.
        route_header_df = get_routes_from_file(xml_file, xpath=None).set_index("id")
    if geojson_file:
        base_network_gj = get_geojson_from_file(geojson_file)

# Both files need to be uploaded for the remainder to work.
if route_header_df is not None:
    # Inspections.
    st.header("Data inspection")
    if base_network_gj is not None:  # Only inspect network file if it is uploaded.
        with st.expander("Inspect network file"):
            st.write("First lines of network data")
            st.write(base_network_gj.head())

    with st.expander("Inspect routes"):
        head_len = 100
        st.write(f"First {head_len} routes")
        # 140 581 trips in test data.
        # FIXME: Change thousands separator.
        st.write(route_header_df[:head_len])

    # TODO: allow users to filter on departure and destination TAZ.

    # Route selection.
    # Allow user to pick a route of choice.
    # In code: get the index of the header dataframe as sorted list.
    #  Then, present them as such to the user.
    id_list = sorted(route_header_df.index.to_list())
    id_count = len(id_list)

    with st.container():
        st.header("Route selection")
        st.write("Please select the route you wish to analyse.")
        if len(id_list) > 10_000:
            st.warning(
                f"There are many trips ({id_count}), so this selection box may be slow to respond.",
                icon=WARNING_ICON,
            )
        chosen_route_id = st.selectbox("Which route?", options=id_list)

    # Now that a route ID is chosen, display that route!
    chosen_route_query = f"/routes/vehicle[@id='{chosen_route_id}']//route"

    with st.container():
        st.header("Route analysis")
        st.subheader("General route information")
        st.write(
            "This table depicts some basic information about the route, such as the departure time."
        )
        chosen_route_header = route_header_df.loc[chosen_route_id]
        st.table(chosen_route_header)
        st.subheader("Route details")
        st.write(
            "Depending on the trip, a vehicle may be rerouted at some point. "
            "In those cases, you can choose which route you would like to see visualised.\n"
            "The route where everything but `edges` is equal to `None` is the original route."
        )
        st.write(f"Performing query: `{chosen_route_query}`")
        chosen_route_df = get_routes_from_config(xpath=chosen_route_query)
        st.write(chosen_route_df)

    # Most of the time there is only one route, but sometimes there are multiple options.
    # In the case there is multiple options, the user must pick the route they wish to visualise.
    vis_all: bool  # Whether >1 route is visualised. Always False if there's only one route.
    # The index within chosen_route_df to be visualised. Will not be used if vis_all is True.
    route_to_vis: int

    option_count = len(chosen_route_df)
    if option_count > 1:  # Multiple route options.
        st.subheader("Route alternative selection")
        st.write(
            f"There are {option_count} different options for this route. "
            f"Please select which one you want to visualise, or choose to visualise all."
        )
        # Ask the user if they want to visualise all routes, or only a specific one.
        vis_all = st.checkbox("Visualise all routes", value=False)
        # Let the user pick a main route if not all routes are to be visualised.
        # Note: this also yields an int if disabled=True!
        route_to_vis: int = st.radio(
            label="Select the main route to visualise",
            index=option_count - 1,
            options=range(option_count),
            format_func=lambda x: f"Route {x}",
            disabled=vis_all,
        )

    else:  # One route.
        st.write("Only one route. Expand the box below to inspect all edges.")
        vis_all = False
        route_to_vis: int = 0

    if base_network_gj is not None:
        # Create a map.
        map_1: KeplerGl = KeplerGl(height=600)

        if vis_all:
            # Traverse the option indices in reverse order,
            #  such that the 'initial' route is the top layer.
            for i in reversed(range(option_count)):
                i_edge_list = get_edge_list(chosen_route_df, route_to_vis)
                i_route_gj = base_network_gj.query("id in @i_edge_list")
                map_1.add_data(i_route_gj, f"Route {i}")

        else:  # Get the edges of the intended route.
            edge_list = get_edge_list(chosen_route_df, route_to_vis)
            with st.expander("See edges of route", expanded=False):
                st.write(edge_list)
            route_gj = base_network_gj.query("id in @edge_list")
            map_1.add_data(route_gj, "Selected trip")

        # Time to visualise!
        with st.container():
            st.subheader("Route visualisation")
            add_full_network: bool = st.checkbox("Also show full network", value=False)

        # Load and display the map.
        if add_full_network:  # Load full network last (if wanted).
            map_1.add_data(base_network_gj, "Full network")
        with st.container():
            keplergl_static(map_1, center_map=True)
    else:
        st.warning("To visualise the route on a map, we need a network `.geojson` file!")
else:  # Without the route_header_df, nothing can be processed.
    st.warning("Please upload an XML file, or use the demo files!")
