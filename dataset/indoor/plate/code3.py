import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Realistic plate dimensions (in meters)
# Standard dinner plate: 26-28cm diameter
PLATE_DIAMETER = 0.30  # 30cm diameter
PLATE_RADIUS = PLATE_DIAMETER / 2
PLATE_DEPTH = 0.05 # Depth of the well (2cm)
PLATE_THICKNESS = 0.004  # Ceramic thickness (4mm - slightly thicker)
RIM_WIDTH = 0.045  # Width of the rim (4.5cm - wider rim)

def create_realistic_plate():
    """
    Creates a realistic dinner plate with a recessed center and raised rim
    """
    
    # Add a bezier curve for the plate profile
    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
    curve = bpy.context.active_object
    curve.name = "PlateProfile"
    
    # Clear default points and create custom profile
    curve.data.splines.clear()
    spline = curve.data.splines.new('BEZIER')
    
    # Define the plate profile points (cross-section from center to edge)
    # This creates a bowl-like depression with a raised rim
    profile_points = [
        # (x, z) coordinates for the plate profile
        (0.0, -PLATE_DEPTH),                           # Center bottom of well
        (PLATE_RADIUS * 0.3, -PLATE_DEPTH),            # Bottom continues
        (PLATE_RADIUS * 0.6, -PLATE_DEPTH * 0.5),      # Start curving up
        (PLATE_RADIUS - RIM_WIDTH, -PLATE_DEPTH * 0.2), # Approaching rim
        (PLATE_RADIUS - RIM_WIDTH * 0.5, 0.0),         # Rim starts
        (PLATE_RADIUS - 0.005, 0.002),                 # Slight rim lip
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
    plate.name = "Plate"
    
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
    
    # Create deep blue ceramic material
    create_ceramic_material(plate)
    
    return plate

def create_ceramic_material(obj):
    """
    Creates a deep blue ceramic material for the plate
    """
    # Create new material
    mat = bpy.data.materials.new(name="BlueCeramic")
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
    
    # Set ceramic properties with deep blue color
    principled_node.inputs['Base Color'].default_value = (0.15, 0.25, 0.55, 1.0)  # Deep blue color
    
    # Ceramic properties - more glossy finish
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = 0.1  # More glossy
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