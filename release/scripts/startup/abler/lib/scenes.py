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


import bpy, os
from . import shadow, layers, objects
from .materials import materials_handler
from types import SimpleNamespace
from math import radians


def genSceneName(name, i=1):
    found = None
    combinedName = name + str(i)

    for scene in bpy.data.scenes:
        if scene.name == combinedName:
            found = True
            break

    if found:
        return genSceneName(name, i + 1)
    else:
        return combinedName


# items should be a global variable due to a bug in EnumProperty
scene_items = []


def add_scene_items(self, context):
    scene_items.clear()
    for scene in bpy.data.scenes:
        scene_items.append((scene.name, scene.name, ""))

    return scene_items


hdri_items = []


def add_hdri_items(self, context):

    hdri_items.clear()
    hdri_items.append(("None", "None", ""))

    path_abler = bpy.utils.preset_paths("abler")[0]
    path_hdri = os.path.join(path_abler, "hdri")

    for file in os.listdir(path_hdri):

        if not file.lower().endswith((".jpg", ".png", ".tif", ".hdr")):
            continue

        path_hdri_image = os.path.join(path_hdri, file)
        if os.path.isfile(path_hdri_image):
            hdri_items.append((path_hdri_image, file, ""))

    return hdri_items


def loadHdri(self, context):

    scene = context.scene

    image_path = scene.ACON_prop.hdri

    if image_path == "None":
        scene.render.film_transparent = True
        scene.world.use_nodes = False
        return

    scene.render.film_transparent = False
    scene.world.use_nodes = True

    node_tree = scene.world.node_tree
    nodes = node_tree.nodes

    for node in nodes:
        nodes.remove(node)

    node_background = nodes.new("ShaderNodeBackground")
    node_output = nodes.new("ShaderNodeOutputWorld")
    node_tree.links.new(node_background.outputs[0], node_output.inputs[0])
    node_texture = nodes.new("ShaderNodeTexEnvironment")

    image = None
    for item in bpy.data.images:
        if item.filepath == image_path:
            image = item

    if not image:
        image = bpy.data.images.load(image_path)

    node_texture.image = image

    node_tree.links.new(node_texture.outputs[0], node_background.inputs[0])


def loadScene(self, context):
    current_scene = context.scene
    target_scene = bpy.data.scenes[current_scene.ACON_prop.scene]

    if current_scene is not target_scene:
        loadScene_helper(self, context)


def loadScene_helper(self, context):
    current_scene = context.scene
    target_scene = bpy.data.scenes[current_scene.ACON_prop.scene]

    override = SimpleNamespace()
    override.scene = target_scene

    materials_handler.toggleToonEdge(self, override)
    materials_handler.changeLineProps(self, override)
    materials_handler.toggleToonFace(self, override)
    materials_handler.toggleTexture(self, override)
    materials_handler.toggleShading(self, override)
    materials_handler.changeToonDepth(self, override)
    materials_handler.changeToonShadingBrightness(self, override)
    shadow.toggleSun(self, override)
    shadow.changeSunStrength(self, override)
    shadow.toggleShadow(self, override)
    shadow.changeSunRotation(self, override)
    materials_handler.changeImageAdjustBrightness(self, override)
    materials_handler.changeImageAdjustContrast(self, override)
    materials_handler.changeImageAdjustColor(self, override)
    materials_handler.changeImageAdjustHue(self, override)
    materials_handler.changeImageAdjustSaturation(self, override)
    layers.handleLayerVisibilityOnSceneChange(current_scene, target_scene)
    for obj in bpy.data.objects:
        objects.setConstraintToCameraByObject(obj, override)

    context.window.scene = target_scene

    target_scene.ACON_prop.scene = current_scene.ACON_prop.scene


def createScene(old_scene, type, name):

    new_scene = old_scene.copy()
    new_scene.name = name

    new_scene.camera = old_scene.camera.copy()
    new_scene.camera.data = old_scene.camera.data.copy()
    new_scene.collection.objects.link(new_scene.camera)

    try:
        new_scene.collection.objects.unlink(old_scene.camera)
    except:
        print("Failed to unlink camera from old scene.")

    prop = new_scene.ACON_prop

    if type == "Indoor Daytime":

        prop.toggle_toon_edge = True
        prop.edge_min_line_width = 1
        prop.edge_max_line_width = 1
        prop.edge_line_detail = 1.5
        prop.toggle_toon_face = True
        prop.toggle_texture = True
        prop.toggle_shading = True
        prop.toon_shading_depth = "3"
        prop.toon_shading_brightness_1 = 3
        prop.toon_shading_brightness_2 = 5
        prop.toggle_sun = True
        prop.sun_strength = 0.7
        prop.toggle_shadow = True
        prop.sun_rotation_x = radians(45)
        prop.sun_rotation_z = radians(45)
        prop.image_adjust_brightness = 0.7
        prop.image_adjust_contrast = 0.5
        prop.image_adjust_color_r = 0.95
        prop.image_adjust_color_g = 0.95
        prop.image_adjust_color_b = 1.05
        prop.image_adjust_hue = 0.5
        prop.image_adjust_saturation = 1
        new_scene.eevee.use_bloom = True
        new_scene.eevee.bloom_threshold = 2
        new_scene.eevee.bloom_knee = 0.5
        new_scene.eevee.bloom_radius = 6.5
        new_scene.eevee.bloom_color = (1, 1, 1)
        new_scene.eevee.bloom_intensity = 0.1
        new_scene.eevee.bloom_clamp = 0
        new_scene.render.resolution_x = 4800
        new_scene.render.resolution_y = 2700

    if type == "Indoor Sunset":

        prop.toggle_toon_edge = True
        prop.edge_min_line_width = 1
        prop.edge_max_line_width = 1
        prop.edge_line_detail = 1.5
        prop.toggle_toon_face = True
        prop.toggle_texture = True
        prop.toggle_shading = True
        prop.toon_shading_depth = "3"
        prop.toon_shading_brightness_1 = 3
        prop.toon_shading_brightness_2 = 5
        prop.toggle_sun = True
        prop.sun_strength = 1
        prop.toggle_shadow = True
        prop.sun_rotation_x = radians(15)
        prop.sun_rotation_z = radians(45)
        prop.image_adjust_brightness = 0
        prop.image_adjust_contrast = 0
        prop.image_adjust_color_r = 1.1
        prop.image_adjust_color_g = 0.9
        prop.image_adjust_color_b = 0.9
        prop.image_adjust_hue = 0.5
        prop.image_adjust_saturation = 1
        new_scene.eevee.use_bloom = True
        new_scene.eevee.bloom_threshold = 1
        new_scene.eevee.bloom_knee = 0.5
        new_scene.eevee.bloom_radius = 6.5
        new_scene.eevee.bloom_color = (1, 1, 1)
        new_scene.eevee.bloom_intensity = 0.5
        new_scene.eevee.bloom_clamp = 0
        new_scene.render.resolution_x = 4800
        new_scene.render.resolution_y = 2700

    if type == "Indoor Nighttime":

        prop.toggle_toon_edge = True
        prop.edge_min_line_width = 1
        prop.edge_max_line_width = 1
        prop.edge_line_detail = 1.5
        prop.toggle_toon_face = True
        prop.toggle_texture = True
        prop.toggle_shading = True
        prop.toon_shading_depth = "3"
        prop.toon_shading_brightness_1 = 3
        prop.toon_shading_brightness_2 = 5
        prop.toggle_sun = True
        prop.sun_strength = 0.5
        prop.toggle_shadow = False
        prop.sun_rotation_x = radians(65)
        prop.sun_rotation_z = radians(45)
        prop.image_adjust_brightness = 0.1
        prop.image_adjust_contrast = 0
        prop.image_adjust_color_r = 1.05
        prop.image_adjust_color_g = 1
        prop.image_adjust_color_b = 0.95
        prop.image_adjust_hue = 0.5
        prop.image_adjust_saturation = 1
        new_scene.eevee.use_bloom = True
        new_scene.eevee.bloom_threshold = 1
        new_scene.eevee.bloom_knee = 0.5
        new_scene.eevee.bloom_radius = 6.5
        new_scene.eevee.bloom_color = (0.9, 0.9, 1)
        new_scene.eevee.bloom_intensity = 0.5
        new_scene.eevee.bloom_clamp = 0
        new_scene.render.resolution_x = 4800
        new_scene.render.resolution_y = 2700

    if type == "Outdoor Daytime":

        prop.toggle_toon_edge = True
        prop.edge_min_line_width = 1
        prop.edge_max_line_width = 1
        prop.edge_line_detail = 1.5
        prop.toggle_toon_face = True
        prop.toggle_texture = True
        prop.toggle_shading = True
        prop.toon_shading_depth = "3"
        prop.toon_shading_brightness_1 = 3
        prop.toon_shading_brightness_2 = 5
        prop.toggle_sun = True
        prop.sun_strength = 1
        prop.toggle_shadow = True
        prop.sun_rotation_x = radians(60)
        prop.sun_rotation_z = radians(45)
        prop.image_adjust_brightness = 0.7
        prop.image_adjust_contrast = 0.5
        prop.image_adjust_color_r = 1
        prop.image_adjust_color_g = 1
        prop.image_adjust_color_b = 1
        prop.image_adjust_hue = 0.5
        prop.image_adjust_saturation = 1
        new_scene.eevee.use_bloom = False
        new_scene.eevee.bloom_threshold = 1
        new_scene.eevee.bloom_knee = 0.5
        new_scene.eevee.bloom_radius = 6.5
        new_scene.eevee.bloom_color = (1, 1, 1)
        new_scene.eevee.bloom_intensity = 0.1
        new_scene.eevee.bloom_clamp = 0
        new_scene.render.resolution_x = 4800
        new_scene.render.resolution_y = 2700

    if type == "Outdoor Sunset":

        prop.toggle_toon_edge = True
        prop.edge_min_line_width = 1
        prop.edge_max_line_width = 1
        prop.edge_line_detail = 1.5
        prop.toggle_toon_face = True
        prop.toggle_texture = True
        prop.toggle_shading = True
        prop.toon_shading_depth = "3"
        prop.toon_shading_brightness_1 = 3
        prop.toon_shading_brightness_2 = 5
        prop.toggle_sun = True
        prop.sun_strength = 1
        prop.toggle_shadow = True
        prop.sun_rotation_x = radians(15)
        prop.sun_rotation_z = radians(45)
        prop.image_adjust_brightness = 0
        prop.image_adjust_contrast = 0
        prop.image_adjust_color_r = 1.1
        prop.image_adjust_color_g = 0.9
        prop.image_adjust_color_b = 0.9
        prop.image_adjust_hue = 0.5
        prop.image_adjust_saturation = 1
        new_scene.eevee.use_bloom = True
        new_scene.eevee.bloom_threshold = 0.8
        new_scene.eevee.bloom_knee = 0.5
        new_scene.eevee.bloom_radius = 6.5
        new_scene.eevee.bloom_color = (1, 0.9, 0.8)
        new_scene.eevee.bloom_intensity = 0.5
        new_scene.eevee.bloom_clamp = 0
        new_scene.render.resolution_x = 4800
        new_scene.render.resolution_y = 2700

    if type == "Outdoor Nighttime":

        prop.toggle_toon_edge = True
        prop.edge_min_line_width = 1
        prop.edge_max_line_width = 1
        prop.edge_line_detail = 1.5
        prop.toggle_toon_face = True
        prop.toggle_texture = True
        prop.toggle_shading = True
        prop.toon_shading_depth = "3"
        prop.toon_shading_brightness_1 = 3
        prop.toon_shading_brightness_2 = 5
        prop.toggle_sun = True
        prop.sun_strength = 0.4
        prop.toggle_shadow = False
        prop.sun_rotation_x = radians(60)
        prop.sun_rotation_z = radians(45)
        prop.image_adjust_brightness = -0.3
        prop.image_adjust_contrast = -0.25
        prop.image_adjust_color_r = 0.9
        prop.image_adjust_color_g = 0.9
        prop.image_adjust_color_b = 1.1
        prop.image_adjust_hue = 0.5
        prop.image_adjust_saturation = 1.2
        new_scene.eevee.use_bloom = True
        new_scene.eevee.bloom_threshold = 1
        new_scene.eevee.bloom_knee = 0.5
        new_scene.eevee.bloom_radius = 6.5
        new_scene.eevee.bloom_color = (1, 1, 1)
        new_scene.eevee.bloom_intensity = 1
        new_scene.eevee.bloom_clamp = 0
        new_scene.render.resolution_x = 4800
        new_scene.render.resolution_y = 2700

    return new_scene
