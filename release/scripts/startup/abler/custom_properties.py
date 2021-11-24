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
from .lib import scenes, cameras, shadow, objects, materials


class AconWindowManagerProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.WindowManager.ACON_prop = bpy.props.PointerProperty(
            type=AconWindowManagerProperty
        )

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.ACON_prop

    scene: bpy.props.EnumProperty(
        name="Scene",
        description="Change scene",
        items=scenes.add_scene_items,
        update=scenes.loadScene,
    )


class CollectionLayerExcludeProperties(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.l_exclude = bpy.props.CollectionProperty(
            type=CollectionLayerExcludeProperties
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.l_exclude

    def updateLayerVis(self, context):
        target_layer = bpy.data.collections[self.name]
        for objs in target_layer.objects:
            objs.hide_viewport = not (self.value)
            objs.hide_render = not (self.value)

    def updateLayerLock(self, context):
        target_layer = bpy.data.collections[self.name]
        for objs in target_layer.objects:
            objs.hide_select = self.lock

    name: bpy.props.StringProperty(name="Layer Name", default="")

    value: bpy.props.BoolProperty(
        name="Layer Exclude", default=True, update=updateLayerVis
    )

    lock: bpy.props.BoolProperty(
        name="Layer Lock", default=False, update=updateLayerLock
    )


class AconSceneProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Scene.ACON_prop = bpy.props.PointerProperty(type=AconSceneProperty)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.ACON_prop

    toggle_toon_edge: bpy.props.BoolProperty(
        name="Toon Style Edge",
        description="Toggle toon style edge expression",
        default=True,
        update=materials.toggleToonEdge,
    )

    edge_min_line_width: bpy.props.FloatProperty(
        name="Min Line Width",
        description="Adjust the thickness of minimum depth edges",
        subtype="PIXEL",
        default=1,
        min=0,
        max=5,
        step=1,
        update=materials.changeLineProps,
    )

    edge_max_line_width: bpy.props.FloatProperty(
        name="Max Line Width",
        description="Adjust the thickness of maximum depth edges",
        subtype="PIXEL",
        default=1,
        min=0,
        max=5,
        step=1,
        update=materials.changeLineProps,
    )

    edge_line_detail: bpy.props.FloatProperty(
        name="Line Detail",
        description="Amount of edges to be shown. (recommended: 1.2)",
        subtype="FACTOR",
        default=2,
        min=0,
        max=20,
        step=10,
        update=materials.changeLineProps,
    )

    toggle_toon_face: bpy.props.BoolProperty(
        name="Toon Style Face",
        description="Toggle toon style face expression",
        default=True,
        update=materials.toggleToonFace,
    )

    toggle_texture: bpy.props.BoolProperty(
        name="Texture",
        description="Toggle material texture",
        default=True,
        update=materials.toggleTexture,
    )

    toggle_shading: bpy.props.BoolProperty(
        name="Shading",
        description="Toggle shading",
        default=True,
        update=materials.toggleShading,
    )

    toon_shading_depth: bpy.props.EnumProperty(
        name="Toon Color Depth",
        description="Change number of colors used for shading",
        items=[("2", "2 depth", ""), ("3", "3 depth", "")],
        update=materials.changeToonDepth,
    )

    toon_shading_brightness_1: bpy.props.FloatProperty(
        name="Brightness 1",
        description="Change shading brightness (Range: 0 ~ 10)",
        subtype="FACTOR",
        default=3,
        min=0,
        max=10,
        step=1,
        update=materials.changeToonShadingBrightness,
    )

    toon_shading_brightness_2: bpy.props.FloatProperty(
        name="Brightness 2",
        description="Change shading brightness (Range: 0 ~ 10)",
        subtype="FACTOR",
        default=5,
        min=0,
        max=10,
        step=1,
        update=materials.changeToonShadingBrightness,
    )

    view: bpy.props.EnumProperty(
        name="View",
        items=cameras.add_view_items_from_collection,
        update=cameras.goToCustomCamera,
    )

    toggle_sun: bpy.props.BoolProperty(
        name="Sun Light", default=True, update=shadow.toggleSun
    )

    sun_strength: bpy.props.FloatProperty(
        name="Strength",
        description="Sunlight strength in watts per meter squared (W/m^2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=10,
        step=1,
        update=shadow.changeSunStrength,
    )

    toggle_shadow: bpy.props.BoolProperty(
        name="Shadow", default=True, update=shadow.toggleShadow
    )

    sun_rotation_x: bpy.props.FloatProperty(
        name="Altitude",
        description="Adjust sun altitude",
        subtype="ANGLE",
        unit="ROTATION",
        default=radians(60),
        update=shadow.changeSunRotation,
    )

    sun_rotation_z: bpy.props.FloatProperty(
        name="Azimuth",
        description="Adjust sun azimuth",
        subtype="ANGLE",
        unit="ROTATION",
        default=radians(60),
        update=shadow.changeSunRotation,
    )

    image_adjust_brightness: bpy.props.FloatProperty(
        name="Brightness",
        description="Adjust brightness of general image (Range: -1 ~ 1)",
        subtype="FACTOR",
        default=0,
        min=-1,
        max=1,
        step=1,
        update=materials.changeImageAdjustBrightness,
    )

    image_adjust_contrast: bpy.props.FloatProperty(
        name="Contrast",
        description="Adjust contrast of general image (Range: -1 ~ 1)",
        subtype="FACTOR",
        default=0,
        min=-1,
        max=1,
        step=1,
        update=materials.changeImageAdjustContrast,
    )

    image_adjust_color_r: bpy.props.FloatProperty(
        name="Red",
        description="Adjust color balance (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials.changeImageAdjustColor,
    )

    image_adjust_color_g: bpy.props.FloatProperty(
        name="Green",
        description="Adjust color balance (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials.changeImageAdjustColor,
    )

    image_adjust_color_b: bpy.props.FloatProperty(
        name="Blue",
        description="Adjust color balance (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials.changeImageAdjustColor,
    )

    image_adjust_hue: bpy.props.FloatProperty(
        name="Hue",
        description="Adjust hue (Range: 0 ~ 1)",
        subtype="FACTOR",
        default=0.5,
        min=0,
        max=1,
        step=1,
        update=materials.changeImageAdjustHue,
    )

    image_adjust_saturation: bpy.props.FloatProperty(
        name="Saturation",
        description="Adjust saturation (Range: 0 ~ 2)",
        subtype="FACTOR",
        default=1,
        min=0,
        max=2,
        step=1,
        update=materials.changeImageAdjustSaturation,
    )

    selected_objects_str: bpy.props.StringProperty(name="Selected Objects")


class AconWorldProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.World.ACON_prop = bpy.props.PointerProperty(type=AconWorldProperty)

    @classmethod
    def unregister(cls):
        del bpy.types.World.ACON_prop

    hdr: bpy.props.EnumProperty(
        name="HDR Background",
        description="Choose HDR Background",
        items=scenes.add_hdr_items,
        update=scenes.loadHdr,
    )

    clouds_height: bpy.props.FloatProperty(
        name="Clouds Height",
        description="Adjust clouds height",
        default=300,
        min=100,
        max=500,
        step=10,
        update=scenes.changeCloudsHeight,
    )

    clouds_rotation: bpy.props.FloatProperty(
        name="Clouds Rotation",
        description="Adjust clouds rotation",
        subtype="ANGLE",
        unit="ROTATION",
        default=radians(60),
        update=scenes.changeCloudsRotation,
    )


class AconMaterialProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Material.ACON_prop = bpy.props.PointerProperty(
            type=AconMaterialProperty
        )

    @classmethod
    def unregister(cls):
        del bpy.types.Material.ACON_prop

    type: bpy.props.EnumProperty(
        name="Type",
        description="Material Type",
        items=[
            ("Diffuse", "Diffuse", ""),
            ("Mirror", "Reflection", ""),
            ("Glow", "Emission", ""),
            ("Clear", "Transparent", ""),
        ],
        update=materials.changeMaterialType,
    )

    toggle_shadow: bpy.props.BoolProperty(
        name="Shadow", default=True, update=materials.toggleEachShadow
    )

    toggle_shading: bpy.props.BoolProperty(
        name="Shading", default=True, update=materials.toggleEachShading
    )

    toggle_edge: bpy.props.BoolProperty(
        name="Edges", default=True, update=materials.toggleEachEdge
    )


class AconMeshProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Mesh.ACON_prop = bpy.props.PointerProperty(type=AconMeshProperty)

    @classmethod
    def unregister(cls):
        del bpy.types.Mesh.ACON_prop

    def toggle_show_password(self, context):
        if self.show_password:
            self.password_shown = self.password
        else:
            self.password = self.password_shown

    username: bpy.props.StringProperty(name="Username", description="Username")

    password: bpy.props.StringProperty(
        name="Password", description="Password", subtype="PASSWORD"
    )

    password_shown: bpy.props.StringProperty(
        name="Password", description="Password", subtype="NONE"
    )

    show_password: bpy.props.BoolProperty(
        name="Show Password", default=False, update=toggle_show_password
    )

    # TODO: description 달기
    remember_username: bpy.props.BoolProperty(name="Remember Username", default=True)

    login_status: bpy.props.StringProperty(
        name="Login Status",
        description="Login Status",
    )


class AconObjectGroupProperty(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Group", description="Group", default="")


class AconObjectStateProperty(bpy.types.PropertyGroup):

    location: bpy.props.FloatVectorProperty(
        name="location", description="location", subtype="TRANSLATION", unit="LENGTH"
    )
    rotation_euler: bpy.props.FloatVectorProperty(
        name="rotation", description="rotation", subtype="EULER", unit="ROTATION"
    )
    scale: bpy.props.FloatVectorProperty(name="scale", description="scale")


class AconObjectProperty(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Object.ACON_prop = bpy.props.PointerProperty(type=AconObjectProperty)

    @classmethod
    def unregister(cls):
        del bpy.types.Object.ACON_prop

    group: bpy.props.CollectionProperty(type=AconObjectGroupProperty)

    constraint_to_camera_rotation_z: bpy.props.BoolProperty(
        name="Look at me", default=False, update=objects.toggleConstraintToCamera
    )

    use_state: bpy.props.BoolProperty(
        name="Use State", default=False, update=objects.toggleUseState
    )

    state_exists: bpy.props.BoolProperty(
        name="Determine if state is created", default=False
    )

    state_slider: bpy.props.FloatProperty(
        name="State Slider",
        description="Move between begin and end of the state",
        default=0,
        min=0,
        max=1,
        step=1,
        update=objects.moveState,
    )

    state_begin: bpy.props.PointerProperty(type=AconObjectStateProperty)

    state_end: bpy.props.PointerProperty(type=AconObjectStateProperty)


classes = (
    AconWindowManagerProperty,
    CollectionLayerExcludeProperties,
    AconSceneProperty,
    AconWorldProperty,
    AconMaterialProperty,
    AconMeshProperty,
    AconObjectGroupProperty,
    AconObjectStateProperty,
    AconObjectProperty,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
