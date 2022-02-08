import bpy
from .tracker import tracker


def tracker_file_open():

    # tracking file_open
    if bpy.data.filepath != "":
        tracker.file_open()
        return True


def change_and_reset_value():
    original_value = bpy.data.scenes["Scene"].ACON_prop.edge_min_line_width
    bpy.data.scenes["Scene"].ACON_prop.edge_min_line_width = 0
    bpy.data.scenes["Scene"].ACON_prop.edge_min_line_width = original_value
