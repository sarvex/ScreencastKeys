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


bl_info = {
    "name": "Screencast Keys",
    "author": "Paulo Gomes, Bart Crouch, John E. Herrenyo, "
              "Gaia Clary, Pablo Vazquez, chromoly, Nutti, Hawkpath",
    "version": (3, 2, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar > Screencast Keys",
    "warning": "",
    "description": "Display keys pressed in Blender",
    "wiki_url": "https://github.com/nutti/Screencast-Keys",
    "doc_url": "https://github.com/nutti/Screencast-Keys",
    "tracker_url": "https://github.com/nutti/Screencast-Keys",
    "category": "System",
}


if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    utils.bl_class_registry.BlClassRegistry.cleanup()
    importlib.reload(preferences)
    importlib.reload(ops)
    importlib.reload(ui)
    importlib.reload(common)
else:
    import bpy
    from . import utils
    from . import preferences
    from . import ops
    from . import ui
    from . import common

import os

import bpy


addon_keymaps = []


@bpy.app.handlers.persistent
def load_pre_handler(scene):
    """SK_OT_ScreencastKeys operation will remain running status when new .blend file is loaded.
       It seems that events from timer is not issued after loading .blend file, but we could not
       find the essential cause.
       Instead, we solve this issue by using handler called at load_pre (i.e. before loading
       .blend file)."""

    if ops.SK_OT_ScreencastKeys.is_running():
        # Call invoke method also cleanup event handlers and draw handlers, so on.
        bpy.ops.wm.sk_screencast_keys('INVOKE_REGION_WIN')


@bpy.app.handlers.persistent
def auto_restart_handler(scene):
    context = bpy.context
    wm = context.window_manager

    if not context.window:
        return
    if not context.area:
        return
    if not context.region:
        return

    if wm.enable_screencast_keys:
        return
    
    need_restart = True
    addrs = []
    for window in wm.windows:
        addr = window.as_pointer()
        addrs.append(addr)
        if addr in ops.SK_OT_ScreencastKeys.window_addr_store:
            need_restart = False

    if need_restart:
        print("Try to Restart Screencast Keys")
        override = {}
        if not (context.screen and context.scene and
                context.screen == window.screen and
                context.scene == window.scene):
            window = context.window
            screen = window.screen
            scene = window.scene
            override = {
                "window": window,
                "screen": screen,
                "scene": scene,
                "area": None,
                "region": None,
            }

        override_context = context.copy()
        override_context.update(override)

        op_context = 'INVOKE_DEFAULT'
        args = [override_context, op_context]

        print("Restarting Screencast Keys...")
        from _bpy import ops as ops_module

        op = getattr(getattr(bpy.ops, "wm"), "sk_screencast_keys")
        BPyOpsSubModOp = op.__class__
        op_call = ops_module.call
        C_dict, C_exec, C_undo = BPyOpsSubModOp._parse_args(args)
        ret = op_call(op.idname_py(), C_dict, {}, C_exec, C_undo)


def register_updater(bl_info):
    config = utils.addon_updator.AddonUpdatorConfig()
    config.owner = "nutti"
    config.repository = "Screencast-Keys"
    config.current_addon_path = os.path.dirname(os.path.realpath(__file__))
    config.branches = ["master"]
    config.addon_directory = config.current_addon_path[:config.current_addon_path.rfind("/")]
    config.min_release_version = bl_info["version"]
    config.target_addon_path = "src/screencast_keys"
    updater = utils.addon_updator.AddonUpdatorManager.get_instance()
    updater.init(bl_info, config)


def register_shortcut_key():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.sk_screencast_keys", 'C', 'PRESS',
                                  shift=True, alt=True)
        addon_keymaps.append((km, kmi))


def unregister_shortcut_key():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    register_updater(bl_info)
    # TODO: Register by BlClassRegistry
    bpy.utils.register_class(preferences.DisplayEventTextAliasProperties)
    utils.bl_class_registry.BlClassRegistry.register()
    register_shortcut_key()
    #bpy.app.handlers.load_pre.append(load_pre_handler)
    bpy.app.handlers.depsgraph_update_pre.append(auto_restart_handler)

    # Apply preferences of the panel location.
    context = bpy.context
    prefs = utils.compatibility.get_user_preferences(context).addons[__package__].preferences
    # Only default panel location is available in < 2.80
    if utils.compatibility.check_version(2, 80, 0) < 0:
        prefs.panel_space_type = 'VIEW_3D'
        prefs.panel_category = "Screencast Key"
    preferences.SK_Preferences.panel_category_update_fn(prefs, context)
    preferences.SK_Preferences.panel_space_type_update_fn(prefs, context)

    for event in list(ops.EventType):
        item = prefs.display_event_text_aliases_props.add()
        item.event_id = event.name
        item.default_text = ops.EventType.names[event.name]


def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(auto_restart_handler)
    #bpy.app.handlers.load_pre.remove(load_pre_handler)
    unregister_shortcut_key()
    # TODO: Unregister by BlClassRegistry
    utils.bl_class_registry.BlClassRegistry.unregister()
    bpy.utils.unregister_class(preferences.DisplayEventTextAliasProperties)


if __name__ == "__main__":
    register()
