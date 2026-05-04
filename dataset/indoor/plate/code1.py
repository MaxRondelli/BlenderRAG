import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Deep soup plate dimensions (in meters)
PLATE_DIAMETER = 0.28  # 28cm diameter (slightly smaller)
PLATE_RADIUS = PLATE_DIAMETER / 2
PLATE_DEPTH = 0.08 # Deeper well for soup (8cm)
PLATE_THICKNESS = 0.004  # Slightly thicker ceramic (4mm)
RIM_WIDTH = 0.025  # Narrower rim (2.5cm)

def create_realistic_plate():
    """
    Creates a realistic soup plate with a deeper recessed center and narrower rim
    """
    
    # Add a bezier curve for the plate profile
    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
    curve = bpy.context.active_object
    curve.name = "PlateProfile"
    
    # Clear default points and create custom profile
    curve.data.splines.clear()
    spline = curve.data.splines.new('BEZIER')
    
    # Define the soup plate profile points (deeper bowl shape)
    profile_points = [
        # (x, z) coordinates for the plate profile
        (0.0, -PLATE_DEPTH),                           # Center bottom of well
        (PLATE_RADIUS * 0.2, -PLATE_DEPTH),            # Bottom continues shorter
        (PLATE_RADIUS * 0.5, -PLATE_DEPTH * 0.7),      # Steeper curve up
        (PLATE_RADIUS - RIM_WIDTH, -PLATE_DEPTH * 0.3), # More pronounced curve
        (PLATE_RADIUS - RIM_WIDTH * 0.6, 0.0),         # Narrower rim starts
        (PLATE_RADIUS - 0.003, 0.001),                 # Smaller rim lip
        (PLATE_RADIUS, 0.0),                           # Outer edge
    ]
    
    # Add points to spline
    spline.bezier_points.add(len(profile_points) - 1)
    
    for i, (x, z) in enumerate(profile_points):
        point = spline.bezier_points[i]
        point.co = (x, 0, z)
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
    
    # Convert curve to mesh
    bpy.ops.object.convert(target='MESH')
    
    # Add Screw modifier to create the circular plate
    plate = bpy.context.active_object
    plate.name = "SoupPlate"
    
    screw_mod = plate.modifiers.new(name="Screw", type='SCREW')
    screw_mod.steps = 64  # Number of segments around the circle
    screw_mod.render_steps = 128  # Higher resolution for rendering
    screw_mod.axis = 'Z'
    screw_mod.use_merge_vertices = True
    
    # Add Solidify modifier for thickness
    solidify_mod = plate.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify_mod.thickness = PLATE_THICKNESS
    solidify_mod.offset = 0  # Thickness centered
    
    # Add Subdivision Surface for smoothness
    subsurf_mod = plate.modifiers.new(name="Subdivision", type='SUBSURF')
    subsurf_mod.levels = 2
    subsurf_mod.render_levels = 3
    
    # Apply modifiers
    bpy.ops.object.modifier_apply(modifier="Screw")
    bpy.ops.object.modifier_apply(modifier="Solidify")
    
    # Smooth shading
    bpy.ops.object.shade_smooth()
    
    # Create dark ceramic material
    create_ceramic_material(plate)
    
    return plate

def create_ceramic_material(obj):
    """
    Creates a dark ceramic material for the soup plate
    """
    # Create new material
    mat = bpy.data.materials.new(name="DarkCeramic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (0, 0)
    
    # Set ceramic properties with dark brown/charcoal color
    principled_node.inputs['Base Color'].default_value = (0.25, 0.18, 0.12, 1.0)  # Dark brown ceramic
    
    # Ceramic properties
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = 0.15  # More glossy finish
    principled_node.inputs['IOR'].default_value = 1.5
    
    # Connect nodes
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

if __name__ == "__main__":
    plate = create_realistic_plate()