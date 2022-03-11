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

# <pep8 compliant>

import re
import platform

import bpy

from .utils import compatibility as compat

if compat.check_version(2, 80, 0) >= 0:
    import gpu


CUSTOM_MOUSE_IMAGE_BASE_NAME = "[Screencast Keys] Custom Mouse Image Base"
CUSTOM_MOUSE_IMAGE_OVERLAY_LEFT_MOUSE_NAME = "[Screencast Keys] Custom Mouse Image Overlay Left Mouse"
CUSTOM_MOUSE_IMAGE_OVERLAY_RIGHT_MOUSE_NAME = "[Screencast Keys] Custom Mouse Image Overlay Right Mouse"
CUSTOM_MOUSE_IMAGE_OVERLAY_MIDDLE_MOUSE_NAME = "[Screencast Keys] Custom Mouse Image Overlay Middle Mouse"


def output_debug_log():
    prefs = compat.get_user_preferences(bpy.context).addons[__package__].preferences

    return prefs.output_debug_log


def debug_print(s):
    """
    Print message to console in debugging mode
    """

    if output_debug_log():
        print(s)


def ensure_custom_mouse_images():
    image_names = [
        CUSTOM_MOUSE_IMAGE_BASE_NAME,
        CUSTOM_MOUSE_IMAGE_OVERLAY_LEFT_MOUSE_NAME,
        CUSTOM_MOUSE_IMAGE_OVERLAY_RIGHT_MOUSE_NAME,
        CUSTOM_MOUSE_IMAGE_OVERLAY_MIDDLE_MOUSE_NAME,
    ]

    for name in image_names:
        if name in bpy.data.images:
            image = bpy.data.images[name]
            image.preview_ensure()
            image.gl_load()


def fix_modifier_display_text(name):
    # Remove left and right identifier.
    fixed_name = re.sub("(Left |Right )", "", name)

    mappings = {
        "Windows": {
            "Shift": "Shift",
            "Ctrl": "Ctrl",
            "Alt": "Alt",
            "OS Key": "Windows Key",
        },
        "Darwin": {
            "Shift": "Shift",
            "Ctrl": "Control",
            "Alt": "Option",
            "OS Key": "Command",
        },
        "Linux": {
            "Shift": "Shift",
            "Ctrl": "Ctrl",
            "Alt": "Alt",
            "OS Key": "OS Key",
        }
    }

    # Change to the platform specific text.
    system = platform.system()
    if system not in mappings:
        return fixed_name
    if fixed_name not in mappings[system]:
        return fixed_name

    fixed_name = mappings[system][fixed_name]
    return fixed_name


def use_3d_polyline(line_thickness=1.0):
    if compat.check_version(2, 80, 0) < 0:
        return False

    if line_thickness < 1.5:
        return False

    system = platform.system()
    if system == 'Darwin':
        try:
            gpu.shader.from_builtin('3D_POLYLINE_UNIFORM_COLOR')
            return True
        except ValueError:
            return False

    return False
