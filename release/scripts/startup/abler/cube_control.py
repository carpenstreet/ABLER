# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "ACON3D Panel",
    "description": "",
    "author": "habi@acon3d.com",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "ACON3D",
}


import os
import bpy
from bpy_extras.io_utils import ImportHelper
from .lib.materials import materials_setup
from .lib.tracker import tracker
from random import randint


class CubeMakeOperator(bpy.types.Operator):
    """Make 'Simple Cube'"""

    bl_idname = "acon3d.make_cube"
    bl_label = "Make Cube"
    bl_translation_context = "*"

    def execute(self, context):
        tracker.make_cube()

        if not "Simple Cube" in bpy.data.objects:
            # Search cube objects.
            n = 0

            while len(bpy.data.objects):
                obj_name = "Cube"

                if n != 0:
                    obj_name += "." + format(n, "03")

                # Find empty number.
                if not obj_name in bpy.data.objects:
                    # Make mesh cube.
                    bpy.ops.mesh.primitive_cube_add()

                    # Re-name mesh cube with "Simple Cube"
                    cube_obj = bpy.data.objects[obj_name]
                    cube_obj.name = "Simple Cube"
                    cube_obj.location = (2, -2, 3)
                    cube_obj.scale = (1, 1, 1)

                    break

                n += 1

        return {"FINISHED"}


class CubeRemoveOperator(bpy.types.Operator):
    """Remove 'Simple Cube'"""

    bl_idname = "acon3d.remove_cube"
    bl_label = "Remove Cube"
    bl_translation_context = "*"

    def execute(self, context):
        tracker.remove_cube()

        cube_obj = bpy.data.objects.get("Simple Cube")

        if cube_obj != None:
            if bpy.context.object.mode == "EDIT":
                bpy.ops.object.mode_set(mode="OBJECT")

            # Select only "Simple Cube"
            bpy.ops.object.select_all(action="DESELECT")
            bpy.data.objects["Simple Cube"].select_set(True)
            bpy.ops.object.delete()

        else:
            print("'Simple Cube' doesn't exist. Make a 'Simple Cube'")

        return {"FINISHED"}


class GetCubeObjectOperator(bpy.types.Operator):
    """Get 'Simple Cube' object'"""

    bl_idname = "acon3d.get_cube_object"
    bl_label = "Get Cube Object"
    bl_translation_context = "*"

    def execute(self, context):
        tracker.get_cube_object()

        cube_obj = bpy.data.objects.get("Simple Cube")

        if cube_obj != None:
            print("Selected 'Simple Cube'")
            print("Location : (" + str(cube_obj.location) + ")")
            print("Scale : (" + str(cube_obj.scale) + ")")

            if bpy.context.object.mode == "EDIT":
                bpy.ops.object.mode_set(mode="OBJECT")

            # Select only "Simple Cube"
            bpy.ops.object.select_all(action="DESELECT")
            bpy.data.objects["Simple Cube"].select_set(True)

        else:
            print("'Simple Cube' doesn't exists. Make a 'Simple Cube'")

        return {"FINISHED"}


class RemoveAllOperator(bpy.types.Operator):
    """Remove all objects except light, camera"""

    bl_idname = "acon3d.remove_all"
    bl_label = "Remove All"
    bl_translation_context = "*"

    def execute(self, context):
        tracker.remove_all()

        bpy.ops.object.select_all(action="SELECT")

        for obj in bpy.context.scene.objects:
            for i in ["LIGHT", "CAMERA"]:
                if obj.type == i:
                    obj.select_set(False)

        bpy.ops.object.delete()

        # Delete layers?

        return {"FINISHED"}


class Acon3dCubeControlPanel(bpy.types.Panel):
    """Control 'Simple Cube'"""

    bl_idname = "ACON3D_PT_cube_control"
    bl_label = "Cube Control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="CUBE")

    def draw(self, context):
        return


class Acon3dCubeObjectPanel(bpy.types.Panel):
    """Cube Object Maker"""

    bl_idname = "ACON3D_PT_cube_object"
    bl_label = "Cube Object"
    bl_parent_id = "ACON3D_PT_cube_control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        layout.use_property_decorate = True

        row = layout.row()
        row.operator("acon3d.make_cube", text="Make Cube")
        row.operator("acon3d.remove_cube", text="Remove Cube")
        row = layout.row()
        row.operator("acon3d.get_cube_object", text="Get Cube Object")
        row = layout.row()
        row.operator("acon3d.remove_all", text="Remove All Objects")


class Acon3dCubeLocationPanel(bpy.types.Panel):
    """Cube Location Control"""

    bl_idname = "ACON3D_PT_cube_location"
    bl_label = "Cube Location"
    bl_parent_id = "ACON3D_PT_cube_control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        # Meaning?
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "cube_location_x", text="x-axis")
        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "cube_location_y", text="y-axis")
        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "cube_location_z", text="z-axis")


class Acon3dCubeScalePanel(bpy.types.Panel):
    """Cube Scale Control"""

    bl_label = "Cube Scale"
    bl_idname = "ACON3D_PT_cube_scale"
    bl_parent_id = "ACON3D_PT_cube_control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        # Meaning?
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "cube_scale_x", text="x-axis")
        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "cube_scale_y", text="y-axis")
        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "cube_scale_z", text="z-axis")


classes = (
    Acon3dCubeControlPanel,
    Acon3dCubeObjectPanel,
    CubeMakeOperator,
    CubeRemoveOperator,
    GetCubeObjectOperator,
    RemoveAllOperator,
    Acon3dCubeLocationPanel,
    Acon3dCubeScalePanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
