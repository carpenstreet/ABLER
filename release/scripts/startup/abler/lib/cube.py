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
        loc_x: FloatProperty = round(prop.cube_location_x, 2)
        loc_y: FloatProperty = round(prop.cube_location_y, 2)
        loc_z: FloatProperty = round(prop.cube_location_z, 2)

        cube_obj.location.x = loc_x
        cube_obj.location.y = loc_y
        cube_obj.location.z = loc_z


def changeCubeScale(self, context: Context) -> None:
    obj_name = "Simple Cube"
    cube_obj: Optional[Object] = bpy.data.objects.get(obj_name)

    if obj_name in bpy.data.objects:
        prop: PropertyGroup = context.scene.ACON_prop
        scale_x: FloatProperty = round(prop.cube_scale_x, 2)
        scale_y: FloatProperty = round(prop.cube_scale_y, 2)
        scale_z: FloatProperty = round(prop.cube_scale_z, 2)

        cube_obj.scale.x = scale_x
        cube_obj.scale.y = scale_y
        cube_obj.scale.z = scale_z
