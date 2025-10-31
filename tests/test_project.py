from pathlib import Path

import uproot

import my_reader

tree = uproot.open(Path(__file__).parent / "demo-data.root")["my_tree"]


def test_override_streamer():
    tree["override_streamer"].arrays()


def test_tobjarray():
    tree["obj_with_obj_array"].arrays()
