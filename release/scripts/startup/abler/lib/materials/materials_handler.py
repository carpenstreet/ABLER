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


def toggleToonEdge(self, context):

    toonEdgeFactorValue = int(context.scene.ACON_prop.toggle_toon_edge)

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    node = node_group.nodes.get("ACON_node_toonEdgeFactor")
    node.outputs[0].default_value = toonEdgeFactorValue


def toggleEachEdge(self, context):

    if "object" not in dir(context):
        return

    obj = context.object
    if obj is None:
        return

    mat = obj.active_material

    if not mat:
        return

    toonEdgeFactorValue = int(mat.ACON_prop.toggle_edge)
    toonNode = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
    toonNode.inputs[9].default_value = toonEdgeFactorValue


def toggleToonFace(self, context):

    toonFaceFactorValue = int(context.scene.ACON_prop.toggle_toon_face)

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    node = node_group.nodes.get("ACON_nodeGroup_toonFace")
    node.inputs[4].default_value = toonFaceFactorValue


def toggleTexture(self, context):

    toggle_texture = context.scene.ACON_prop.toggle_texture
    textureFactorValue = int(not toggle_texture)
    if context.scene.camera:
        for image in context.scene.camera.data.background_images:
            image.show_background_image = toggle_texture

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    node = node_group.nodes.get("ACON_node_textureMixFactor")
    node.inputs[0].default_value = textureFactorValue


def toggleShading(self, context):

    toggle_shading = context.scene.ACON_prop.toggle_shading
    shadingFactorValue = int(toggle_shading)

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    node = node_group.nodes.get("ACON_node_shadeMixFactor")
    node.outputs[0].default_value = shadingFactorValue


def toggleEachShading(self, context):

    if "object" not in dir(context):
        return

    obj = context.object
    if obj is None:
        return

    mat = obj.active_material

    if not mat:
        return

    shadingFactorValue = int(mat.ACON_prop.toggle_shading)
    toonNode = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
    toonNode.inputs[4].default_value = shadingFactorValue


def toggleEachShadow(self, context):

    if "object" not in dir(context):
        return

    obj = context.object
    if obj is None:
        return

    mat = obj.active_material
    if mat is None:
        return
    mat.shadow_method = "CLIP" if mat.ACON_prop.toggle_shadow else "NONE"


def changeToonDepth(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    toonFaceFactorValue = int(context.scene.ACON_prop.toon_shading_depth == "3")

    node = node_group.nodes.get("ACON_nodeGroup_toonFace")
    node.inputs[1].default_value = toonFaceFactorValue


def setMaterialParametersByType(mat):

    type = mat.ACON_prop.type

    toonNode = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
    if not toonNode:
        return

    if type == "Clear":
        mat.blend_method = "BLEND"
        mat.ACON_prop.toggle_shadow = False
        toonNode.inputs[1].default_value = 1
        toonNode.inputs[3].default_value = 1
    elif type == "Diffuse":
        mat.blend_method = "CLIP"
        mat.ACON_prop.toggle_shadow = True
        toonNode.inputs[1].default_value = 0
        toonNode.inputs[3].default_value = 1
    elif type == "Glow":
        mat.blend_method = "CLIP"
        mat.ACON_prop.toggle_shadow = True
        toonNode.inputs[1].default_value = 0
        toonNode.inputs[2].default_value = 0
        toonNode.inputs[3].default_value = 0
    elif type == "Mirror":
        bpy.context.scene.eevee.use_ssr = True
        mat.blend_method = "CLIP"
        mat.ACON_prop.toggle_shadow = True
        toonNode.inputs[1].default_value = 0
        toonNode.inputs[2].default_value = 1
        toonNode.inputs[3].default_value = 0.5


def changeMaterialType(self, context):

    try:
        material_slots = context.active_object.material_slots

        for mat_slot in material_slots:
            mat = mat_slot.material
            setMaterialParametersByType(mat)

    except:
        print("ACON Material Type change handler could not complete.")


def changeImageAdjustBrightness(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    bright = node_group.nodes.get("ACON_node_bright")
    inputs = bright.inputs

    prop = context.scene.ACON_prop
    value = prop.image_adjust_brightness

    inputs[1].default_value = value
    inputs[2].default_value = value


def changeImageAdjustContrast(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    contrast = node_group.nodes.get("ACON_node_contrast")
    inputs = contrast.inputs

    prop = context.scene.ACON_prop
    value = prop.image_adjust_contrast

    inputs[1].default_value = -0.1 * value
    inputs[2].default_value = value


def changeImageAdjustColor(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    brightContrast = node_group.nodes.get("ACON_node_colorBalance")
    inputs = brightContrast.inputs

    prop = context.scene.ACON_prop
    r = prop.image_adjust_color_r
    g = prop.image_adjust_color_g
    b = prop.image_adjust_color_b
    color = (r, g, b, 1)

    inputs[2].default_value = color


def changeImageAdjustHue(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    hueSaturation = node_group.nodes.get("ACON_node_hueSaturation")
    inputs = hueSaturation.inputs

    prop = context.scene.ACON_prop
    value = prop.image_adjust_hue

    inputs[0].default_value = value


def changeImageAdjustSaturation(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    hueSaturation = node_group.nodes.get("ACON_node_hueSaturation")
    inputs = hueSaturation.inputs

    prop = context.scene.ACON_prop
    value = prop.image_adjust_saturation

    inputs[1].default_value = value


def changeLineProps(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    node_outline = node_group.nodes.get("ACON_nodeGroup_outline")
    inputs = node_outline.inputs

    prop = context.scene.ACON_prop
    min_value = prop.edge_min_line_width
    max_value = prop.edge_max_line_width
    line_detail = prop.edge_line_detail

    inputs[0].default_value = min_value
    inputs[1].default_value = max_value
    inputs[3].default_value = line_detail


def changeToonShadingBrightness(self, context):

    node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")
    if not node_group:
        return

    node_outline = node_group.nodes.get("ACON_nodeGroup_toonFace")
    inputs = node_outline.inputs

    prop = context.scene.ACON_prop
    value_1 = prop.toon_shading_brightness_1
    value_2 = prop.toon_shading_brightness_2

    inputs[2].default_value = value_1
    inputs[3].default_value = value_2
