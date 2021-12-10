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
from typing import List, Union


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


def get_parent_collection(
    collection: bpy.types.Collection, parents: List[bpy.types.Collection]
) -> None:
    for parent_collection in bpy.data.collections:
        if collection.name in parent_collection.children.keys():
            parents.append(parent_collection)
            get_parent_collection(parent_collection, parents)
            return


def get_single_parent_collection(
    collection: bpy.types.Collection,
) -> bpy.types.Collection:
    for parent_collection in bpy.data.collections:
        if collection.name in parent_collection.children.keys():
            return parent_collection


def is_parent_collection(a: bpy.types.Collection, b: bpy.types.Collection) -> bool:
    parents = []
    get_parent_collection(a, parents)
    return b in parents


def quick_sort_by_hierarchy(
    arr: List[bpy.types.Collection],
) -> List[bpy.types.Collection]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    lesser_arr, equal_arr, greater_arr = [], [], []
    for col in arr:
        if is_parent_collection(col, pivot):
            lesser_arr.append(col)
        elif is_parent_collection(pivot, col):
            greater_arr.append(col)
        else:
            equal_arr.append(col)
    return (
        quick_sort_by_hierarchy(lesser_arr)
        + equal_arr
        + quick_sort_by_hierarchy(greater_arr)
    )


def get_root_collections(
    collection: bpy.types.Collection,
) -> List[bpy.types.Collection]:
    parents = []
    get_parent_collection(collection, parents)
    parents.pop()
    ret_list = list(reversed(quick_sort_by_hierarchy(parents)))
    ret_list.append(collection)
    return ret_list


def get_root_collections_from_object(
    obj: bpy.types.Object,
) -> List[bpy.types.Collection]:
    if not obj or not obj.ACON_prop or not obj.ACON_prop.group:
        return

    group_props = obj.ACON_prop.group

    group_length = len(group_props)
    if not group_length:
        return

    last_group_prop = group_props[-1]

    selected_group = bpy.data.collections.get(last_group_prop.name)
    return get_root_collections(selected_group)


def selectByGroup(direction: str) -> None:

    selected_object = bpy.context.active_object
    selected_group_prop = bpy.context.scene.ACON_selected_group

    if not selected_object:
        selected_group_prop.current_root_group = ""
        selected_group_prop.current_group = ""
        return

    group_props = selected_object.ACON_prop.group

    group_length = len(group_props)
    if not group_length:
        return

    last_group_prop = group_props[-1]

    selected_group = bpy.data.collections.get(last_group_prop.name)
    ordered_parent_group = get_root_collections(selected_group)
    if len(ordered_parent_group) > 0:
        root_parent_group: bpy.types.Collection = ordered_parent_group[0]
    if not selected_group:
        group_props.remove(group_length - 1)
        return selectByGroup(direction)
    # Put root group in prop
    selected_group_prop.current_root_group = root_parent_group.name
    if direction == "TOP":
        selected_group_prop.current_group = root_parent_group.name
        for obj in root_parent_group.all_objects:
            obj.select_set(True)
    elif direction == "BOTTOM":
        # Put last group in prop
        selected_group_prop.current_group = ordered_parent_group[-1].name
    elif direction == "UP":
        if selected_group_prop.current_root_group == root_parent_group.name:
            selection = up(
                ordered_parent_group,
                bpy.data.collections[selected_group_prop.current_group],
            )
            if not selection:
                return selectByGroup("TOP")
            selected_group_prop.current_group = selection.name
            for obj in selection.all_objects:
                obj.select_set(True)
    elif direction == "DOWN":
        if selected_group_prop.current_root_group == root_parent_group.name:
            selection = down(
                ordered_parent_group,
                bpy.data.collections[selected_group_prop.current_group],
            )
            if not selection:
                return selectByGroup("TOP")
            if selection == "object":
                return
            selected_group_prop.current_group = selection.name
            for obj in selection.all_objects:
                obj.select_set(True)


def up(
    group_list: List[bpy.types.Collection], group_item: bpy.types.Collection
) -> Union[bpy.types.Collection, str]:
    """
    group_list: List of collections
    group_item: Collection to find upper item of
    """
    try:
        idx: int = group_list.index(group_item)
        if idx > 0:
            return group_list[idx - 1]
        else:
            return group_list[0]
    except:
        return None


def down(
    group_list: List[bpy.types.Collection], group_item: bpy.types.Collection
) -> Union[bpy.types.Collection, str]:
    """
    group_list: List of collections
    group_item: Collection to find item below of
    """
    try:
        idx = group_list.index(group_item)
        if idx < len(group_list) - 1:
            return group_list[idx + 1]
        else:
            return "object"
    except:
        return None


@persistent
def checkObjectSelectionChange(dummy):

    depsgraph = bpy.context.evaluated_depsgraph_get()
    if not depsgraph.id_type_updated("SCENE"):
        return

    new_selected_objects_str = "".join(obj.name for obj in bpy.context.selected_objects)

    ACON_prop = bpy.context.scene.ACON_prop

    if new_selected_objects_str == ACON_prop.selected_objects_str:
        return

    if new_selected_objects_str:
        selectByGroup(bpy.context.scene.ACON_selected_group.direction)

    ACON_prop.selected_objects_str = "".join(
        obj.name for obj in bpy.context.selected_objects
    )


@persistent
def initDoubleClick(dummy):
    bpy.ops.wm.modal_timer_operator("INVOKE_DEFAULT")


def subscribeToDoubleClick():
    bpy.app.handlers.load_post.append(initDoubleClick)


def clearDoubleClickSubscribers():
    bpy.app.handlers.load_post.remove(initDoubleClick)


def subscribeToGroupedObjects():
    bpy.app.handlers.depsgraph_update_post.append(checkObjectSelectionChange)


def clearSubscribers():
    bpy.app.handlers.depsgraph_update_post.remove(checkObjectSelectionChange)
