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
import ctypes
import platform
from bpy.app.handlers import persistent
import requests, webbrowser, pickle, os
from .lib.remember_username import (
    delete_remembered_username,
    read_remembered_checkbox,
    remember_username,
    read_remembered_username,
)
from .lib.tracker import tracker


class Acon3dAlertOperator(bpy.types.Operator):
    bl_idname = "acon3d.alert"
    bl_label = ""

    title: bpy.props.StringProperty(name="Title")

    message_1: bpy.props.StringProperty(name="Message")

    message_2: bpy.props.StringProperty(name="Message")

    message_3: bpy.props.StringProperty(name="Message")

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text=self.title)
        if self.message_1:
            row = layout.row()
            row.scale_y = 0.7
            row.label(text=self.message_1)
        if self.message_2:
            row = layout.row()
            row.scale_y = 0.7
            row.label(text=self.message_2)
        if self.message_3:
            row = layout.row()
            row.scale_y = 0.7
            row.label(text=self.message_3)
        layout.separator()
        layout.separator()


class Acon3dModalOperator(bpy.types.Operator):
    bl_idname = "acon3d.modal_operator"
    bl_label = "Login Modal Operator"
    pass_key = {
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "ZERO",
        "ONE",
        "TWO",
        "THREE",
        "FOUR",
        "FIVE",
        "SIX",
        "SEVEN",
        "EIGHT",
        "NINE",
        "BACK_SPACE",
        "SEMI_COLON",
        "PERIOD",
        "COMMA",
        "QUOTE",
        "ACCENT_GRAVE",
        "MINUS",
        "PLUS",
        "SLASH",
        "BACK_SLASH",
        "EQUAL",
        "LEFT_BRACKET",
        "RIGHT_BRACKET",
        "NUMPAD_2",
        "NUMPAD_4",
        "NUMPAD_6",
        "NUMPAD_8",
        "NUMPAD_1",
        "NUMPAD_3",
        "NUMPAD_5",
        "NUMPAD_7",
        "NUMPAD_9",
        "NUMPAD_PERIOD",
        "NUMPAD_SLASH",
        "NUMPAD_ASTERIX",
        "NUMPAD_0",
        "NUMPAD_MINUS",
        "NUMPAD_ENTER",
        "NUMPAD_PLUS",
    }

    def execute(self, context):
        return {"FINISHED"}

    def modal(self, context, event):
        userInfo = bpy.data.meshes.get("ACON_userInfo")

        def char2key(c):
            result = ctypes.windll.User32.VkKeyScanW(ord(c))
            shift_state = (result & 0xFF00) >> 8
            vk_key = result & 0xFF
            return vk_key

        if userInfo and userInfo.ACON_prop.login_status == "SUCCESS":
            return {"FINISHED"}

        if event.type == "LEFTMOUSE":
            bpy.ops.wm.splash("INVOKE_DEFAULT")
        if event.type in self.pass_key:
            if platform.system() == "Windows":
                if event.type == "BACK_SPACE":
                    ctypes.windll.user32.keybd_event(char2key("\b"))
                else:
                    ctypes.windll.user32.keybd_event(char2key(event.unicode))
            elif platform.system() == "Darwin":
                import keyboard

                try:
                    if event.type == "BACK_SPACE":
                        keyboard.send("delete")
                    else:
                        keyboard.write(event.unicode)
                except Exception as e:
                    print(e)
            elif platform.system() == "Linux":
                print("Linux")

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


def requestLogin():

    userInfo = bpy.data.meshes.get("ACON_userInfo")
    prop = userInfo.ACON_prop

    try:

        path = bpy.utils.resource_path("USER")
        path_cookiesFolder = os.path.join(path, "cookies")
        path_cookiesFile = os.path.join(path_cookiesFolder, "acon3d_session")

        if prop.show_password:
            prop.password = prop.password_shown
        else:
            prop.password_shown = prop.password

        cookies_godo = ""
        response_godo = None

        try:
            response_godo = requests.post(
                "https://www.acon3d.com/api/login.php",
                data={"loginId": prop.username, "loginPwd": prop.password},
            )
        except:
            response_godo = None

        try:
            success_msg = response_godo.json()["message"]
            if success_msg != "success":
                response_godo = None
        except:
            response_godo = None

        if response_godo is not None:
            cookies_godo = response_godo.cookies

        response = requests.post(
            "https://api-v2.acon3d.com/auth/acon3d/signin",
            data={"account": prop.username, "password": prop.password},
            cookies=cookies_godo,
        )

        cookie_final = response.cookies

        if response_godo is not None:
            cookie_final = requests.cookies.merge_cookies(
                cookies_godo, response.cookies
            )

        if response.status_code == 200:
            tracker.logged_in(prop.username)
            prop.login_status = "SUCCESS"

            cookiesFile = open(path_cookiesFile, "wb")
            pickle.dump(cookie_final, cookiesFile)
            cookiesFile.close()

            if prop.remember_username:
                remember_username(prop.username)
            else:
                delete_remembered_username()

            prop.username = ""
            prop.password = ""
            prop.password_shown = ""

        else:

            prop.login_status = "FAIL"

    except Exception as e:

        print("Login request has failed.")
        print(e)

    window = bpy.context.window
    width = window.width
    height = window.height
    window.cursor_warp(width / 2, height / 2)

    if prop.login_status != "SUCCESS":
        bpy.ops.acon3d.alert(
            "INVOKE_DEFAULT",
            title="Login failed",
            message_1="If this happens continuously",
            message_2='please contact us at "cs@acon3d.com".',
        )

    def moveMouse():
        window.cursor_warp(width / 2, (height / 2) - 150)

    bpy.app.timers.register(moveMouse, first_interval=0.1)
    bpy.context.window.cursor_set("DEFAULT")


class Acon3dLoginOperator(bpy.types.Operator):
    bl_idname = "acon3d.login"
    bl_label = "Login"
    bl_translation_context = "*"

    def execute(self, context):
        userInfo = bpy.data.meshes.get("ACON_userInfo")
        userInfo.ACON_prop.login_status = "LOADING"
        context.window.cursor_set("WAIT")
        bpy.app.timers.register(requestLogin, first_interval=0.1)
        return {"FINISHED"}


class Acon3dAnchorOperator(bpy.types.Operator):
    bl_idname = "acon3d.anchor"
    bl_label = "Go to link"
    bl_translation_context = "*"

    href: bpy.props.StringProperty(name="href", description="href")

    def execute(self, context):
        webbrowser.open(self.href)

        return {"FINISHED"}


@persistent
def open_credential_modal(dummy):
    prefs = bpy.context.preferences
    prefs.view.show_splash = True

    userInfo = bpy.data.meshes.new("ACON_userInfo")
    prop = userInfo.ACON_prop
    prop.login_status = "IDLE"

    try:
        path = bpy.utils.resource_path("USER")
        path_cookiesFolder = os.path.join(path, "cookies")
        path_cookiesFile = os.path.join(path_cookiesFolder, "acon3d_session")

        if not os.path.isdir(path_cookiesFolder):
            os.mkdir(path_cookiesFolder)

        if not os.path.exists(path_cookiesFile):
            raise
        prop.remember_username = read_remembered_checkbox()

        cookiesFile = open(path_cookiesFile, "rb")
        cookies = pickle.load(cookiesFile)
        cookiesFile.close()
        response = requests.get(
            "https://api-v2.acon3d.com/auth/acon3d/refresh", cookies=cookies
        )

        responseData = response.json()
        token = responseData["accessToken"]

        if token:
            prop.login_status = "SUCCESS"

    except:
        print("Failed to load cookies")

    if userInfo.ACON_prop.login_status != "SUCCESS":
        bpy.ops.acon3d.modal_operator("INVOKE_DEFAULT")

    if prop.remember_username:
        prop.username = read_remembered_username()


@persistent
def hide_header(dummy):
    bpy.data.screens["ACON3D"].areas[0].spaces[0].show_region_header = False


classes = (
    Acon3dAlertOperator,
    Acon3dModalOperator,
    Acon3dLoginOperator,
    Acon3dAnchorOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.load_post.append(open_credential_modal)
    bpy.app.handlers.load_post.append(hide_header)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.load_post.remove(hide_header)
    bpy.app.handlers.load_post.remove(open_credential_modal)
