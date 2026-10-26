import bpy
from ...sollumz_ui import BasicListHelper, SollumzFileSettingsPanel
from ...sollumz_preferences import (
    get_import_settings,
    get_export_settings,
    SollumzImportSettings,
    SollumzExportSettings
)
from ..utils import get_selected_amv_zone


class SOLLUMZ_UL_AMV_ZONE_LIST(BasicListHelper, bpy.types.UIList):
    bl_idname = "SOLLUMZ_UL_AMV_ZONE_LIST"
    item_icon = "FILE_VOLUME"


class SOLLUMZ_UL_AMV_VOLUME_LIST(BasicListHelper, bpy.types.UIList):
    bl_idname = "SOLLUMZ_UL_AMV_VOLUME_LIST"
    item_icon = "CUBE"
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Draw list item with editable display_name"""
        layout.prop(item, "display_name", text="", emboss=False, icon="CUBE")


class SOLLUMZ_PT_AMV_TOOL_PANEL(bpy.types.Panel):
    """Main Ambient Mask Volume panel"""
    bl_label = "Ambient Mask Volumes"
    bl_idname = "SOLLUMZ_PT_AMV_TOOL_PANEL"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    bl_category = "Sollumz Tools"

    bl_order = 7

    def draw_header(self, context):
        self.layout.label(text="", icon="FILE_VOLUME")

    def draw(self, context):
        pass


class AmvToolChildPanel:
    """Base class for Ambient Mask Volume sub-panels"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = SOLLUMZ_PT_AMV_TOOL_PANEL.bl_idname
    bl_category = SOLLUMZ_PT_AMV_TOOL_PANEL.bl_category


class SOLLUMZ_PT_AMV_ZONE_YMT_PANEL(AmvToolChildPanel, bpy.types.Panel):
    """YMT Import/Export panel for Ambient Mask Volumes"""
    bl_label = "YMTS"
    bl_idname = "SOLLUMZ_PT_AMV_ZONE_YMT_PANEL"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        
        # Draw list with only delete button (no create)
        row = layout.row()
        list_col = row.column()
        list_col.template_list(
            SOLLUMZ_UL_AMV_ZONE_LIST.bl_idname,
            "",
            context.scene,
            "amv_zones",
            context.scene,
            "amv_zone_index",
            rows=3
        )
        
        # Delete button on the right
        side_col = row.column()
        col = side_col.column(align=True)
        col.operator("sollumz.deleteamvzone", text="", icon="REMOVE")
        
        # Import/Export buttons
        row = list_col.row()
        row.operator("sollumz.importamvzone", icon="IMPORT", text="Import ymt.xml")
        row.operator("sollumz.exportamvzone", icon="EXPORT", text="Export ymt.xml")


class SOLLUMZ_PT_AMV_ZONE_YMAP_COORDS(AmvToolChildPanel, bpy.types.Panel):
    """Panel to edit ymap coordinates for AMV Zone"""
    bl_label = "Ymap Entity Coordinates"
    bl_idname = "SOLLUMZ_PT_AMV_ZONE_YMAP_COORDS"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return get_selected_amv_zone(context) is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        selected_amv_zone = get_selected_amv_zone(context)
        
        if not selected_amv_zone:
            return
        
        layout.operator(
            "sollumz.setamvzoneentitytransform",
            text="Copy Active YMAP Entity",
            icon="OBJECT_ORIGIN",
        )
        layout.prop(selected_amv_zone, "position")
        layout.prop(selected_amv_zone, "rotation")


class SOLLUMZ_PT_AMV_ZONE_VOLUMES(AmvToolChildPanel, bpy.types.Panel):
    """Panel to manage Ambient Mask Volumes"""
    bl_label = "Ambient Mask Volumes"
    bl_idname = "SOLLUMZ_PT_AMV_ZONE_VOLUMES"
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return get_selected_amv_zone(context) is not None

    def draw(self, context):
        layout = self.layout
        
        selected_amv_zone = get_selected_amv_zone(context)
        
        if not selected_amv_zone:
            return
        
        # Draw list with add/delete buttons
        row = layout.row()
        list_col = row.column()
        list_col.template_list(
            SOLLUMZ_UL_AMV_VOLUME_LIST.bl_idname,
            "",
            selected_amv_zone,
            "volumes",
            selected_amv_zone,
            "volume_index",
            rows=5
        )
        
        # Add/Delete buttons on the right
        side_col = row.column()
        col = side_col.column(align=True)
        col.operator("sollumz.addamvvolume", text="", icon="ADD")
        col.operator("sollumz.deleteamvvolume", text="", icon="REMOVE")
        
        # Visualization checkbox
        layout.separator()
        layout.prop(context.scene, "show_amv_volume_gizmos")


def get_selected_volume(context):
    """Helper to get the currently selected volume"""
    amv_zone = get_selected_amv_zone(context)
    if amv_zone and amv_zone.volume_index < len(amv_zone.volumes):
        return amv_zone.volumes[amv_zone.volume_index]
    return None


class SOLLUMZ_PT_AMV_VOLUME_PROPERTIES(AmvToolChildPanel, bpy.types.Panel):
    """Panel to edit properties of the selected Ambient Mask Volume"""
    bl_label = "Volume Properties"
    bl_idname = "SOLLUMZ_PT_AMV_VOLUME_PROPERTIES"
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return get_selected_volume(context) is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        volume = get_selected_volume(context)
        
        if not volume:
            return
        
        # Basic properties
        layout.prop(volume, "enabled")
        layout.prop(volume, "position")
        layout.prop(volume, "rotation")
        layout.prop(volume, "scale")
        
        layout.separator()
        
        # Falloff properties
        layout.prop(volume, "falloff_scale_min")
        layout.prop(volume, "falloff_scale_max")
        layout.prop(volume, "falloff_power")
        layout.prop(volume, "sampling_offset_strength")
        layout.prop(volume, "distance")
        
        layout.separator()
        
        # Cell counts
        layout.prop(volume, "cell_count_x")
        layout.prop(volume, "cell_count_y")
        layout.prop(volume, "cell_count_z")
        
        layout.separator()
        
        # Blending and layer properties
        layout.prop(volume, "blending_mode")
        layout.prop(volume, "layer")
        layout.prop(volume, "order")
        
        layout.separator()
        
        # Boolean flags
        layout.prop(volume, "natural")
        layout.prop(volume, "attached_to_door")
        layout.prop(volume, "interior")
        layout.prop(volume, "exterior")
        layout.prop(volume, "vehicle_interior")
        
        layout.separator()
        
        # Clip planes (collapsible)
        row = layout.row()
        row.prop(volume, "ui_show_clip_planes", text="Clip Planes", toggle=True, icon="TRIA_DOWN" if volume.ui_show_clip_planes else "TRIA_RIGHT")
        
        if volume.ui_show_clip_planes:
            for i in range(4):
                box = layout.box()
                plane = getattr(volume, f"clip_plane{i}")
                row = box.row()
                row.label(text=f"Plane {i}")
                plane_col = row.column()
                plane_col.prop(plane, "x", text="X")
                plane_col.prop(plane, "y", text="Y")
                plane_col.prop(plane, "z", text="Z")
                plane_col.prop(plane, "w", text="W")
                box.prop(volume, f"clip_plane_blend{i}", text=f"Blend {i}")
        
        layout.separator()
        layout.prop(volume, "source_folder")
        layout.prop(volume, "uuid")
        layout.prop(volume, "ipl_hash")


class SOLLUMZ_PT_import_amv_zone(bpy.types.Panel, SollumzFileSettingsPanel):
    """Import settings for AMV Zone files"""
    bl_options = {"HIDE_HEADER"}
    operator_id = "sollumz.importamvzone"

    def get_settings(self, context: bpy.types.Context) -> SollumzImportSettings:
        return get_import_settings(context)

    def draw_settings(self, layout: bpy.types.UILayout, settings: SollumzImportSettings):
        layout.use_property_split = False
        # Import settings can be added here in the future


class SOLLUMZ_PT_export_amv_zone(bpy.types.Panel, SollumzFileSettingsPanel):
    """Export settings for AMV Zone files"""
    bl_options = {"HIDE_HEADER"}
    operator_id = "sollumz.exportamvzone"

    def get_settings(self, context: bpy.types.Context) -> SollumzExportSettings:
        return get_export_settings(context)

    def draw_settings(self, layout: bpy.types.UILayout, settings: SollumzExportSettings):
        layout.use_property_split = False
        # Export settings can be added here in the future
