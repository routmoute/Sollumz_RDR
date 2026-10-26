import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    CollectionProperty,
    PointerProperty,
)

# Import gizmo overlay module for visualization
try:
    from ..gizmos import overlay as gizmo_overlay
except ImportError:
    gizmo_overlay = None


class CAmvClipPlane(PropertyGroup):
    """Represents a clip plane (x, y, z, w)"""
    x: FloatProperty(default=0.0)
    y: FloatProperty(default=0.0)
    z: FloatProperty(default=0.0)
    w: FloatProperty(default=1.0)


class CAmvVolumeProperties(PropertyGroup):
    """Properties for a single AMV volume"""
    
    item_id: IntProperty(
        name="Item ID",
        description="Immutable item identifier from XML order",
        default=0
    )
    
    display_name: StringProperty(
        name="Display Name",
        description="Editable name in Blender (not exported)",
        default=""
    )
    
    enabled: BoolProperty(
        name="Enabled",
        description="Whether this volume is enabled",
        default=True
    )
    
    position: FloatVectorProperty(
        name="Position",
        description="Position of the volume",
        size=3,
        subtype="XYZ",
        default=(0, 0, 0)
    )
    
    rotation: FloatVectorProperty(
        name="Rotation",
        description="Rotation of the volume (in radians)",
        size=3,
        subtype="XYZ",
        default=(0, 0, 0)
    )
    
    scale: FloatVectorProperty(
        name="Scale",
        description="Scale of the volume",
        size=3,
        subtype="XYZ",
        default=(1, 1, 1)
    )
    
    falloff_scale_min: FloatVectorProperty(
        name="Falloff Scale Min",
        size=3,
        subtype="XYZ",
        default=(1, 1, 1)
    )
    
    falloff_scale_max: FloatVectorProperty(
        name="Falloff Scale Max",
        size=3,
        subtype="XYZ",
        default=(1, 1, 1)
    )
    
    sampling_offset_strength: FloatProperty(
        name="Sampling Offset Strength",
        default=0.0
    )
    
    falloff_power: FloatProperty(
        name="Falloff Power",
        default=3.0
    )
    
    distance: FloatProperty(
        name="Distance",
        default=-1.0
    )
    
    cell_count_x: IntProperty(
        name="Cell Count X",
        default=1,
        min=1
    )
    
    cell_count_y: IntProperty(
        name="Cell Count Y",
        default=1,
        min=1
    )
    
    cell_count_z: IntProperty(
        name="Cell Count Z",
        default=1,
        min=1
    )
    
    ui_show_clip_planes: BoolProperty(
        name="Show Clip Planes",
        description="Expand/Collapse clip planes section",
        default=False
    )
    
    clip_plane0: PointerProperty(type=CAmvClipPlane)
    clip_plane1: PointerProperty(type=CAmvClipPlane)
    clip_plane2: PointerProperty(type=CAmvClipPlane)
    clip_plane3: PointerProperty(type=CAmvClipPlane)
    
    clip_plane_blend0: FloatProperty(name="Clip Plane Blend 0", default=1.0)
    clip_plane_blend1: FloatProperty(name="Clip Plane Blend 1", default=1.0)
    clip_plane_blend2: FloatProperty(name="Clip Plane Blend 2", default=1.0)
    clip_plane_blend3: FloatProperty(name="Clip Plane Blend 3", default=1.0)
    
    blending_mode: StringProperty(
        name="Blending Mode",
        default="BM_Lerp"
    )
    
    layer: IntProperty(name="Layer", default=0)
    order: IntProperty(name="Order", default=1)
    
    natural: BoolProperty(name="Natural", default=True)
    attached_to_door: BoolProperty(name="Attached To Door", default=False)
    interior: BoolProperty(name="Interior", default=False)
    exterior: BoolProperty(name="Exterior", default=True)
    vehicle_interior: BoolProperty(name="Vehicle Interior", default=False)
    
    source_folder: StringProperty(
        name="Source Folder",
        default=""
    )
    
    uuid: StringProperty(
        name="UUID",
        default="0"
    )
    
    ipl_hash: StringProperty(
        name="IPL Hash",
        default="0"
    )


class CAmvZoneProperties(PropertyGroup):
    """Properties for an AMV Zone file"""
    
    name: StringProperty(
        name="Name",
        description="Name of the AMV Zone file",
        default="AMV_ZONE"
    )
    
    file_path: StringProperty(
        name="File Path",
        description="Path to the imported AMV Zone file",
        default=""
    )
    
    txd_name: StringProperty(
        name="Texture Dictionary Name",
        description="Name of the texture dictionary",
        default="amv_zone"
    )
    
    volumes: CollectionProperty(
        type=CAmvVolumeProperties,
        name="Volumes"
    )
    
    volume_index: IntProperty(
        name="Volume Index",
        default=0
    )
    
    # Coordinates from ymap entity (not exported, for internal calculations)
    position: FloatVectorProperty(
        name="Position",
        description="Position of MLO entity in ymap - used to calculate volume positions",
        size=3,
        subtype="XYZ",
        default=(0, 0, 0)
    )
    
    rotation: FloatVectorProperty(
        name="Rotation",
        description="Rotation of MLO entity in ymap as quaternion - used to calculate volume rotations",
        size=4,
        subtype="QUATERNION",
        default=(1, 0, 0, 0)
    )


def register():
    """Register AMV Zone scene properties"""
    bpy.types.Scene.amv_zones = CollectionProperty(
        type=CAmvZoneProperties,
        name="AMV Zones"
    )
    bpy.types.Scene.amv_zone_index = IntProperty(
        name="AMV Zone Index",
        default=0
    )
    
    # Register gizmo visualization property
    bpy.types.Scene.show_amv_volume_gizmos = BoolProperty(
        name="Show AMV Volume Gizmos",
        description="Visualize AMV volumes as wireframe boxes in the 3D viewport",
        default=False,
        update=_on_show_amv_volume_gizmos_update
    )


def unregister():
    """Unregister AMV Zone scene properties"""
    del bpy.types.Scene.amv_zones
    del bpy.types.Scene.amv_zone_index
    del bpy.types.Scene.show_amv_volume_gizmos
    
    # Cleanup viewport draw
    if gizmo_overlay is not None:
        gizmo_overlay.unregister_viewport_draw()


def _on_show_amv_volume_gizmos_update(self, context):
    """Callback when show_amv_volume_gizmos is toggled"""
    if gizmo_overlay is None:
        return
    
    if self.show_amv_volume_gizmos:
        gizmo_overlay.register_viewport_draw()
    else:
        gizmo_overlay.unregister_viewport_draw()
    
    # Force viewport redraw
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    region.tag_redraw()
