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


class Acon3dStateUpdateOperator(bpy.types.Operator):
    """Save object's current location / rotation / scale values to state data"""

    bl_idname = "acon3d.state_update"
    bl_label = "Update State"
    bl_translation_context = "*"

    @classmethod
    def poll(cls, context):
        return context.selected_objects

    def execute(self, context):

        for obj in context.selected_objects:

            prop = obj.ACON_prop

            if not prop.use_state:
                continue

            for att in ["location", "rotation_euler", "scale"]:

                vector = getattr(obj, att)
                setattr(prop.state_end, att, vector)

        context.object.ACON_prop.state_slider = 1

        return {"FINISHED"}


class Acon3dStateActionOperator(bpy.types.Operator):
    """Move object state"""

    bl_idname = "acon3d.state_action"
    bl_label = "Move State"
    bl_translation_context = "*"

    step: bpy.props.FloatProperty(name="Toggle Mode", default=0.25)

    def execute(self, context):

        for obj in context.selected_objects:

            prop = obj.ACON_prop
            x = prop.state_slider

            if x == 1:
                x = 0
            else:
                x += self.step

            if x > 1:
                x = 1

            prop.state_slider = x

        return {"FINISHED"}


class RefreshLookAtMeOperator(bpy.types.Operator):

    bl_idname = "acon3d.refresh_lookatme"
    bl_label = "Refresh Look at me"

    def execute(self, context):
        bpy.ops.object.select_all(action="SELECT")
        for obj in bpy.data.objects:
            if obj.ACON_prop.constraint_to_camera_rotation_z:
                obj.ACON_prop.constraint_to_camera_rotation_z = True
        bpy.ops.object.select_all(action="DESELECT")
        return {"FINISHED"}


class Acon3dObjectPanel(bpy.types.Panel):
    bl_idname = "ACON_PT_Object_Main"
    bl_label = "Object Control"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="FILE_3D")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.scale_x = 3
        col.separator()
        col = row.column()

        if context.object:
            row = col.row()
            row.prop(context.object.ACON_prop, "constraint_to_camera_rotation_z")
            row.operator("acon3d.refresh_lookatme", text="", icon="FILE_REFRESH")


class ObjectSubPanel(bpy.types.Panel):
    bl_parent_id = "ACON_PT_Object_Main"
    bl_idname = "ACON_PT_Object_Sub"
    bl_label = "Use State"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        obj = context.object
        if obj:
            layout = self.layout
            layout.active = bool(len(context.selected_objects))
            layout.enabled = layout.active
            layout.prop(obj.ACON_prop, "use_state", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        obj = context.object
        prop = obj.ACON_prop

        layout.active = prop.use_state and bool(len(context.selected_objects))
        layout.enabled = layout.active
        row = layout.row(align=True)
        row.prop(prop, "state_slider", slider=True)
        row.operator("acon3d.state_update", text="", icon="FILE_REFRESH")


classes = (
    Acon3dStateActionOperator,
    Acon3dStateUpdateOperator,
    RefreshLookAtMeOperator,
    Acon3dObjectPanel,
    ObjectSubPanel,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
