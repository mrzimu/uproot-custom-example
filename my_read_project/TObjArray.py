from array import array

import awkward.contents
import awkward.forms
import awkward.index
import numpy as np
from uproot_custom import Factory, build_factory
from uproot_custom.readers.python import IReader

from . import cpp


class TObjArrayReader(IReader):
    def __init__(self, name: str, element_reader: IReader):
        super().__init__(name)
        self.element_reader = element_reader
        self.offsets = array("q", [0])

    def read(self, stream):
        # Read TObjArray header
        stream.skip_fNBytes()
        stream.skip_fVersion()
        stream.skip_TObject()
        stream.read_TString()  # fName
        fSize = stream.read_uint32()
        stream.skip(4)  # fLowerBound

        # Record the new offset
        self.offsets.append(self.offsets[-1] + fSize)

        # Read the elements using the element reader
        self.element_reader.read_many(stream, fSize)

    def data(self):
        offsets_array = np.asarray(self.offsets)
        element_data = self.element_reader.data()
        return offsets_array, element_data


class TObjArrayFactory(Factory):
    """
    This factory reads `TObjArray` with only `TObjInObjArray` elements.
    The definition is on [here](https://github.com/mrzimu/uproot-custom/blob/main/example/gen-demo-data/include/TObjInObjArray.hh)
    """

    @classmethod
    def priority(cls):
        """
        Set a higher priority to ensure this factory is chosen first,
        otherwise the pre-defined factory of `uproot-custom` may be selected.

        The default priority is 10 for other factories.
        """
        return 50

    @classmethod
    def build_factory(
        cls,
        top_type_name: str,
        cur_streamer_info: dict,
        all_streamer_info: dict,
        item_path: str,
        **kwargs,
    ):
        # `top_type_name` is the type name of the top-level object.
        if top_type_name != "TObjArray":
            return None

        # `item_path` is the path of the current item being processed.
        # Since `TObjArray` is designed to store any object, we can adjust the `item_path`
        # to point to the actual object type stored in the array.
        item_path = item_path.replace(".TObjArray*", "")
        obj_typename = "TObjInObjArray*"
        element_factory = build_factory(
            cur_streamer_info={
                "fName": obj_typename,
                "fTypeName": obj_typename,
            },
            all_streamer_info=all_streamer_info,
            item_path=f"{item_path}.{obj_typename}",
        )

        return cls(name=cur_streamer_info["fName"], element_factory=element_factory)

    def __init__(self, name: str, element_factory: Factory):
        super().__init__(name)

        # Store the element factory, so that we can use it to build C++ reader,
        # and create Awkward content/form for the elements.
        self.element_factory = element_factory

    def build_cpp_reader(self):
        # Build the C++ reader for the elements first.
        element_reader = self.element_factory.build_cpp_reader()

        # Combine the element reader into the TObjArray reader.
        return cpp.TObjArrayReader(self.name, element_reader)

    def build_python_reader(self):
        # Build the Python reader for the elements first.
        element_reader = self.element_factory.build_python_reader()

        # Combine the element reader into the TObjArray reader.
        return TObjArrayReader(self.name, element_reader)

    def make_awkward_content(self, raw_data):
        # Receive the raw data from `TObjArrayReader`,
        # extract offsets and element raw data.
        offsets, element_raw_data = raw_data

        # Build the element content using the element factory.
        element_content = self.element_factory.make_awkward_content(element_raw_data)

        # Construct and return the ListOffsetArray.
        # Note that `AnyPointerFactory` returns `IndexedOptionArray` to represent nullptr
        # and duplicate objects. But we're quite sure that there will be no nullptr here
        # and all objects are unique, so we extract the content directly here.
        return awkward.contents.ListOffsetArray(
            awkward.index.Index64(offsets),
            element_content.content,
        )

    def make_awkward_form(self):
        # Build the element form using the element factory.
        element_form = self.element_factory.make_awkward_form()

        # Construct and return the ListOffsetForm.
        return awkward.forms.ListOffsetForm(
            "i64",
            element_form.content,
        )
