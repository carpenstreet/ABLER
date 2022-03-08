import bpy
from . import cameras
from .tracker import tracker


def toggleConstraintToCamera(self, context):

    cameras.makeSureCameraExists()

    # repr returns canonical string representation of the object.
    # For many object types, including most builtins, eval(repr(obj)) == obj
    obj = eval(repr(self).rsplit(".", 1)[0])

    look_at_me = obj.ACON_prop.constraint_to_camera_rotation_z
    if look_at_me:
        tracker.look_at_me()

    setConstraintToCameraByObject(obj, context)


def setConstraintToCameraByObject(obj, context=None):

    if not context:
        context = bpy.context

    look_at_me = obj.ACON_prop.constraint_to_camera_rotation_z

    objects = context.selected_objects.copy()
    objects.append(obj)

    for object in objects:

        prop = object.ACON_prop
        const = object.constraints.get("ACON_const_copyRotation")

        if look_at_me:

            if not const:
                const = object.constraints.new(type="COPY_ROTATION")
                const.name = "ACON_const_copyRotation"
                const.use_x = False
                const.use_y = False
                const.use_z = True

            const.target = context.scene.camera
            const.mute = False

        elif const:

            const.mute = True

        if prop.constraint_to_camera_rotation_z != look_at_me:
            prop.constraint_to_camera_rotation_z = look_at_me


def step(edge0: tuple[float], edge1: tuple[float], x: float) -> tuple[float]:
    return tuple(edge0[i] + ((edge1[i] - edge0[i]) * x) for i in [0, 1, 2])


def toggleUseState(self, context):

    use_state = self.use_state

    prop = context.object.ACON_prop
    if prop.use_state:
        tracker.use_state_on()
    else:
        tracker.use_state_off()

    if use_state:

        for obj in context.selected_objects:

            prop = obj.ACON_prop

            if obj == context.object or not prop.use_state:

                if not prop.state_exists:

                    for att in ["location", "rotation_euler", "scale"]:

                        vector = getattr(obj, att)
                        setattr(prop.state_begin, att, vector)
                        setattr(prop.state_end, att, vector)

                    prop.state_exists = True

            if not prop.use_state:

                prop.use_state = True

        prop.state_slider = 1

    else:

        context.object.ACON_prop.state_slider = 0

        for obj in context.selected_objects:

            prop = obj.ACON_prop

            if prop.use_state:

                prop.use_state = False


def moveState(self, context):

    state_slider = self.state_slider

    for obj in context.selected_objects:

        prop = obj.ACON_prop

        if obj != context.object and not prop.use_state:
            continue

        for att in ["location", "rotation_euler", "scale"]:

            vector_begin = getattr(prop.state_begin, att)
            vector_end = getattr(prop.state_end, att)
            vector_mid = step(vector_begin, vector_end, state_slider)

            setattr(obj, att, vector_mid)

        if prop.state_slider != state_slider:
            prop.state_slider = state_slider
