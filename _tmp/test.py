import uproot

import my_reader

tree = uproot.open(
    "/home/mrli/work/workarea-uproot-custom/uproot-custom-example/tests/demo-data.root"
)["my_tree"]

tree["override_streamer/m_obj"].array()
