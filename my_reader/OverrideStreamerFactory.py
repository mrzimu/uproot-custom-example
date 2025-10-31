import awkward.contents
import awkward.forms

from uproot_custom import Factory

from .my_reader_cpp import OverrideStreamerReader


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
