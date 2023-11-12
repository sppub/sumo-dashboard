# Standard library.
import csv
import json
import os.path
from collections import defaultdict
from io import StringIO
from textwrap import dedent
from typing import TextIO
from xml.dom import minidom

# Dependencies
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Custom types (to make the types also self-documenting).
TAZ = int
SOURCE_TAZ = TAZ
TARGET_TAZ = TAZ


class ODMatrix:
    """Hold the properties of an OD-Matrix file."""

    PRINT_FORMAT = dedent(
        """
        --- Origin-destination matrix ---
        {header}
        * From-Time  To-Time 
        {start} {end} 
        * Factor 
        {factor}
        * Data rows in file
        {row_count}
        * Total movements
        {movement_count}"""
    )

    file_header: str | None = None
    start: float | None = None
    end: float | None = None
    factor: float | None = None
    counts: dict[tuple[SOURCE_TAZ, TARGET_TAZ], int] | None = None
    # upscaling_factor: float | None = None

    def __init__(self):
        pass

    def load_from_filepath(self, filepath: os.PathLike | str):
        assert os.path.exists(filepath)
        # csv_rf: TextIO
        with open(filepath, "r", newline="", encoding="utf8") as csv_rf:
            self.read_matrix(csv_rf)

    def load_from_streamlit_file(self, uploaded_file: UploadedFile):
        string_io = StringIO(uploaded_file.getvalue().decode("utf-8"))
        self.read_matrix(string_io)

    def read_matrix(self, csv_rf: TextIO | StringIO):
        """Read the OD-Matrices as provided by SUMO"""
        # First 5 lines are header-like.
        self.file_header = csv_rf.readline().rstrip("\n")
        csv_rf.readline()  # "From-time, to-time", ignore input.
        line_3 = csv_rf.readline()
        # We expect two float values depicting the time (??), store them
        line_3l, line_3r = line_3.split()  # Split on whitespace.
        self.start = float(line_3l)
        self.end = float(line_3r)
        csv_rf.readline()  # "Factor", ignore input.
        # Finally, we store the factor.
        line_5 = csv_rf.readline()
        self.factor = float(line_5)
        # Now that the "header bit" is done, read the rest of the rows in a csv-like manner.
        result_dict: dict[(int, int), int] = {}
        csv_reader = csv.reader(csv_rf, delimiter=" ")
        for row in csv_reader:
            _source, _target, _count = row
            source = int(_source)
            target = int(_target)
            count = int(_count)
            result_dict[(source, target)] = count
        # Finally, after all rows are read, assign result dict to counts.
        self.counts = result_dict

    def get_row_count(self) -> int:
        return len(self.counts)

    def get_movement_count(self) -> int:
        return sum(self.counts.values())

    def __str__(self) -> str:
        """Read the class info"""
        return self.PRINT_FORMAT.format(
            header=self.file_header,
            start=self.start,
            end=self.end,
            factor=self.factor,
            row_count=self.get_row_count(),
            movement_count=self.get_movement_count(),
        )

    def __dict__(self) -> dict[tuple[SOURCE_TAZ, TARGET_TAZ], int]:
        return self.counts

    def to_json(self) -> str:
        """Convert the OD-Matrix into a json for easy further processing

        Example JSON format
        -------------------
        ```json
        {
          "header": "$OR;D2 ",
          "time_from": 5.0,
          "time_to": 6.0,
          "factor": 1.0,
          "distinct_path_count": 5256,
          "movement_count": 20438,
          "od_matrix": {
            "783176708": {
              "9162004": 153,
              "9162115": 55,
              ...
            },
            "783095006": {
              "9162119": 85,
              "9162004": 55,
              "9162115": 63,
              ...
            }
        }
        ```

        Returns
        -------
        str
            A json-formatted string with the basic OD config, as well as the OD matrix.
        """
        # (1) Store basic info.
        json_base_dict: dict = {
            "header": self.file_header,
            "time_from": self.start,
            "time_to": self.end,
            "factor": self.factor,
            "distinct_path_count": self.get_row_count(),
            "movement_count": self.get_movement_count(),
        }
        # (2) Convert counts to json-friendly format. Reason: json does not support tuple keys.
        # Format: {origin: {destination: count}}
        json_od_counts: dict[SOURCE_TAZ, dict[TARGET_TAZ, int]] = defaultdict(dict)
        for (origin, destination), count in self.counts.items():
            json_od_counts[origin][destination] = count
        # (3) Add OD counts to base dict, and return that.
        json_base_dict["od_matrix"] = json_od_counts
        return json.dumps(json_base_dict, indent=2)


class Trip:
    """Wrapper around trip"""

    PRINT_FORMAT = dedent(
        """
        --- Trip {trip_id} information ---
        Route:     {s} -> {t}
        TAZ  :     {s_taz} -> {t_taz}
        Departure: {depart}
        """
    )

    def __init__(
        self,
        trip_id: int,
        depart_stamp: float,
        source: str,
        target: str,
        source_taz: SOURCE_TAZ,
        target_taz: TARGET_TAZ,
    ):
        self.id = trip_id
        self.depart_stamp = depart_stamp
        self.source_str = source
        self.target_str = target
        self.source_taz = source_taz
        self.target_taz = target_taz

    def __str__(self) -> str:
        """Get a string representation of a trip"""
        return self.PRINT_FORMAT.format(
            trip_id=self.id,
            s=self.source_taz,
            t=self.target_str,
            s_taz=self.source_taz,
            t_taz=self.target_taz,
            depart=self.depart_stamp,
        )

    def __dict__(self) -> dict[str, str | int | float]:
        """Represent the trip in a dict"""
        return {
            "id": self.id,
            "depart": self.depart_stamp,
            "from": self.source_str,
            "to": self.target_str,
            "from_taz": self.source_taz,
            "to_taz": self.target_taz,
        }

    def to_json(self) -> str:
        """Represent the trip in json"""
        dict_rep = self.__dict__()
        return json.dumps(dict_rep, indent=2)

    @classmethod
    def from_xml_element(cls, trip: minidom.Element):
        _id = trip.attributes["id"].value
        trip_id = _id
        _depart = trip.attributes["depart"].value
        stamp = float(_depart)
        _from = trip.attributes["from"].value
        _to = trip.attributes["to"].value
        _fromtaz = trip.attributes["fromTaz"].value
        from_taz = int(_fromtaz)
        _totaz = trip.attributes["toTaz"].value
        to_taz = int(_totaz)
        return cls(trip_id, stamp, _from, _to, from_taz, to_taz)


# Debug utilities.
def read_trips_xml(demo_data_dir: os.PathLike | str):
    trips_fp = os.path.join(demo_data_dir, "xml_files", "trips.trips.xml")

    print("parsing xml...")
    xml_obj: minidom.Document = minidom.parse(trips_fp)
    # print(type(xml_obj))
    trip: minidom.Element
    n: int = 0
    print("processing trip data...")
    for trip in xml_obj.getElementsByTagName("trip"):
        # print(type(trip))
        # print("---")
        trip_obj = Trip.from_xml_element(trip)
        print(trip_obj)
        print(trip_obj.to_json())
        # print(dir(trip.attributes))
        # print(type(trip.attributes))
        # print(trip.attributes["to"].value)
        # print(trip.attributes["toTaz"].value)
        n += 1
        if n == 10:
            break


def print_munich_od_summary(demo_data_dir: os.PathLike | str):
    """Print the summary of each OD file in the calibration repo"""
    od_dir = os.path.join(demo_data_dir, "od_matrix")
    for filename in sorted(os.listdir(od_dir)):
        od_path = os.path.join(od_dir, filename)
        od_class = ODMatrix()
        od_class.load_from_filepath(od_path)
        print(od_class)
        print(od_class.to_json())


def print_trips(demo_data_dir: os.PathLike | str):
    read_trips_xml(demo_data_dir)


if __name__ == "__main__":
    this_dir = os.path.dirname(os.path.realpath(__file__))
    sample_dir = os.path.join(this_dir, "..", "..", "demo_data")

    print("welcome!")
    show_trips: bool = True
    if show_trips:
        print_trips(sample_dir)
    else:
        print_munich_od_summary(sample_dir)
    print("done!")
