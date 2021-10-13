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
    "author": "hoie@acon3d.com",
    "version": (0, 0, 1),
    "blender": (2, 93, 0),
    "location": "",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "ACON3D",
}


import bpy
from .lib import scenes


class CreateSceneOperator(bpy.types.Operator):
    """Create a new scene with current settings"""

    bl_idname = "acon3d.create_scene"
    bl_label = "New Scene"
    bl_translation_context = "*"

    def execute(self, context):
        bpy.ops.acon3d.set_scene_name("INVOKE_DEFAULT")

        return {"FINISHED"}


class SetScenePropsOperator(bpy.types.Operator):
    bl_idname = "acon3d.set_scene_name"
    bl_label = "New Scene"

    name: bpy.props.StringProperty(name="Name")

    preset: bpy.props.EnumProperty(
        name="Preset",
        description="Scene preset",
        items=[
            ("None", "Use Current Scene Settings", ""),
            ("Indoor Daytime", "Indoor Daytime", ""),
            ("Indoor Sunset", "Indoor Sunset", ""),
            ("Indoor Nighttime", "Indoor Nighttime", ""),
            ("Outdoor Daytime", "Outdoor Daytime", ""),
            ("Outdoor Sunset", "Outdoor Sunset", ""),
            ("Outdoor Nighttime", "Outdoor Nighttime", ""),
        ],
    )

    def execute(self, context):
        old_scene = context.scene
        new_scene = scenes.createScene(old_scene, self.preset, self.name)
        context.scene.ACON_prop.scene = new_scene.name
        return {"FINISHED"}

    def invoke(self, context, event):
        self.name = scenes.genSceneName("ACON_Scene_")
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.separator()
        layout.prop(self, "name")
        layout.prop(self, "preset")
        layout.separator()


class DeleteSceneOperator(bpy.types.Operator):
    """Remove current scene from project"""

    bl_idname = "acon3d.delete_scene"
    bl_label = "Remove Scene"
    bl_translation_context = "*"

    def execute(self, context):
        sceneName = context.scene.ACON_prop.scene
        scene = bpy.data.scenes[sceneName]
        bpy.data.scenes.remove(scene)
        context.scene.ACON_prop.scene = context.scene.name
        scenes.loadScene_helper(self, context)

        return {"FINISHED"}


class Acon3dScenesPanel(bpy.types.Panel):
    bl_idname = "ACON3D_PT_scenes"
    bl_label = "Scenes"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="SCENE_DATA")

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row(align=True)
        row.prop(scene.ACON_prop, "scene", text="")
        row.operator("acon3d.create_scene", text="", icon="ADD")
        row.operator("acon3d.delete_scene", text="", icon="REMOVE")

        row = layout.row(align=True)
        row.prop(scene.ACON_prop, "hdri", text="")


classes = (
    CreateSceneOperator,
    SetScenePropsOperator,
    DeleteSceneOperator,
    Acon3dScenesPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
