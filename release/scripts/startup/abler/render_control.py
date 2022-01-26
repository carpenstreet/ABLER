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


import bpy, platform, os, subprocess
from bpy_extras.io_utils import ImportHelper
from .lib import render, cameras, materials
from .lib.tracker import tracker


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


def openDirectory(path):

    if platform.system() == "Windows":

        FILEBROWSER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")
        path = os.path.normpath(path)

        if os.path.isdir(path):
            subprocess.run([FILEBROWSER_PATH, path])
        elif os.path.isfile(path):
            subprocess.run([FILEBROWSER_PATH, "/select,", os.path.normpath(path)])

    elif platform.system() == "Darwin":
        subprocess.call(["open", "-R", path])

    elif platform.system() == "Linux":
        print("Linux")


class Acon3dCameraViewOperator(bpy.types.Operator):
    """Fit Camera Region to Viewport"""

    bl_idname = "acon3d.camera_view"
    bl_label = "Camera View"
    bl_translation_context = "*"

    def execute(self, context):
        cameras.turnOnCameraView()

        return {"FINISHED"}


class Acon3dRenderOperator(bpy.types.Operator, ImportHelper):

    filter_glob: bpy.props.StringProperty(default="", options={"HIDDEN"})
    show_on_completion: bpy.props.BoolProperty(
        name="Show in folder on completion", default=True
    )
    write_still = True
    render_queue = []
    rendering = False
    render_canceled = False
    timer_event = None
    initial_scene = None
    initial_display_type = None

    def pre_render(self, dummy, dum):
        self.rendering = True

    def post_render(self, dummy, dum):
        self.render_queue.pop(0)
        self.rendering = False

    def on_render_cancel(self, dummy, dum):
        self.render_canceled = True

    def on_render_finish(self, context):
        return {"FINISHED"}

    def prepare_queue(self, context):

        for scene in bpy.data.scenes:
            self.render_queue.append(scene)

        return {"RUNNING_MODAL"}

    def prepare_render(self):
        render.setupBackgroundImagesCompositor()
        render.matchObjectVisibility()

    def execute(self, context):

        dirname, basename = os.path.split(os.path.normpath(self.filepath))
        if "." in basename:
            basename = basename.split(".")[0]

        self.filepath = os.path.join(dirname, basename)
        self.render_canceled = False
        self.rendering = False
        self.render_queue = []
        self.initial_scene = context.scene
        self.initial_display_type = context.preferences.view.render_display_type
        self.timer_event = context.window_manager.event_timer_add(
            0.2, window=context.window
        )

        context.preferences.view.render_display_type = "NONE"
        context.window_manager.modal_handler_add(self)

        bpy.app.handlers.render_pre.append(self.pre_render)
        bpy.app.handlers.render_post.append(self.post_render)
        bpy.app.handlers.render_cancel.append(self.on_render_cancel)

        return self.prepare_queue(context)

    def modal(self, context, event):

        if event.type == "TIMER":

            if not self.render_queue or self.render_canceled is True:

                bpy.app.handlers.render_pre.remove(self.pre_render)
                bpy.app.handlers.render_post.remove(self.post_render)
                bpy.app.handlers.render_cancel.remove(self.on_render_cancel)

                context.window_manager.event_timer_remove(self.timer_event)
                context.window.scene = self.initial_scene
                context.preferences.view.render_display_type = self.initial_display_type

                self.report({"INFO"}, "RENDER QUEUE FINISHED")

                bpy.ops.acon3d.alert(
                    "INVOKE_DEFAULT",
                    title="Render Queue Finished",
                    message_1="Rendered images are saved in:",
                    message_2=self.filepath,
                )

                if self.show_on_completion:
                    scene = context.scene
                    filename = (
                        scene.name + "." + scene.render.image_settings.file_format
                    )
                    openDirectory(os.path.join(self.filepath, filename))

                return self.on_render_finish(context)

            elif self.rendering is False:

                qitem = self.render_queue[0]

                base_filepath = os.path.join(self.filepath, qitem.name)
                file_format = qitem.render.image_settings.file_format
                numbered_filepath = base_filepath
                number = 2
                while os.path.isfile(f"{numbered_filepath}.{file_format}"):
                    numbered_filepath = f"{base_filepath} ({number})"
                    number += 1

                qitem.render.filepath = numbered_filepath
                context.window_manager.ACON_prop.scene = qitem.name

                self.prepare_render()

                bpy.ops.render.render("INVOKE_DEFAULT", write_still=self.write_still)

        return {"PASS_THROUGH"}


class Acon3dRenderAllOperator(Acon3dRenderOperator):
    """Render all scenes with full render settings"""

    bl_idname = "acon3d.render_all"
    bl_label = "Save"
    bl_translation_context = "*"

    def prepare_queue(self, context):
        tracker.render_all_scenes()

        super().prepare_queue(context)
        return {"RUNNING_MODAL"}


class Acon3dRenderFullOperator(Acon3dRenderOperator):
    """Render according to the set pixel"""

    bl_idname = "acon3d.render_full"
    bl_label = "Full Render"
    bl_translation_context = "*"

    def prepare_queue(self, context):
        tracker.render_full()

        self.render_queue.append(context.scene)
        return {"RUNNING_MODAL"}


class Acon3dRenderTempSceneOperator(Acon3dRenderOperator):

    temp_scenes = []

    def prepare_render(self):
        render.clearCompositor()
        render.matchObjectVisibility()

    def prepare_queue(self, context):

        scene = context.scene.copy()
        scene.name = context.scene.name + "_shadow"
        self.render_queue.append(scene)
        self.temp_scenes.append(scene)

        prop = scene.ACON_prop
        prop.toggle_texture = False
        prop.toggle_shading = True
        prop.toggle_toon_edge = False
        scene.eevee.use_bloom = False
        scene.render.use_lock_interface = True

        for mat in bpy.data.materials:
            mat.blend_method = "OPAQUE"
            mat.shadow_method = "OPAQUE"
            toonNode = mat.node_tree.nodes.get("ACON_nodeGroup_combinedToon")
            if toonNode:
                toonNode.inputs[1].default_value = 0
                toonNode.inputs[3].default_value = 1

        return {"RUNNING_MODAL"}

    def on_render_finish(self, context):

        for mat in bpy.data.materials:
            materials.setMaterialParametersByType(mat)

        for scene in self.temp_scenes:
            bpy.data.scenes.remove(scene)

        self.temp_scenes.clear()

        return {"FINISHED"}


class Acon3dRenderShadowOperator(Acon3dRenderTempSceneOperator):
    """Renders only shadow according to the set pixel"""

    bl_idname = "acon3d.render_shadow"
    bl_label = "Shadow Render"
    bl_translation_context = "*"

    def prepare_queue(self, context):
        tracker.render_shadow()

        super().prepare_queue(context)
        return {"RUNNING_MODAL"}


class Acon3dRenderLineOperator(Acon3dRenderTempSceneOperator):
    """Renders only lines according to the set pixel"""

    bl_idname = "acon3d.render_line"
    bl_label = "Line Render"
    bl_translation_context = "*"

    def prepare_queue(self, context):
        tracker.render_line()

        super().prepare_queue(context)

        scene = self.render_queue[0]
        scene.name = context.scene.name + "_line"
        prop = scene.ACON_prop
        prop.toggle_shading = False
        prop.toggle_toon_edge = True

        return {"RUNNING_MODAL"}


class Acon3dRenderSnipOperator(Acon3dRenderTempSceneOperator):
    """Render selected objects isolatedly from background"""

    bl_idname = "acon3d.render_snip"
    bl_label = "Snip Render"
    bl_translation_context = "*"

    temp_layer = None
    temp_col = None
    temp_image = None

    @classmethod
    def poll(self, context):
        return len(context.selected_objects)

    def prepare_render(self):

        if len(self.render_queue) == 3:

            render.clearCompositor()

        elif len(self.render_queue) == 2:

            shade_scene = self.temp_scenes[0]
            filename = (
                shade_scene.name + "." + shade_scene.render.image_settings.file_format
            )
            image_path = os.path.join(self.filepath, filename)
            self.temp_image = bpy.data.images.load(image_path)

            for mat in bpy.data.materials:
                materials.setMaterialParametersByType(mat)

            compNodes = render.clearCompositor()
            render.setupBackgroundImagesCompositor(*compNodes)
            render.setupSnipCompositor(
                *compNodes, snip_layer=self.temp_layer, shade_image=self.temp_image
            )

        else:

            bpy.data.collections.remove(self.temp_col)
            bpy.data.images.remove(self.temp_image)
            render.setupBackgroundImagesCompositor()

        render.matchObjectVisibility()

    def prepare_queue(self, context):
        tracker.render_snip()

        super().prepare_queue(context)

        scene = context.scene.copy()
        scene.name = context.scene.name + "_snipped"
        scene.ACON_prop.toggle_shading = False
        self.render_queue.append(scene)
        self.temp_scenes.append(scene)

        layer = scene.view_layers.new("ACON_layer_snip")
        self.temp_layer = layer
        for col in layer.layer_collection.children:
            col.exclude = True

        col_group = bpy.data.collections.new("ACON_group_snip")
        self.temp_col = col_group
        scene.collection.children.link(col_group)
        for obj in context.selected_objects:
            col_group.objects.link(obj)

        scene = context.scene.copy()
        scene.name = context.scene.name + "_full"
        self.render_queue.append(scene)
        self.temp_scenes.append(scene)

        return {"RUNNING_MODAL"}


class Acon3dRenderQuickOperator(Acon3dRenderOperator):
    """Take a snapshot of the active viewport"""

    bl_idname = "acon3d.render_quick"
    bl_label = "Quick Render"
    bl_translation_context = "*"

    initial_selected_objects = []

    def execute(self, context):
        tracker.render_quick()
        return super().execute(context)

    def prepare_queue(self, context):

        filepath = self.filepath
        scene = context.scene
        scene.render.filepath = os.path.join(filepath, scene.name)

        for obj in context.selected_objects:
            self.initial_selected_objects.append(obj)
            obj.select_set(False)

        bpy.ops.render.opengl("INVOKE_DEFAULT", write_still=True)

        return {"RUNNING_MODAL"}

    def on_render_finish(self, context):

        for obj in self.initial_selected_objects:
            obj.select_set(True)

        return {"FINISHED"}


class Acon3dRenderPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""

    bl_idname = "ACON3D_PT_render"
    bl_label = "Render"
    bl_category = "ACON3D"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"BLENDER_RENDER", "BLENDER_EEVEE", "BLENDER_WORKBENCH"}

    def draw_header(self, context):
        layout = self.layout
        layout.label(icon="RENDER_STILL")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        is_camera = False
        for obj in bpy.data.objects:
            if obj.type == "CAMERA":
                is_camera = True
                break

        scene = context.scene

        row = layout.row(align=True)
        row.operator("acon3d.camera_view", text="", icon="RESTRICT_VIEW_OFF")
        row.prop(scene.render, "resolution_x", text="")
        row.prop(scene.render, "resolution_y", text="")

        row = layout.row()
        row.operator("acon3d.render_quick", text="Quick Render", text_ctxt="*")

        if is_camera:
            row.operator("acon3d.render_full", text="Full Render")
            row = layout.row()
            row.operator("acon3d.render_line", text="Line Render")
            row.operator("acon3d.render_shadow", text="Shadow Render")
            row = layout.row()
            row.operator("acon3d.render_all", text="Render All Scenes")
            row.operator("acon3d.render_snip", text="Snip Render")
            row = layout.row()
            row.operator(
                "acon3d.world_diffuse_render", text="Render Diffuse Texture HDR"
            )
            row = layout.row()
            row.operator("acon3d.world_normal_render", text="Render Normal Texture HDR")


class Acon3dWorldDiffuseTextureRenderOperator(bpy.types.Operator):
    """Development"""

    bl_idname = "acon3d.world_diffuse_render"
    bl_label = "Render Diffuse Texture HDR"
    bl_translation_context = "*"

    def execute(self, context):
        from math import radians

        scene = bpy.context.scene

        camera = scene.camera
        camera.location = (0, 0, 2)
        camera.rotation_euler = (radians(90), radians(0), radians(-90))
        camera.data.type = "PANO"
        camera.data.cycles.panorama_type = "EQUIRECTANGULAR"

        render = scene.render
        render.engine = "CYCLES"
        render.resolution_x = 8000
        render.resolution_y = 4000
        render.resolution_percentage = 100
        render.film_transparent = True

        for mat in bpy.data.materials:

            node_tree = mat.node_tree
            nodes = node_tree.nodes

            node_output = None
            node_combinedToon = None

            for node in nodes:
                if node.type == "OUTPUT_MATERIAL":
                    node_output = node

                if node.name == "ACON_nodeGroup_combinedToon":
                    node_combinedToon = node

            if node_combinedToon and node_output:
                node_tree.links.new(node_combinedToon.outputs[0], node_output.inputs[0])

        node_group = bpy.data.node_groups.get("ACON_nodeGroup_combinedToon")

        if node_group:

            node_outline = node_group.nodes.get("ACON_nodeGroup_outline")
            inputs = node_outline.inputs
            inputs[0].default_value = 40
            inputs[1].default_value = 40

        bpy.ops.render.render("INVOKE_DEFAULT")

        return {"FINISHED"}


class Acon3dWorldNormalTextureRenderOperator(bpy.types.Operator):
    """Development"""

    bl_idname = "acon3d.world_normal_render"
    bl_label = "Render Normal Texture HDR"
    bl_translation_context = "*"

    def execute(self, context):
        from math import radians

        scene = bpy.context.scene

        camera = scene.camera
        camera.location = (0, 0, 2)
        camera.rotation_euler = (radians(90), radians(0), radians(-90))
        camera.data.type = "PANO"
        camera.data.cycles.panorama_type = "EQUIRECTANGULAR"

        render = scene.render
        render.engine = "CYCLES"
        render.resolution_x = 8000
        render.resolution_y = 4000
        render.resolution_percentage = 100
        render.film_transparent = True

        for mat in bpy.data.materials:

            node_tree = mat.node_tree
            nodes = node_tree.nodes

            node_output = None

            for node in nodes:
                if node.type == "OUTPUT_MATERIAL":
                    node_output = node

            if not node_output:
                node_output = nodes.new("ShaderNodeOutputMaterial")

            node_normalToColor = nodes.get("ACON_normal_to_color")

            if not node_normalToColor:

                node_group = bpy.data.node_groups.get("ACON_normal_to_color")

                if not node_group:

                    node_group = bpy.data.node_groups.new(
                        "ACON_normal_to_color", "ShaderNodeTree"
                    )

                    nodes = node_group.nodes

                    node_geometry = nodes.new("ShaderNodeNewGeometry")

                    node_vectorMath_1 = nodes.new("ShaderNodeVectorMath")
                    node_vectorMath_1.operation = "MULTIPLY"
                    node_vectorMath_1.inputs[1].default_value = (0.5, 0.5, 0.5)
                    node_group.links.new(
                        node_geometry.outputs[1], node_vectorMath_1.inputs[0]
                    )

                    node_vectorMath_2 = nodes.new("ShaderNodeVectorMath")
                    node_vectorMath_2.operation = "ADD"
                    node_vectorMath_2.inputs[1].default_value = (0.5, 0.5, 0.5)
                    node_group.links.new(
                        node_vectorMath_1.outputs[0], node_vectorMath_2.inputs[0]
                    )

                    node_mixShader = nodes.new("ShaderNodeMixShader")
                    node_group.links.new(
                        node_geometry.outputs[6], node_mixShader.inputs[0]
                    )
                    node_group.links.new(
                        node_vectorMath_2.outputs[0], node_mixShader.inputs[1]
                    )

                    node_transparent = nodes.new("ShaderNodeBsdfTransparent")
                    node_transparent.inputs[0].default_value = (1, 1, 1, 1)
                    node_group.links.new(
                        node_transparent.outputs[0], node_mixShader.inputs[2]
                    )

                    outputs = nodes.new("NodeGroupOutput")
                    node_group.outputs.new("NodeSocketShader", "Shader")
                    node_group.links.new(node_mixShader.outputs[0], outputs.inputs[0])

                    nodes = mat.node_tree.nodes

                node_normalToColor = nodes.new(type="ShaderNodeGroup")
                node_normalToColor.name = "ACON_normal_to_color"
                node_normalToColor.node_tree = node_group

            node_tree.links.new(node_normalToColor.outputs[0], node_output.inputs[0])

        bpy.ops.render.render("INVOKE_DEFAULT")

        return {"FINISHED"}


classes = (
    Acon3dCameraViewOperator,
    Acon3dRenderFullOperator,
    Acon3dRenderAllOperator,
    Acon3dRenderShadowOperator,
    Acon3dRenderLineOperator,
    Acon3dRenderSnipOperator,
    Acon3dRenderQuickOperator,
    Acon3dRenderPanel,
    Acon3dWorldDiffuseTextureRenderOperator,
    Acon3dWorldNormalTextureRenderOperator,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
