import awkward.contents
import awkward.forms
import awkward.index

from uproot_custom import (
    Factory,
    build_factory,
)
from uproot_custom.factories import AnyClassFactory, ObjectHeaderFactory

from .my_reader_cpp import TObjArrayReader


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
        obj_typename = "TObjInObjArray"

        # `all_streamer_info` contains the streamer info of all classes.
        # We retrieve the members of `TObjInObjArray`, and build sub-factories for them.
        sub_factories = []
        for s in all_streamer_info[obj_typename]:
            sub_factories.append(
                build_factory(
                    cur_streamer_info=s,
                    all_streamer_info=all_streamer_info,
                    item_path=f"{item_path}.{obj_typename}",  # Adjust the item path accordingly
                )
            )

        # Objects stored in `TObjArray` have such a format:
        # - TObjArray header (contains size info)
        #   * Object 1: [ObjectHeader, Member1, Member2, ...]
        #   * Object 2: [ObjectHeader, Member1, Member2, ...]
        #   * ...
        #
        # Therefore, we first create an `AnyClassFactory` for the object's members,
        # then wrap it with an `ObjectHeaderFactory` to include the object header.
        # Finally, we create the `TObjArrayFactory` to read objects in a loop.
        return cls(
            name=cur_streamer_info["fName"],
            element_factory=ObjectHeaderFactory(
                name=obj_typename,
                element_factory=AnyClassFactory(
                    name=obj_typename,
                    sub_factories=sub_factories,
                ),
            ),
        )

    def __init__(self, name: str, element_factory: Factory):
        super().__init__(name)

        # Store the element factory, so that we can use it to build C++ reader,
        # and create Awkward content/form for the elements.
        self.element_factory = element_factory

    def build_cpp_reader(self):
        # Build the C++ reader for the elements first.
        element_reader = self.element_factory.build_cpp_reader()

        # Combine the element reader into the TObjArray reader.
        return TObjArrayReader(self.name, element_reader)

    def make_awkward_content(self, raw_data):
        # Receive the raw data from `TObjArrayReader`,
        # extract offsets and element raw data.
        offsets, element_raw_data = raw_data

        # Build the element content using the element factory.
        element_content = self.element_factory.make_awkward_content(element_raw_data)

        # Construct and return the ListOffsetArray.
        return awkward.contents.ListOffsetArray(
            awkward.index.Index64(offsets),
            element_content,
        )

    def make_awkward_form(self):
        # Build the element form using the element factory.
        element_form = self.element_factory.make_awkward_form()

        # Construct and return the ListOffsetForm.
        return awkward.forms.ListOffsetForm(
            "i64",
            element_form,
        )
