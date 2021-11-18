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


import bpy
from bpy.app.handlers import persistent


def handleLayerVisibilityOnSceneChange(oldScene, newScene):

    if not oldScene or not newScene:
        print("Invalid oldScene / newScene given")
        return

    i = 0
    for oldProp in oldScene.l_exclude:
        newProp = newScene.l_exclude[i]

        if oldProp.value is not newProp.value:
            target_layer = bpy.data.collections[newProp.name]
            for objs in target_layer.objects:
                objs.hide_viewport = not (newProp.value)
                objs.hide_render = not (newProp.value)

        if oldProp.lock is not newProp.lock:
            target_layer = bpy.data.collections[newProp.name]
            for objs in target_layer.objects:
                objs.hide_select = newProp.lock

        i += 1


def selectByGroup():

    selected_object = bpy.context.active_object
    group_props = selected_object.ACON_prop.group

    group_length = len(group_props)
    if not group_length:
        return

    last_group_prop = group_props[group_length - 1]

    selected_group = bpy.data.collections.get(last_group_prop.name)
    if not selected_group:
        group_props.remove(group_length - 1)
        return selectByGroup()

    for obj in selected_group.all_objects:
        obj.select_set(True)


@persistent
def checkObjectSelectionChange(dummy):

    depsgraph = bpy.context.evaluated_depsgraph_get()
    if not depsgraph.id_type_updated("SCENE"):
        return

    new_selected_objects_str = ""
    for obj in bpy.context.selected_objects:
        new_selected_objects_str += obj.name

    ACON_prop = bpy.context.scene.ACON_prop

    if new_selected_objects_str == ACON_prop.selected_objects_str:
        return

    if new_selected_objects_str:
        selectByGroup()

    ACON_prop.selected_objects_str = ""
    for obj in bpy.context.selected_objects:
        ACON_prop.selected_objects_str += obj.name


def subscribeToGroupedObjects():
    bpy.app.handlers.depsgraph_update_post.append(checkObjectSelectionChange)


def clearSubscribers():
    bpy.app.handlers.depsgraph_update_post.remove(checkObjectSelectionChange)
