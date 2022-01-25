import bpy
from .tracker import tracker


def tracker_file_open():

    # tracking file_open
    if bpy.data.filepath != "":
        tracker.file_open()
        return True


def change_and_reset_value():
    # 아무 씬 값이나 변경했다가 다시 리셋
    original_value = bpy.data.scenes["Scene"].ACON_prop.edge_min_line_width
    bpy.data.scenes["Scene"].ACON_prop.edge_min_line_width = 0
    bpy.data.scenes["Scene"].ACON_prop.edge_min_line_width = original_value
