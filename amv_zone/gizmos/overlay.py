"""
AMV Zone Volume Visualization Overlay
Displays wireframe boxes for each volume in the 3D viewport
"""

import bpy
import gpu
import math
from mathutils import Matrix, Quaternion, Vector


# Global handle for viewport draw handler
_viewport_draw_handle = None


def get_mesh_from_volume_box():
    """Return a tuple of line vertices for a wireframe box (pairs of vertices forming lines)"""
    return (
        # Bottom face - 4 edges
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5),
        (0.5, -0.5, -0.5), (0.5, 0.5, -0.5),
        (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5),
        # Top face - 4 edges
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5),
        (0.5, -0.5, 0.5), (0.5, 0.5, 0.5),
        (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
        (-0.5, 0.5, 0.5), (-0.5, -0.5, 0.5),
        # Vertical edges connecting top and bottom
        (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5),
        (0.5, -0.5, -0.5), (0.5, -0.5, 0.5),
        (0.5, 0.5, -0.5), (0.5, 0.5, 0.5),
        (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5),
    )


def draw_volume_box(volume, amv_zone_position, amv_zone_rotation, is_selected=False):
    """Draw a single volume as a wireframe box using immediate mode"""
    try:
        # Get volume transform
        volume_position = Vector(volume.position)
        zone_position = Vector(amv_zone_position)
        zone_rotation = Quaternion(amv_zone_rotation).inverted()  # World to local
        
        # Calculate relative position to zone
        relative_position = volume_position - zone_position
        
        # Apply zone rotation to relative position
        rotated_position = zone_rotation @ relative_position
        
        # Scale represents the radius (half-size), so multiply by 2 for full size
        scale = Vector(volume.scale) * 2.0
        
        # Convert rotation from degrees to radians for calculation
        rotation = Vector(volume.rotation)
        # Remap axes: CodeX (X,Y,Z) -> Blender (Y,Z,X)
        rx = math.radians(rotation.y)
        ry = math.radians(rotation.z)
        rz = -math.radians(rotation.x)
        
        # Create rotation matrix for volume
        # CodeX uses YZX order (not XYZ)
        mat_x = Matrix.Rotation(rx, 4, 'X')
        mat_y = Matrix.Rotation(ry, 4, 'Y')
        mat_z = Matrix.Rotation(rz, 4, 'Z')
        volume_rot_matrix = mat_y @ mat_z @ mat_x
        
        # Apply the volume rotation in the zone's local coordinate system.
        total_rotation = zone_rotation.to_matrix().to_4x4() @ volume_rot_matrix
        
        # Create scale matrix (4x4)
        scale_matrix = Matrix([
            [scale.x, 0, 0, 0],
            [0, scale.y, 0, 0],
            [0, 0, scale.z, 0],
            [0, 0, 0, 1]
        ])
        
        # Create transformation matrix: Translate -> Rotate -> Scale
        # Use rotated position relative to zone origin
        transform = Matrix.Translation(rotated_position) @ total_rotation @ scale_matrix
        
        # Get shader
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        
        # Get box mesh vertices
        vertices = get_mesh_from_volume_box()
        
        # Transform vertices
        transformed_vertices = []
        for v in vertices:
            v_vec = Vector(v + (1,))  # Add homogeneous coordinate
            v_transformed = transform @ v_vec
            transformed_vertices.append(v_transformed[:3])
        
        # Set color based on selected and enabled state
        if is_selected:
            color = (1.0, 1.0, 0.0, 1.0)  # Yellow for selected
        elif volume.enabled:
            color = (0.2, 0.8, 0.2, 1.0)  # Green for enabled
        else:
            color = (0.8, 0.2, 0.2, 1.0)  # Red for disabled
        
        # Draw using immediate mode
        gpu.state.line_width_set(2.0 if is_selected else 1.0)
        shader.bind()
        shader.uniform_float("color", color)
        
        # Draw lines in pairs
        from gpu_extras.batch import batch_for_shader
        batch = batch_for_shader(shader, 'LINES', {"pos": transformed_vertices})
        batch.draw(shader)
    except Exception as e:
        import traceback
        print(f"Error drawing AMV volume: {e}")
        traceback.print_exc()


def viewport_draw_callback():
    """Draw callback for viewport"""
    try:
        import bpy
        scene = bpy.context.scene
        
        if not hasattr(scene, 'show_amv_volume_gizmos') or not scene.show_amv_volume_gizmos:
            return
        
        if not hasattr(scene, 'amv_zones') or len(scene.amv_zones) == 0:
            return
        
        gpu.state.blend_set('ALPHA')
        
        # Draw all volumes from all zones
        for amv_zone_idx, amv_zone in enumerate(scene.amv_zones):
            zone_position = amv_zone.position
            zone_rotation = amv_zone.rotation  # Quaternion
            
            for vol_idx, volume in enumerate(amv_zone.volumes):
                # Check if this volume is selected
                is_selected = (amv_zone_idx == scene.amv_zone_index and 
                              vol_idx == amv_zone.volume_index)
                draw_volume_box(volume, zone_position, zone_rotation, is_selected)
        
        gpu.state.blend_set('NONE')
    except Exception as e:
        import traceback
        print(f"Error in viewport draw callback: {e}")
        traceback.print_exc()


def register_viewport_draw():
    """Register the viewport draw handler"""
    global _viewport_draw_handle
    
    if _viewport_draw_handle is None:
        _viewport_draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            viewport_draw_callback,
            (),
            'WINDOW',
            'POST_VIEW'
        )


def unregister_viewport_draw():
    """Unregister the viewport draw handler"""
    global _viewport_draw_handle
    
    if _viewport_draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_viewport_draw_handle, 'WINDOW')
        _viewport_draw_handle = None

