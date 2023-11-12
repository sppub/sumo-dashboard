# Standard library.
from os import listdir
import os.path
from collections import Counter

# Dependencies.
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib.colors import LogNorm
from streamlit.runtime.uploaded_file_manager import UploadedFile  # For type checking.

# Local.
from util.sumo_conversions import ODMatrix
from util.texts import ABOUT_INPUT_PAGE, UPLOAD_INFO_OD, INFO_ICON


# ISSUE: Caching data does not work, likely because it is a custom data type.
# @st.cache_data
def load_user_od(file: UploadedFile) -> ODMatrix:
    """
    Create an O/D Matrix object and fill it based on the file input.
    Basically wraps the logic into a function such that it can be cached.

    Parameters
    ----------
    file
      The O/D Matrix file (uploaded through Streamlit) to process

    Returns
    -------
    ODMatrix
      An ODMatrix object, which can provide several statistics related to the O/D Matrix.
    """
    to_return = ODMatrix()
    to_return.load_from_streamlit_file(file)
    return to_return


# @st.cache_data
def load_config_od(filepath: os.PathLike | str) -> ODMatrix:
    """
    Create an O/D Matrix object and fill it based on the file input.
    Basically wraps the logic into a function such that it can be cached.

    Parameters
    ----------
    filepath
      The path to the O/D Matrix file to process

    Returns
    -------
    ODMatrix
      An ODMatrix object, which can provide several statistics related to the O/D Matrix.
    """
    to_return = ODMatrix()
    to_return.load_from_filepath(filepath)
    return to_return


# Streamlit.
state = st.session_state

with st.container():
    st.title("Origin-Destination matrix inspection")
    st.write(ABOUT_INPUT_PAGE)
    st.divider()
    st.write(UPLOAD_INFO_OD)
    use_demo_files_1: bool = st.checkbox("Try out the demo files", value=False)

od_obj: ODMatrix | None
if use_demo_files_1:
    # Load the directory of OD-matrices. Dir has several files, put them in a radio.
    od_dir = st.session_state.demo_data["od_matrix_dir"]
    # List all the files in the directory.
    files = sorted(listdir(od_dir))
    with st.container():
        st.header("File selection")
        st.write("Please select one of the filenames below to inspect its data!")
        od_filename = st.radio(label="Try out any O/D matrix below:", options=files, index=0)
    od_fp = os.path.join(od_dir, od_filename)
    # Load the file from config (based on the filepath).
    od_obj = load_config_od(od_fp)

else:
    with st.container():
        st.header("File upload")
        st.write("Please upload the Origin-Destination Matrix (OD-Matrix) to inspect!")
        od_file = st.file_uploader("Upload your trips file here", type="txt")

    if od_file:  # Load the file class
        od_obj = load_user_od(od_file)
    else:
        od_obj = None

st.header("File overview")
if od_obj:
    with st.container():
        st.subheader("Summary data")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total rows", od_obj.get_row_count())
        col2.metric("Total movements", od_obj.get_movement_count())
        col3.metric("Scale factor", od_obj.factor)

    # Try to display most common and least common trips.
    with st.expander("10 most common origin-destination pairs"):
        test_counter = Counter(od_obj.counts)
        test_df = pd.DataFrame(
            (
                (from_taz, to_taz, count)
                for (from_taz, to_taz), count in test_counter.most_common(10)
            ),
            columns=["Origin TAZ", "Destination TAZ", "Trip count"],
        )
        st.dataframe(test_df.style.format(thousands=None, precision=0))

    # Make a heatmap.
    # Transform the data to something Seaborn-friendly.
    # Thanks to: https://stackoverflow.com/a/33712480
    fig: plt.Figure = plt.figure(figsize=(9, 7))
    ser = pd.Series(
        list(od_obj.counts.values()), index=pd.MultiIndex.from_tuples(od_obj.counts.keys())
    )
    df: pd.DataFrame = ser.unstack().fillna(0)
    # Configure colour to deal with empty slots.
    # With the help of: https://stackoverflow.com/a/58185087
    colour = plt.get_cmap()
    colour.set_bad("black")  # If the value is bad, the colour will be black instead of transparent.
    # Set the heatmap itself
    plt.title("Origin-Destination Heatmap")
    ax = sns.heatmap(df, norm=LogNorm(), cmap=colour)
    # Now, display it in Streamlit.
    with st.container():
        st.subheader("Origin-Destination Heatmap")
        st.pyplot(fig)

else:
    st.info("Please select a file above to see the rest!", icon=INFO_ICON)
