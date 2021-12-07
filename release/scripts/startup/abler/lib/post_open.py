import bpy
from .tracker import tracker


def tracker_file_open():

    # tracking file_open
    if bpy.data.filepath != "":
        tracker.file_open()
