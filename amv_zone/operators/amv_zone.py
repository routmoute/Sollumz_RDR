import bpy
import traceback
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import StringProperty, BoolProperty
from ...sollumz_helper import SOLLUMZ_OT_base
from ..utils import get_selected_amv_zone
from ..amvzoneimport import import_amv_zone
from ..amvzoneexport import export_amv_zone


class SOLLUMZ_OT_create_amv_zone(SOLLUMZ_OT_base, bpy.types.Operator):
    """Add an AMV Zone to the project"""
    bl_idname = "sollumz.createamvzone"
    bl_label = "Create AMV Zone"

    def run(self, context):
        item = context.scene.amv_zones.add()
        index = len(context.scene.amv_zones)
        item.name = f"AMV_ZONE.{index}"
        context.scene.amv_zone_index = index - 1

        return True


class SOLLUMZ_OT_set_amv_zone_entity_transform(SOLLUMZ_OT_base, bpy.types.Operator):
    """Copy the active object's transform to the selected AMV Zone"""
    bl_idname = "sollumz.setamvzoneentitytransform"
    bl_label = "Copy Active YMAP Entity"

    @classmethod
    def poll(cls, context):
        return get_selected_amv_zone(context) is not None and context.active_object is not None

    def run(self, context):
        amv_zone = get_selected_amv_zone(context)
        active_object = context.active_object
        if amv_zone is None or active_object is None:
            return False

        world_transform = active_object.matrix_world
        amv_zone.position = world_transform.translation
        amv_zone.rotation = world_transform.to_quaternion()
        return True


class SOLLUMZ_OT_delete_amv_zone(SOLLUMZ_OT_base, bpy.types.Operator):
    """Delete an AMV Zone from the project"""
    bl_idname = "sollumz.deleteamvzone"
    bl_label = "Delete AMV Zone"

    @classmethod
    def poll(cls, context):
        return len(context.scene.amv_zones) > 0

    def run(self, context):
        context.scene.amv_zones.remove(context.scene.amv_zone_index)
        context.scene.amv_zone_index = max(context.scene.amv_zone_index - 1, 0)

        return True


class SOLLUMZ_OT_import_amv_zone(SOLLUMZ_OT_base, ImportHelper, bpy.types.Operator):
    """Import AMV Zone YMT file"""
    bl_idname = "sollumz.importamvzone"
    bl_label = "Import ymt.xml"
    bl_action = "Import an AMV Zone"
    
    filename_ext = ".xml"
    filter_glob: StringProperty(default="*amv_zone*.xml", options={"HIDDEN"})

    def run(self, context):
        try:
            import_amv_zone(self.filepath)
            self.message(f"Successfully imported: {self.filepath}")
            return True
        except Exception as e:
            self.error(f"Error during import: {traceback.format_exc()}")
            return False


class SOLLUMZ_OT_export_amv_zone(SOLLUMZ_OT_base, bpy.types.Operator):
    """Export the selected AMV Zone"""
    bl_idname = "sollumz.exportamvzone"
    bl_label = "Export ymt.xml"
    bl_action = "Export an AMV Zone"
    
    filter_glob: StringProperty(default="*amv_zone*.xml", options={"HIDDEN"})

    directory: bpy.props.StringProperty(
        name="Output directory",
        description="Select export output directory",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        pass

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    @classmethod
    def poll(cls, context):
        num_amv_zones = len(context.scene.amv_zones)
        return num_amv_zones > 0 and context.scene.amv_zone_index < num_amv_zones

    def run(self, context):
        try:
            selected_amv_zone = get_selected_amv_zone(context)
            if not selected_amv_zone:
                self.error("No AMV Zone selected")
                return False
            
            # Generate filename
            filename = f"{selected_amv_zone.name}.ymt.pso.xml" if selected_amv_zone.name else "amv_zone.ymt.pso.xml"
            filepath = os.path.join(self.directory, filename)
            
            # Export
            export_amv_zone(selected_amv_zone, filepath)
            self.message(f"Successfully exported to: {filepath}")
            return True
        except Exception as e:
            self.error(f"Error during export: {traceback.format_exc()}")
            return False


class SOLLUMZ_OT_add_amv_volume(SOLLUMZ_OT_base, bpy.types.Operator):
    """Add a new Ambient Mask Volume to the selected AMV Zone"""
    bl_idname = "sollumz.addamvvolume"
    bl_label = "Add Ambient Mask Volume"

    @classmethod
    def poll(cls, context):
        return get_selected_amv_zone(context) is not None

    def run(self, context):
        selected_amv_zone = get_selected_amv_zone(context)
        if not selected_amv_zone:
            return False
        
        # Calculate next item_id (max + 1)
        max_item_id = -1
        for volume in selected_amv_zone.volumes:
            if volume.item_id > max_item_id:
                max_item_id = volume.item_id
        next_item_id = max_item_id + 1
        
        volume = selected_amv_zone.volumes.add()
        volume.item_id = next_item_id
        volume.display_name = f"volume.{next_item_id}"
        selected_amv_zone.volume_index = len(selected_amv_zone.volumes) - 1
        
        return True


class SOLLUMZ_OT_delete_amv_volume(SOLLUMZ_OT_base, bpy.types.Operator):
    """Delete the selected Ambient Mask Volume from the AMV Zone"""
    bl_idname = "sollumz.deleteamvvolume"
    bl_label = "Delete Ambient Mask Volume"

    @classmethod
    def poll(cls, context):
        selected_amv_zone = get_selected_amv_zone(context)
        return selected_amv_zone is not None and len(selected_amv_zone.volumes) > 0

    def run(self, context):
        selected_amv_zone = get_selected_amv_zone(context)
        if not selected_amv_zone or len(selected_amv_zone.volumes) == 0:
            return False
        
        selected_amv_zone.volumes.remove(selected_amv_zone.volume_index)
        selected_amv_zone.volume_index = max(selected_amv_zone.volume_index - 1, 0)
        
        return True
