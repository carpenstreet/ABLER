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
from math import radians


def createAconWorldSurfaceNodeGroup():

    node_group = bpy.data.node_groups.new(
        "ACON_nodeGroup_world_surface", "ShaderNodeTree"
    )

    nodes = node_group.nodes

    node_input = nodes.new("NodeGroupInput")
    node_group.inputs.new("NodeSocketFloat", "Cloud Height").default_value = 300
    node_group.inputs.new("NodeSocketFloat", "Cloud Rotation").default_value = radians(
        100
    )
    node_group.inputs.new("NodeSocketVector", "Sun Vector")
    node_group.inputs.new("NodeSocketVector", "Diffuse")
    node_group.inputs.new("NodeSocketVector", "Normal")

    node_texCord = nodes.new("ShaderNodeTexCoord")
    node_mapping_1 = nodes.new("ShaderNodeMapping")
    node_group.links.new(
        node_texCord.outputs.get("Generated"), node_mapping_1.inputs.get("Vector")
    )

    node_vector_cloud_rotation = nodes.new("ShaderNodeCombineXYZ")
    node_vector_cloud_rotation.inputs.get("X").default_value = radians(45)
    node_group.links.new(
        node_vector_cloud_rotation.outputs.get("Vector"),
        node_mapping_1.inputs.get("Rotation"),
    )
    node_group.links.new(
        node_input.outputs.get("Cloud Rotation"),
        node_vector_cloud_rotation.inputs.get("Z"),
    )

    node_multiply_1 = nodes.new("ShaderNodeVectorMath")
    node_multiply_1.operation = "MULTIPLY"
    node_group.links.new(
        node_mapping_1.outputs.get("Vector"), node_multiply_1.inputs[0]
    )

    node_vector_cloud = nodes.new("ShaderNodeCombineXYZ")
    node_group.links.new(
        node_input.outputs.get("Cloud Height"), node_vector_cloud.inputs.get("Z")
    )

    node_normalize = nodes.new("ShaderNodeVectorMath")
    node_normalize.operation = "NORMALIZE"
    node_group.links.new(
        node_vector_cloud.outputs.get("Vector"), node_normalize.inputs.get("Vector")
    )

    node_dot_1 = nodes.new("ShaderNodeVectorMath")
    node_dot_1.operation = "DOT_PRODUCT"
    node_group.links.new(node_normalize.outputs.get("Vector"), node_dot_1.inputs[0])
    node_group.links.new(node_vector_cloud.outputs.get("Vector"), node_dot_1.inputs[1])

    node_dot_2 = nodes.new("ShaderNodeVectorMath")
    node_dot_2.operation = "DOT_PRODUCT"
    node_group.links.new(node_normalize.outputs.get("Vector"), node_dot_2.inputs[0])
    node_group.links.new(node_texCord.outputs.get("Generated"), node_dot_2.inputs[1])

    node_divide = nodes.new("ShaderNodeMath")
    node_divide.operation = "DIVIDE"
    node_group.links.new(node_dot_1.outputs.get("Value"), node_divide.inputs[0])
    node_group.links.new(node_dot_2.outputs.get("Value"), node_divide.inputs[1])
    node_group.links.new(node_divide.outputs.get("Value"), node_multiply_1.inputs[1])

    node_noise_1 = nodes.new("ShaderNodeTexNoise")
    node_noise_1.inputs.get("Scale").default_value = 0.005
    node_noise_1.inputs.get("Detail").default_value = 14
    node_group.links.new(
        node_multiply_1.outputs.get("Vector"), node_noise_1.inputs.get("Vector")
    )

    node_noise_2 = nodes.new("ShaderNodeTexNoise")
    node_noise_2.inputs.get("Scale").default_value = 0.001
    node_noise_2.inputs.get("Detail").default_value = 14
    node_group.links.new(
        node_multiply_1.outputs.get("Vector"), node_noise_2.inputs.get("Vector")
    )

    node_multiply_2 = nodes.new("ShaderNodeMixRGB")
    node_multiply_2.blend_type = "MULTIPLY"
    node_multiply_2.inputs.get("Fac").default_value = 0.8
    node_group.links.new(
        node_noise_1.outputs.get("Fac"), node_multiply_2.inputs.get("Color1")
    )
    node_group.links.new(
        node_noise_2.outputs.get("Fac"), node_multiply_2.inputs.get("Color2")
    )

    node_separate = nodes.new("ShaderNodeSeparateXYZ")
    node_group.links.new(
        node_texCord.outputs.get("Generated"), node_separate.inputs.get("Vector")
    )

    node_add_1 = nodes.new("ShaderNodeMath")
    node_add_1.operation = "ADD"
    node_add_1.inputs[1].default_value = 1
    node_group.links.new(node_separate.outputs.get("Z"), node_add_1.inputs[0])

    node_multiply_3 = nodes.new("ShaderNodeMath")
    node_multiply_3.operation = "MULTIPLY"
    node_multiply_3.inputs[1].default_value = 0.5
    node_group.links.new(node_add_1.outputs.get("Value"), node_multiply_3.inputs[0])

    node_mapping_2 = nodes.new("ShaderNodeMapping")
    node_group.links.new(
        node_normalize.outputs.get("Vector"), node_mapping_2.inputs.get("Vector")
    )
    node_group.links.new(
        node_input.outputs.get("Sun Vector"), node_mapping_2.inputs.get("Rotation")
    )

    node_distance = nodes.new("ShaderNodeVectorMath")
    node_distance.operation = "DISTANCE"
    node_group.links.new(node_texCord.outputs.get("Generated"), node_distance.inputs[0])
    node_group.links.new(node_mapping_2.outputs.get("Vector"), node_distance.inputs[1])

    node_multiply_4 = nodes.new("ShaderNodeMath")
    node_multiply_4.operation = "MULTIPLY"
    node_multiply_4.inputs[1].default_value = -0.5
    node_group.links.new(node_distance.outputs.get("Value"), node_multiply_4.inputs[0])

    node_add_2 = nodes.new("ShaderNodeMath")
    node_add_2.operation = "ADD"
    node_add_2.inputs[1].default_value = 1
    node_group.links.new(node_multiply_4.outputs.get("Value"), node_add_2.inputs[0])

    node_colorRamp_1 = nodes.new("ShaderNodeValToRGB")
    node_colorRamp_1.color_ramp.interpolation = "LINEAR"
    node_colorRamp_1.color_ramp.elements[0].position = 0.5
    node_colorRamp_1.color_ramp.elements[0].color = (0, 0, 0, 1)
    node_colorRamp_1.color_ramp.elements[1].position = 0.6
    node_colorRamp_1.color_ramp.elements[1].color = (1, 1, 1, 1)
    node_group.links.new(
        node_multiply_3.outputs.get("Value"), node_colorRamp_1.inputs.get("Fac")
    )

    node_multiply_5 = nodes.new("ShaderNodeMixRGB")
    node_multiply_5.blend_type = "MULTIPLY"
    node_multiply_5.inputs.get("Fac").default_value = 1
    node_group.links.new(
        node_add_2.outputs.get("Value"), node_multiply_5.inputs.get("Color1")
    )
    node_group.links.new(
        node_colorRamp_1.outputs.get("Color"), node_multiply_5.inputs.get("Color2")
    )

    node_colorRamp_2 = nodes.new("ShaderNodeValToRGB")
    node_colorRamp_2.name = "ACON_node_skyColor"
    node_colorRamp_2.color_ramp.interpolation = "LINEAR"
    node_colorRamp_2.color_ramp.elements[0].position = 0
    node_colorRamp_2.color_ramp.elements[0].color = (0.02, 0.03, 0.12, 1)
    node_colorRamp_2.color_ramp.elements[1].position = 1
    node_colorRamp_2.color_ramp.elements[1].color = (0.08, 0.6, 1, 1)
    node_colorRamp_2.color_ramp.elements.new(0.5).position = 0.4
    node_group.links.new(
        node_multiply_5.outputs.get("Color"), node_colorRamp_2.inputs.get("Fac")
    )

    node_colorRamp_3 = nodes.new("ShaderNodeValToRGB")
    node_colorRamp_3.color_ramp.interpolation = "LINEAR"
    node_colorRamp_3.color_ramp.elements[0].position = 0.3
    node_colorRamp_3.color_ramp.elements[0].color = (0, 0, 0, 1)
    node_colorRamp_3.color_ramp.elements[1].position = 0.5
    node_colorRamp_3.color_ramp.elements[1].color = (1, 1, 1, 1)
    node_group.links.new(
        node_multiply_2.outputs.get("Color"), node_colorRamp_3.inputs.get("Fac")
    )

    node_softLight = nodes.new("ShaderNodeMixRGB")
    node_softLight.blend_type = "SOFT_LIGHT"
    node_softLight.inputs.get("Fac").default_value = 0.5
    node_group.links.new(
        node_multiply_5.outputs.get("Color"), node_softLight.inputs.get("Color1")
    )
    node_group.links.new(
        node_colorRamp_3.outputs.get("Color"), node_softLight.inputs.get("Color2")
    )

    node_colorRamp_4 = nodes.new("ShaderNodeValToRGB")
    node_colorRamp_4.name = "ACON_node_cloudColor"
    node_colorRamp_4.color_ramp.interpolation = "LINEAR"
    node_colorRamp_4.color_ramp.elements[0].position = 0
    node_colorRamp_4.color_ramp.elements[0].color = (0.14, 0.28, 0.58, 1)
    node_colorRamp_4.color_ramp.elements[1].position = 1
    node_colorRamp_4.color_ramp.elements[1].color = (1, 1, 1, 1)
    node_group.links.new(
        node_softLight.outputs.get("Color"), node_colorRamp_4.inputs.get("Fac")
    )

    node_multiply_6 = nodes.new("ShaderNodeMath")
    node_multiply_6.operation = "MULTIPLY"
    node_multiply_6.inputs[1].default_value = -1
    node_group.links.new(
        node_colorRamp_1.outputs.get("Color"), node_multiply_6.inputs[0]
    )

    node_add_3 = nodes.new("ShaderNodeMath")
    node_add_3.operation = "ADD"
    node_add_3.inputs[1].default_value = 1
    node_group.links.new(node_multiply_6.outputs.get("Value"), node_add_3.inputs[0])

    node_colorRamp_5 = nodes.new("ShaderNodeValToRGB")
    node_colorRamp_5.color_ramp.interpolation = "CONSTANT"
    node_colorRamp_5.color_ramp.elements[0].position = 0
    node_colorRamp_5.color_ramp.elements[0].color = (0, 0, 0, 1)
    node_colorRamp_5.color_ramp.elements[1].position = 0.22
    node_colorRamp_5.color_ramp.elements[1].color = (1, 1, 1, 1)
    node_group.links.new(
        node_multiply_2.outputs.get("Color"), node_colorRamp_5.inputs.get("Fac")
    )

    node_add_4 = nodes.new("ShaderNodeMath")
    node_add_4.operation = "ADD"
    node_group.links.new(node_add_3.outputs.get("Value"), node_add_4.inputs[0])
    node_group.links.new(node_colorRamp_5.outputs.get("Color"), node_add_4.inputs[1])

    node_mix_1 = nodes.new("ShaderNodeMixRGB")
    node_mix_1.blend_type = "MIX"
    node_group.links.new(node_add_4.outputs.get("Value"), node_mix_1.inputs.get("Fac"))
    node_group.links.new(
        node_colorRamp_4.outputs.get("Color"), node_mix_1.inputs.get("Color1")
    )
    node_group.links.new(
        node_colorRamp_2.outputs.get("Color"), node_mix_1.inputs.get("Color2")
    )

    node_colorRamp_6 = nodes.new("ShaderNodeValToRGB")
    node_colorRamp_6.color_ramp.interpolation = "EASE"
    node_colorRamp_6.color_ramp.elements[0].position = 0
    node_colorRamp_6.color_ramp.elements[0].color = (1, 1, 1, 1)
    node_colorRamp_6.color_ramp.elements[1].position = 0.05
    node_colorRamp_6.color_ramp.elements[1].color = (0, 0, 0, 1)
    node_group.links.new(
        node_distance.outputs.get("Value"), node_colorRamp_6.inputs.get("Fac")
    )

    node_multiply_7 = nodes.new("ShaderNodeMath")
    node_multiply_7.operation = "MULTIPLY"
    node_multiply_7.inputs[1].default_value = 100
    node_group.links.new(
        node_colorRamp_6.outputs.get("Color"), node_multiply_7.inputs[0]
    )

    node_add_5 = nodes.new("ShaderNodeMath")
    node_add_5.operation = "ADD"
    node_add_5.inputs[1].default_value = 1
    node_group.links.new(node_multiply_7.outputs.get("Value"), node_add_5.inputs[0])

    node_multiply_8 = nodes.new("ShaderNodeMixRGB")
    node_multiply_8.blend_type = "MULTIPLY"
    node_multiply_8.inputs.get("Fac").default_value = 1
    node_group.links.new(
        node_add_5.outputs.get("Value"), node_multiply_8.inputs.get("Color1")
    )
    node_group.links.new(
        node_mix_1.outputs.get("Color"), node_multiply_8.inputs.get("Color2")
    )

    node_length = nodes.new("ShaderNodeVectorMath")
    node_length.operation = "LENGTH"
    node_group.links.new(
        node_input.outputs.get("Normal"), node_length.inputs.get("Vector")
    )

    node_lessThan = nodes.new("ShaderNodeMath")
    node_lessThan.operation = "LESS_THAN"
    node_lessThan.inputs[1].default_value = 0.1
    node_group.links.new(node_length.outputs.get("Value"), node_lessThan.inputs[0])

    node_subtract = nodes.new("ShaderNodeVectorMath")
    node_subtract.operation = "SUBTRACT"
    node_subtract.inputs[1].default_value = (0.5, 0.5, 0.5)
    node_group.links.new(node_input.outputs.get("Normal"), node_subtract.inputs[0])

    node_multiply_9 = nodes.new("ShaderNodeVectorMath")
    node_multiply_9.operation = "MULTIPLY"
    node_multiply_9.inputs[1].default_value = (2, 2, 2)
    node_group.links.new(node_subtract.outputs.get("Vector"), node_multiply_9.inputs[0])

    node_dot_3 = nodes.new("ShaderNodeVectorMath")
    node_dot_3.operation = "DOT_PRODUCT"
    node_group.links.new(node_multiply_9.outputs.get("Vector"), node_dot_3.inputs[0])
    node_group.links.new(node_mapping_2.outputs.get("Vector"), node_dot_3.inputs[1])

    node_colorRamp_7 = nodes.new("ShaderNodeValToRGB")
    node_colorRamp_7.color_ramp.interpolation = "CONSTANT"
    node_colorRamp_7.color_ramp.elements.new(0.5)
    node_colorRamp_7.color_ramp.elements[0].position = 0
    node_colorRamp_7.color_ramp.elements[0].color = (0.4, 0.4, 0.4, 1)
    node_colorRamp_7.color_ramp.elements[1].position = 0.1
    node_colorRamp_7.color_ramp.elements[1].color = (0.6, 0.6, 0.6, 1)
    node_colorRamp_7.color_ramp.elements[2].position = 0.4
    node_colorRamp_7.color_ramp.elements[2].color = (1, 1, 1, 1)
    node_group.links.new(
        node_dot_3.outputs.get("Value"), node_colorRamp_7.inputs.get("Fac")
    )

    node_multiply_10 = nodes.new("ShaderNodeMixRGB")
    node_multiply_10.blend_type = "MULTIPLY"
    node_multiply_10.inputs.get("Fac").default_value = 1
    node_group.links.new(
        node_colorRamp_7.outputs.get("Color"), node_multiply_10.inputs.get("Color1")
    )
    node_group.links.new(
        node_input.outputs.get("Diffuse"), node_multiply_10.inputs.get("Color2")
    )

    node_mix_2 = nodes.new("ShaderNodeMixRGB")
    node_mix_2.blend_type = "MIX"
    node_group.links.new(
        node_lessThan.outputs.get("Value"), node_mix_2.inputs.get("Fac")
    )
    node_group.links.new(
        node_multiply_10.outputs.get("Color"), node_mix_2.inputs.get("Color1")
    )
    node_group.links.new(
        node_multiply_8.outputs.get("Color"), node_mix_2.inputs.get("Color2")
    )

    node_lightPath = nodes.new("ShaderNodeLightPath")

    node_mix_3 = nodes.new("ShaderNodeMixRGB")
    node_mix_3.blend_type = "MIX"
    node_mix_3.inputs.get("Color1").default_value = (0, 0, 0, 1)
    node_group.links.new(
        node_lightPath.outputs.get("Is Camera Ray"), node_mix_3.inputs.get("Fac")
    )
    node_group.links.new(
        node_mix_2.outputs.get("Color"), node_mix_3.inputs.get("Color2")
    )

    node_background = nodes.new("ShaderNodeBackground")
    node_background.inputs.get("Strength").default_value = 1
    node_group.links.new(
        node_mix_3.outputs.get("Color"), node_background.inputs.get("Color")
    )

    node_output = nodes.new("NodeGroupOutput")
    node_group.outputs.new("NodeSocketShader", "Background")
    node_group.links.new(
        node_background.outputs.get("Background"), node_output.inputs.get("Background")
    )

    return node_group


def applyAconWorldShader():

    for node_group in bpy.data.node_groups:
        if "ACON_nodeGroup_world_surface" in node_group.name:
            bpy.data.node_groups.remove(node_group)

    node_group_data_surface = createAconWorldSurfaceNodeGroup()

    node_tree = bpy.context.scene.world.node_tree
    nodes = node_tree.nodes

    node_group_surface = None
    node_volume = None
    node_output = None
    node_env_diffuse = None
    node_env_normal = None

    for node in nodes:
        if node.name == "ACON_nodeGroup_world_surface":
            node.node_tree = node_group_data_surface
            node_group_surface = node
        elif node.name == "ACON_node_volume":
            node_volume = node
        elif node.name == "ACON_node_env_diffuse":
            node_env_diffuse = node
        elif node.name == "ACON_node_env_normal":
            node_env_normal = node
        elif node.type == "OUTPUT_WORLD":
            node_output = node
        else:
            nodes.remove(node)

    if not node_group_surface:
        node_group_surface = nodes.new(type="ShaderNodeGroup")
        node_group_surface.name = "ACON_nodeGroup_world_surface"
        node_group_surface.node_tree = node_group_data_surface

    if not node_volume:
        node_volume = nodes.new("ShaderNodeVolumeScatter")
        node_volume.name = "ACON_node_volume"
        node_volume.inputs.get("Density").default_value = 0

    if not node_env_diffuse:
        node_env_diffuse = nodes.new("ShaderNodeTexEnvironment")
        node_env_diffuse.name = "ACON_node_env_diffuse"

    if not node_env_normal:
        node_env_normal = nodes.new("ShaderNodeTexEnvironment")
        node_env_normal.name = "ACON_node_env_normal"

    if not node_output:
        node_output = nodes.new("ShaderNodeOutputWorld")

    node_tree.links.new(
        node_group_surface.outputs.get("Background"), node_output.inputs.get("Surface")
    )

    node_tree.links.new(
        node_volume.outputs.get("Volume"), node_output.inputs.get("Volume")
    )

    node_tree.links.new(
        node_env_diffuse.outputs.get("Color"), node_group_surface.inputs.get("Diffuse")
    )

    node_tree.links.new(
        node_env_normal.outputs.get("Color"), node_group_surface.inputs.get("Normal")
    )
