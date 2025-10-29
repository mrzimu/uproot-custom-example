import uproot_custom

from .OverrideStreamerFactory import OverrideStreamerFactory
from .TObjArrayFactory import TObjArrayFactory

# Register the custom factories so that `uproot-custom` can find them
uproot_custom.registered_factories.add(OverrideStreamerFactory)
uproot_custom.registered_factories.add(TObjArrayFactory)

# Specify which branches the `uproot-custom` should be applied to
uproot_custom.AsCustom.target_branches |= {
    "/my_tree:override_streamer",
    "/my_tree:obj_with_obj_array/m_obj_array",
}
