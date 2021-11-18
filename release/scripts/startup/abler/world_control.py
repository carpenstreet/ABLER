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
    "author": "sdk@acon3d.com",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "ACON3D",
}


import bpy


class Acon3dWorldPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_world"
    bl_label = "World Control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="LIGHT")

    def draw(self, context):
        return


class Acon3dCloudControlPanel(bpy.types.Panel):
    bl_label = "Background"
    bl_parent_id = "ACON3D_PT_world"
    bl_idname = "ACON_PT_world_cloud"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_decorate = False  # No animation.
        layout.use_property_split = True
        row = layout.row(align=True)
        row.prop(context.scene.world.ACON_prop, "hdr", text="")
        row = layout.row(align=True)
        row.prop(context.scene.world.ACON_prop, "clouds_height", text="Clouds Height")
        row = layout.row(align=True)
        row.prop(
            context.scene.world.ACON_prop, "clouds_rotation", text="Clouds Rotation"
        )


class Acon3dSunControlPanel(bpy.types.Panel):
    bl_label = "Sun Light"
    bl_parent_id = "ACON3D_PT_world"
    bl_idname = "ACON_PT_world_sun"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.ACON_prop, "toggle_sun", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_decorate = False  # No animation.
        layout.use_property_split = True
        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "sun_strength", text="Strength")


class Acon3dShadowControlPanel(bpy.types.Panel):
    bl_label = "Shadow"
    bl_parent_id = "ACON3D_PT_world"
    bl_idname = "ACON_PT_world_shadow"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.prop(context.scene.ACON_prop, "toggle_shadow", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_decorate = False  # No animation.
        layout.use_property_split = True
        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "sun_rotation_x", text="Altitude")
        row = layout.row(align=True)
        row.prop(context.scene.ACON_prop, "sun_rotation_z", text="Azimuth")


classes = (
    Acon3dWorldPanel,
    Acon3dCloudControlPanel,
    Acon3dSunControlPanel,
    Acon3dShadowControlPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
