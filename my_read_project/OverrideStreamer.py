import array

import awkward.contents
import awkward.forms
import numpy as np
from uproot_custom import Factory
from uproot_custom.readers.python import IReader

from . import cpp


class OverrideStreamerReader(IReader):
    def __init__(self, name):
        super().__init__(name)
        self.m_ints = array.array("i")  # int32
        self.m_doubles = array.array("d")  # float64

    def read(self, buffer):
        # Skip TObject header
        buffer.skip_TObject()

        # Read integer value
        self.m_ints.append(buffer.read_int32())

        # Read a custom added mask value
        mask = buffer.read_uint32()
        if mask != 0x12345678:
            raise RuntimeError(f"Error: Unexpected mask value: {mask:#x}")

        # Read double value
        self.m_doubles.append(buffer.read_double())

    def data(self):
        int_array = np.asarray(self.m_ints)
        double_array = np.asarray(self.m_doubles)
        return int_array, double_array


class OverrideStreamerFactory(Factory):
    """
    This factory handles the TOverrideStreamer class.
    """

    @classmethod
    def build_factory(
        cls,
        top_type_name: str,
        cur_streamer_info: dict,
        all_streamer_info: dict,
        item_path: str,
        **kwargs,
    ):
        """
        Decides whether to use this factory based on the streamer info.

        In this method, we check if the current streamer name or `top_type_name` is `TOverrideStreamer`.
        """
        fName = cur_streamer_info["fName"]
        if fName != "TOverrideStreamer" and top_type_name != "TOverrideStreamer":
            return None

        # Use `Factory`'s constructor to create an instance of this factory.
        # The constructor requires the factory name as an argument.
        return cls(fName)

    def build_cpp_reader(self):
        """
        Instantiate the C++ reader with factory name.
        """
        return cpp.OverrideStreamerReader(self.name)

    def build_python_reader(self):
        """
        Instantiate the Python reader with factory name.
        """
        return OverrideStreamerReader(self.name)

    def make_awkward_content(self, raw_data):
        """
        Transform the raw data returned from C++ reader into an Awkward RecordArray.

        The raw data is expected to be a tuple of two arrays: an integer array and a double array.

        Users can customize their C++ reader to return different data structures as needed.
        """
        int_array, double_array = raw_data

        return awkward.contents.RecordArray(
            [
                awkward.contents.NumpyArray(int_array),
                awkward.contents.NumpyArray(double_array),
            ],
            ["m_int", "m_double"],
        )

    def make_awkward_form(self):
        """
        Define the Awkward form for the data structure.

        The form should match the structure created in `make_awkward_content`.
        """
        return awkward.forms.RecordForm(
            [
                awkward.forms.NumpyForm("int32"),
                awkward.forms.NumpyForm("float64"),
            ],
            ["m_int", "m_double"],
        )
