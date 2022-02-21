from typing import Optional
import bpy
from .tracker import tracker


def tracker_file_open() -> Optional(bool):

    # tracking file_open
    if bpy.data.filepath != "":
        tracker.file_open()
        return True


def change_and_reset_value() -> None:

    # line update
    original_value = bpy.context.scene.ACON_prop.edge_min_line_width
    bpy.context.scene.ACON_prop.edge_min_line_width = 0
    bpy.context.scene.ACON_prop.edge_min_line_width = original_value

    # sun update
    original_value = bpy.context.scene.ACON_prop.sun_strength
    bpy.context.scene.ACON_prop.sun_strength = 1.0
    bpy.context.scene.ACON_prop.sun_strength = original_value
