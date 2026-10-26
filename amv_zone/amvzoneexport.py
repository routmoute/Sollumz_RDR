import bpy
import os
import math
from xml.etree import ElementTree as ET

from .properties.amv_zone import CAmvZoneProperties, CAmvVolumeProperties


def export_amv_zone(amv_zone: CAmvZoneProperties, filepath: str) -> None:
    """Export AMV Zone to XML file"""
    
    # Create root element
    root = ET.Element("AMV__CAMVolumeListSaveData")
    
    # Create amvList
    amv_list = ET.SubElement(root, "amvList")
    amv_list.set("itemType", "iwcGfDA_0x2395C18C")
    
    # Add volumes
    for volume in amv_zone.volumes:
        item = ET.SubElement(amv_list, "Item")
        export_amv_volume(volume, item)
    
    # Add txdName
    txd_name = ET.SubElement(root, "txdName")
    txd_name.text = amv_zone.txd_name if amv_zone.txd_name else "amv_zone"
    
    # Write XML file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")  # Pretty print (Python 3.9+)
    tree.write(filepath, encoding="UTF-8", xml_declaration=True)


def export_amv_volume(volume: CAmvVolumeProperties, item_elem: ET.Element):
    """Export an AMV volume to XML element"""
    
    # enabled
    enabled = ET.SubElement(item_elem, "enabled")
    enabled.set("value", "True" if volume.enabled else "False")
    
    # position
    position = ET.SubElement(item_elem, "position")
    position.set("x", str(volume.position[0]))
    position.set("y", str(volume.position[1]))
    position.set("z", str(volume.position[2]))
    
    # rotation (stored in degrees)
    rotation = ET.SubElement(item_elem, "rotation")
    rotation.set("x", str(volume.rotation[0]))
    rotation.set("y", str(volume.rotation[1]))
    rotation.set("z", str(volume.rotation[2]))
    
    # scale
    scale = ET.SubElement(item_elem, "scale")
    scale.set("x", str(volume.scale[0]))
    scale.set("y", str(volume.scale[1]))
    scale.set("z", str(volume.scale[2]))
    
    # falloffScaleMin
    falloff_min = ET.SubElement(item_elem, "falloffScaleMin")
    falloff_min.set("x", str(volume.falloff_scale_min[0]))
    falloff_min.set("y", str(volume.falloff_scale_min[1]))
    falloff_min.set("z", str(volume.falloff_scale_min[2]))
    
    # falloffScaleMax
    falloff_max = ET.SubElement(item_elem, "falloffScaleMax")
    falloff_max.set("x", str(volume.falloff_scale_max[0]))
    falloff_max.set("y", str(volume.falloff_scale_max[1]))
    falloff_max.set("z", str(volume.falloff_scale_max[2]))
    
    # samplingOffsetStrength
    samp = ET.SubElement(item_elem, "samplingOffsetStrength")
    samp.set("value", str(volume.sampling_offset_strength))
    
    # falloffPower
    falloff_power = ET.SubElement(item_elem, "falloffPower")
    falloff_power.set("value", str(volume.falloff_power))
    
    # distance
    distance = ET.SubElement(item_elem, "distance")
    distance.set("value", str(volume.distance))
    
    # cellCount
    cell_x = ET.SubElement(item_elem, "cellCountX")
    cell_x.set("value", str(volume.cell_count_x))
    
    cell_y = ET.SubElement(item_elem, "cellCountY")
    cell_y.set("value", str(volume.cell_count_y))
    
    cell_z = ET.SubElement(item_elem, "cellCountZ")
    cell_z.set("value", str(volume.cell_count_z))
    
    # clipPlanes
    for i in range(4):
        plane_elem = ET.SubElement(item_elem, f"clipPlane{i}")
        plane_prop = getattr(volume, f"clip_plane{i}")
        plane_elem.set("x", str(plane_prop.x))
        plane_elem.set("y", str(plane_prop.y))
        plane_elem.set("z", str(plane_prop.z))
        plane_elem.set("w", str(plane_prop.w))
    
    # clipPlaneBlends
    for i in range(4):
        blend_elem = ET.SubElement(item_elem, f"clipPlaneBlend{i}")
        blend_val = getattr(volume, f"clip_plane_blend{i}")
        blend_elem.set("value", str(blend_val))
    
    # blendingMode
    blending = ET.SubElement(item_elem, "blendingMode")
    blending.text = volume.blending_mode
    
    # layer
    layer = ET.SubElement(item_elem, "layer")
    layer.set("value", str(volume.layer))
    
    # order
    order = ET.SubElement(item_elem, "order")
    order.set("value", str(volume.order))
    
    # natural
    natural = ET.SubElement(item_elem, "natural")
    natural.set("value", "True" if volume.natural else "False")
    
    # attachedToDoor
    attached_door = ET.SubElement(item_elem, "attachedToDoor")
    attached_door.set("value", "True" if volume.attached_to_door else "False")
    
    # interior
    interior = ET.SubElement(item_elem, "interior")
    interior.set("value", "True" if volume.interior else "False")
    
    # exterior
    exterior = ET.SubElement(item_elem, "exterior")
    exterior.set("value", "True" if volume.exterior else "False")
    
    # vehicleInterior
    vehicle_interior = ET.SubElement(item_elem, "vehicleInterior")
    vehicle_interior.set("value", "True" if volume.vehicle_interior else "False")
    
    # sourceFolder
    source_folder = ET.SubElement(item_elem, "sourceFolder")
    source_folder.text = volume.source_folder
    
    # uuid
    uuid = ET.SubElement(item_elem, "uuid")
    uuid.set("value", volume.uuid)
    
    # iplHash
    ipl_hash = ET.SubElement(item_elem, "iplHash")
    ipl_hash.set("value", str(volume.ipl_hash))
