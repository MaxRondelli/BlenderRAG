import bpy
import bmesh
from mathutils import Vector

def create_photo_frame(
    outer_width=0.3,      # Outer width of frame (meters)
    outer_height=0.4,     # Outer height of frame (meters)
    frame_depth=0.03,     # Depth/thickness of frame (reduced for modern look)
    frame_width=0.03,     # Width of frame border (reduced for sleeker profile)
    bevel_segments=2,     # Number of stepped bevels (reduced for cleaner look)
    material_color=(0.7, 0.7, 0.75, 1.0)  # Brushed aluminum color (RGBA)
):
    """
    Create a decorative photo frame with stepped profile in Blender
    
    Parameters:
    - outer_width: Total width of the frame
    - outer_height: Total height of the frame
    - frame_depth: How deep/thick the frame is
    - frame_width: Width of the frame border around the picture opening
    - bevel_segments: Number of decorative steps in the frame profile
    - material_color: RGBA color for the frame material
    """
    
    # Calculate inner dimensions (picture opening)
    inner_width = outer_width - (2 * frame_width)
    inner_height = outer_height - (2 * frame_width)
    
    # Create the frame profile curve (cross-section)
    curve_data = bpy.data.curves.new(name="FrameProfile", type='CURVE')
    curve_data.dimensions = '2D'
    curve_data.fill_mode = 'BOTH'
    
    # Create a spline for the profile
    spline = curve_data.splines.new('BEZIER')
    
    # Define the stepped profile points
    profile_points = []
    
    # Start from front edge
    profile_points.append((0, 0))
    
    # Create stepped bevel profile
    step_depth = frame_depth / (bevel_segments + 1)
    step_width = frame_width / (bevel_segments + 1)
    
    for i in range(bevel_segments):
        # Step back
        profile_points.append((step_width * (i + 0.5), step_depth * i))
        # Step in
        profile_points.append((step_width * (i + 1), step_depth * i))
        # Step down
        profile_points.append((step_width * (i + 1), step_depth * (i + 1)))
    
    # Final points to complete the profile
    profile_points.append((frame_width, frame_depth))
    profile_points.append((frame_width, frame_depth - 0.005))
    profile_points.append((0, frame_depth - 0.005))
    profile_points.append((0, 0))
    
    # Set bezier points
    spline.bezier_points.add(len(profile_points) - 1)
    for i, point in enumerate(profile_points):
        bp = spline.bezier_points[i]
        bp.co = (point[0], 0, point[1])
        bp.handle_left_type = 'VECTOR'
        bp.handle_right_type = 'VECTOR'
    
    spline.use_cyclic_u = True
    
    # Create profile object
    profile_obj = bpy.data.objects.new("FrameProfile", curve_data)
    bpy.context.collection.objects.link(profile_obj)
    
    # Create the frame path (rectangle for the frame outline)
    path_data = bpy.data.curves.new(name="FramePath", type='CURVE')
    path_data.dimensions = '3D'
    
    # Create rectangular path
    path_spline = path_data.splines.new('POLY')
    
    # Define rectangle points (centered at origin)
    half_w = outer_width / 2
    half_h = outer_height / 2
    
    path_points = [
        (-half_w, half_h, 0),
        (half_w, half_h, 0),
        (half_w, -half_h, 0),
        (-half_w, -half_h, 0),
    ]
    
    path_spline.points.add(len(path_points) - 1)
    for i, point in enumerate(path_points):
        path_spline.points[i].co = (point[0], point[1], point[2], 1)
    
    path_spline.use_cyclic_u = True
    
    # Set the profile as bevel object for the path
    path_data.bevel_mode = 'OBJECT'
    path_data.bevel_object = profile_obj
    
    # Create path object
    path_obj = bpy.data.objects.new("PhotoFrame", path_data)
    bpy.context.collection.objects.link(path_obj)
    
    # Create material for metallic frame
    mat = bpy.data.materials.new(name="FrameMaterial")
    mat.use_nodes = True
    
    # Clear default nodes
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = material_color
    bsdf.inputs['Roughness'].default_value = 0.2
    bsdf.inputs['Metallic'].default_value = 0.8
    
    # Add Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # Link nodes
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to frame
    if path_obj.data.materials:
        path_obj.data.materials[0] = mat
    else:
        path_obj.data.materials.append(mat)
    
    # Create a simple backing/picture plane
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -frame_depth/2))
    backing = bpy.context.active_object
    backing.name = "FrameBacking"
    backing.scale = (inner_width * 0.98, inner_height * 0.98, 1)
    
    # Create backing material (dark gunmetal)
    backing_mat = bpy.data.materials.new(name="BackingMaterial")
    backing_mat.use_nodes = True
    backing_bsdf = backing_mat.node_tree.nodes["Principled BSDF"]
    backing_bsdf.inputs['Base Color'].default_value = (0.2, 0.2, 0.25, 1.0)
    backing_bsdf.inputs['Metallic'].default_value = 0.3
    backing_bsdf.inputs['Roughness'].default_value = 0.4
    backing.data.materials.append(backing_mat)
    
    # Select the frame
    bpy.ops.object.select_all(action='DESELECT')
    path_obj.select_set(True)
    bpy.context.view_layer.objects.active = path_obj
    
    # Hide the profile helper object
    profile_obj.hide_set(True)
    profile_obj.hide_render = True
    
    print(f"Photo frame created successfully!")
    print(f"Frame dimensions: {outer_width}m x {outer_height}m")
    print(f"Picture opening: {inner_width}m x {inner_height}m")
    
    return path_obj, backing, profile_obj


# Example usage:
if __name__ == "__main__":
    # Clear existing objects (optional)
    # bpy.ops.object.select_all(action='SELECT')
    # bpy.ops.object.delete()
    
    # Create the photo frame
    frame, backing, profile = create_photo_frame(
        outer_width=0.3,
        outer_height=0.4,
        frame_depth=0.03,
        frame_width=0.03,
        bevel_segments=2,
        material_color=(0.7, 0.7, 0.75, 1.0)  # Brushed aluminum color
    )
    
    # Optional: Add a camera for better viewing
    bpy.ops.object.camera_add(location=(0, -0.8, 0), rotation=(1.5708, 0, 0))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera