from typing import Optional
import bpy
from bpy.types import (
    Scene,
    Context,
    Object,
    PropertyGroup,
    FloatProperty,
)


def changeCubeLocation(self, context: Context) -> None:
    obj_name = "Simple Cube"
    cube_obj: Optional[Object] = bpy.data.objects.get(obj_name)

    if obj_name in bpy.data.objects:
        prop: PropertyGroup = context.scene.ACON_prop
        cube_obj.location.x = round(prop.cube_location_x, 2)
        cube_obj.location.y = round(prop.cube_location_y, 2)
        cube_obj.location.z = round(prop.cube_location_z, 2)


def changeCubeScale(self, context: Context) -> None:
    obj_name = "Simple Cube"
    cube_obj: Optional[Object] = bpy.data.objects.get(obj_name)

    if obj_name in bpy.data.objects:
        prop: PropertyGroup = context.scene.ACON_prop
        cube_obj.scale.x = round(prop.cube_scale_x, 2)
        cube_obj.scale.y = round(prop.cube_scale_y, 2)
        cube_obj.scale.z = round(prop.cube_scale_z, 2)
