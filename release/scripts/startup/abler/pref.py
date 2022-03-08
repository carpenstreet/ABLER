import bpy
import sys
from bpy.app.handlers import persistent
from .lib import cameras, shadow, render, scenes
from .lib.materials import materials_setup
from .lib.post_open import change_and_reset_value
from .lib.tracker import tracker


def init_setting(dummy):

    prefs = bpy.context.preferences
    prefs_sys = prefs.system
    prefs_view = prefs.view
    prefs_paths = prefs.filepaths

    if "--background" not in sys.argv and "-b" not in sys.argv:
        try:
            init_screen = bpy.data.screens["ACON3D"].areas[0].spaces[0]
            init_screen.shading.type = "RENDERED"
            init_screen.show_region_header = False
            init_screen.show_region_tool_header = False
            init_screen.show_gizmo = True
            init_screen.show_gizmo_object_translate = True
            init_screen.show_gizmo_object_rotate = True
            init_screen.show_gizmo_object_scale = True
            init_screen.show_gizmo_navigate = False
            init_screen.show_gizmo_tool = True
            init_screen.show_gizmo_context = True

        except:
            print("Failed to find screen 'ACON3D'")

    prefs_sys.use_region_overlap = False
    prefs_view.show_layout_ui = True
    prefs_view.show_navigate_ui = False
    prefs_view.show_developer_ui = False
    prefs_view.show_tooltips_python = False
    prefs_paths.use_load_ui = False


@persistent
def load_handler(dummy):
    tracker.turn_off()
    try:
        init_setting(None)
        cameras.makeSureCameraExists()
        cameras.switchToRendredView()
        cameras.turnOnCameraView(False)
        shadow.setupSharpShadow()
        render.setupBackgroundImagesCompositor()
        materials_setup.applyAconToonStyle()
        for scene in bpy.data.scenes:
            scene.view_settings.view_transform = "Standard"

        scenes.refresh_look_at_me()
        change_and_reset_value()
    finally:
        tracker.turn_on()


def register():
    bpy.app.handlers.load_factory_startup_post.append(init_setting)
    bpy.app.handlers.load_post.append(load_handler)


def unregister():
    bpy.app.handlers.load_post.remove(load_handler)
    bpy.app.handlers.load_factory_startup_post.remove(init_setting)
