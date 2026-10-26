import bpy
import os
import math
from xml.etree import ElementTree as ET

from .properties.amv_zone import CAmvZoneProperties, CAmvVolumeProperties


def import_amv_zone(filepath: str) -> CAmvZoneProperties:
    """Import AMV Zone from XML file"""
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Parse XML
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # Create AMV Zone item in scene
    scene = bpy.context.scene
    amv_zone = scene.amv_zones.add()
    
    # Get filename without extension
    filename = os.path.basename(filepath)
    amv_zone.name = filename.replace(".ymt.pso.xml", "").replace(".xml", "")
    amv_zone.file_path = filepath
    
    # Find txdName
    txd_name_elem = root.find("txdName")
    if txd_name_elem is not None and txd_name_elem.text:
        amv_zone.txd_name = txd_name_elem.text
    
    # Parse volumes
    amv_list = root.find("amvList")
    if amv_list is not None:
        for item_id, item_elem in enumerate(amv_list.findall("Item")):
            volume = amv_zone.volumes.add()
            volume.item_id = item_id
            volume.display_name = f"volume.{item_id}"
            parse_amv_volume(item_elem, volume)
    
    # Set as current
    scene.amv_zone_index = len(scene.amv_zones) - 1


def parse_amv_volume(item_elem: ET.Element, volume: CAmvVolumeProperties):
    """Parse an AMV volume from XML element"""
    
    # enabled
    enabled_elem = item_elem.find("enabled")
    if enabled_elem is not None:
        volume.enabled = enabled_elem.get("value") == "True"
    
    # position
    pos_elem = item_elem.find("position")
    if pos_elem is not None:
        volume.position = (
            float(pos_elem.get("x", 0)),
            float(pos_elem.get("y", 0)),
            float(pos_elem.get("z", 0))
        )
    
    # rotation (keep in degrees for UI display)
    rot_elem = item_elem.find("rotation")
    if rot_elem is not None:
        rx = float(rot_elem.get("x", 0))
        ry = float(rot_elem.get("y", 0))
        rz = float(rot_elem.get("z", 0))
        volume.rotation = (rx, ry, rz)
    
    # scale
    scale_elem = item_elem.find("scale")
    if scale_elem is not None:
        volume.scale = (
            float(scale_elem.get("x", 1)),
            float(scale_elem.get("y", 1)),
            float(scale_elem.get("z", 1))
        )
    
    # falloffScaleMin
    falloff_min_elem = item_elem.find("falloffScaleMin")
    if falloff_min_elem is not None:
        volume.falloff_scale_min = (
            float(falloff_min_elem.get("x", 1)),
            float(falloff_min_elem.get("y", 1)),
            float(falloff_min_elem.get("z", 1))
        )
    
    # falloffScaleMax
    falloff_max_elem = item_elem.find("falloffScaleMax")
    if falloff_max_elem is not None:
        volume.falloff_scale_max = (
            float(falloff_max_elem.get("x", 1)),
            float(falloff_max_elem.get("y", 1)),
            float(falloff_max_elem.get("z", 1))
        )
    
    # samplingOffsetStrength
    samp_elem = item_elem.find("samplingOffsetStrength")
    if samp_elem is not None:
        volume.sampling_offset_strength = float(samp_elem.get("value", 0))
    
    # falloffPower
    falloff_power_elem = item_elem.find("falloffPower")
    if falloff_power_elem is not None:
        volume.falloff_power = float(falloff_power_elem.get("value", 1))
    
    # distance
    distance_elem = item_elem.find("distance")
    if distance_elem is not None:
        volume.distance = float(distance_elem.get("value", -1))
    
    # cellCount
    cell_x_elem = item_elem.find("cellCountX")
    if cell_x_elem is not None:
        volume.cell_count_x = int(cell_x_elem.get("value", 1))
    
    cell_y_elem = item_elem.find("cellCountY")
    if cell_y_elem is not None:
        volume.cell_count_y = int(cell_y_elem.get("value", 1))
    
    cell_z_elem = item_elem.find("cellCountZ")
    if cell_z_elem is not None:
        volume.cell_count_z = int(cell_z_elem.get("value", 1))
    
    # clipPlanes
    for i in range(4):
        plane_elem = item_elem.find(f"clipPlane{i}")
        if plane_elem is not None:
            plane_prop = getattr(volume, f"clip_plane{i}")
            plane_prop.x = float(plane_elem.get("x", 0))
            plane_prop.y = float(plane_elem.get("y", 0))
            plane_prop.z = float(plane_elem.get("z", 0))
            plane_prop.w = float(plane_elem.get("w", 1))
    
    # clipPlaneBlends
    for i in range(4):
        blend_elem = item_elem.find(f"clipPlaneBlend{i}")
        if blend_elem is not None:
            setattr(volume, f"clip_plane_blend{i}", float(blend_elem.get("value", 1)))
    
    # blendingMode
    blend_elem = item_elem.find("blendingMode")
    if blend_elem is not None and blend_elem.text:
        volume.blending_mode = blend_elem.text
    
    # layer
    layer_elem = item_elem.find("layer")
    if layer_elem is not None:
        volume.layer = int(layer_elem.get("value", 0))
    
    # order
    order_elem = item_elem.find("order")
    if order_elem is not None:
        volume.order = int(order_elem.get("value", 0))
    
    # Flags
    natural_elem = item_elem.find("natural")
    if natural_elem is not None:
        volume.natural = natural_elem.get("value") == "True"
    
    attached_door_elem = item_elem.find("attachedToDoor")
    if attached_door_elem is not None:
        volume.attached_to_door = attached_door_elem.get("value") == "True"
    
    interior_elem = item_elem.find("interior")
    if interior_elem is not None:
        volume.interior = interior_elem.get("value") == "True"
    
    exterior_elem = item_elem.find("exterior")
    if exterior_elem is not None:
        volume.exterior = exterior_elem.get("value") == "True"
    
    vehicle_interior_elem = item_elem.find("vehicleInterior")
    if vehicle_interior_elem is not None:
        volume.vehicle_interior = vehicle_interior_elem.get("value") == "True"
    
    # sourceFolder
    source_elem = item_elem.find("sourceFolder")
    if source_elem is not None and source_elem.text:
        volume.source_folder = source_elem.text
    
    # uuid
    uuid_elem = item_elem.find("uuid")
    if uuid_elem is not None:
        volume.uuid = uuid_elem.get("value", "0")
    
    # iplHash
    ipl_elem = item_elem.find("iplHash")
    if ipl_elem is not None:
        volume.ipl_hash = ipl_elem.get("value", "0")
