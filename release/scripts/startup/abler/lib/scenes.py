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


from typing import List, Union, Tuple
import bpy
from bpy.types import Scene
from . import shadow, layers, objects
from .materials import materials_handler
from math import radians


def genSceneName(name: str, i: int = 1) -> str:
    found: Union[bool, None] = None
    combinedName: str = name + str(i)

    for scene in bpy.data.scenes:
        if scene.name == combinedName:
            found = True
            break

    if found:
        return genSceneName(name, i + 1)
    else:
        return combinedName


# scene_items should be a global variable due to a bug in EnumProperty
scene_items: List[Tuple[str, str, str]] = []


def add_scene_items(self, context) -> List[Tuple[str, str, str]]:
    scene_items.clear()
    for scene in bpy.data.scenes:
        scene_items.append((scene.name, scene.name, ""))

    return scene_items


def loadScene(self, context) -> None:

    if not context:
        context = bpy.context

    if not self:
        self = context.window_manager.ACON_prop

    newScene: Union[Scene, None] = bpy.data.scenes.get(self.scene)
    oldScene: Union[Scene, None] = context.scene
    context.window.scene = newScene

    materials_handler.toggleToonEdge(None, context)
    materials_handler.changeLineProps(None, context)
    materials_handler.toggleToonFace(None, context)
    materials_handler.toggleTexture(None, context)
    materials_handler.toggleShading(None, context)
    materials_handler.changeToonDepth(None, context)
    materials_handler.changeToonShadingBrightness(None, context)
    materials_handler.changeImageAdjustBrightness(None, context)
    materials_handler.changeImageAdjustContrast(None, context)
    materials_handler.changeImageAdjustColor(None, context)
    materials_handler.changeImageAdjustHue(None, context)
    materials_handler.changeImageAdjustSaturation(None, context)

    layers.handleLayerVisibilityOnSceneChange(oldScene, newScene)

    shadow.toggleSun(None, context)
    shadow.changeSunStrength(None, context)
    shadow.toggleShadow(None, context)
    shadow.changeSunRotation(None, context)

    for obj in bpy.data.objects:
        objects.setConstraintToCameraByObject(obj, context)


def createScene(old_scene: Scene, type: str, name: str) -> Union[Scene, None]:

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
