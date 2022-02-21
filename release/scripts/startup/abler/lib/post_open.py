from typing import Optional
import bpy
from .tracker import tracker
from ..custom_properties import AconSceneProperty


def tracker_file_open() -> Optional[bool]:

    # tracking file_open
    if bpy.data.filepath != "":
        tracker.file_open()
        return True


def change_and_reset_value() -> None:

    properties = AconSceneProperty.__annotations__
    for property in properties:
        original_value = getattr(bpy.context.scene.ACON_prop, property)
        if type(original_value) == float or type(original_value) == int:
            setattr(bpy.context.scene.ACON_prop, property, 0)
            setattr(bpy.context.scene.ACON_prop, property, original_value)
