import bpy
import math

# ============================================
# RUSTIC FARMHOUSE WOODEN TABLE - SEPARATE OBJECTS
# Table top and legs are kept as separate objects
# ============================================

def cleanup_scene():
    """Clean the scene."""
    bpy.ops.object.select_all(action='SELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            obj.select_set(False)
    bpy.ops.object.delete()
    
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def create_simple_realistic_table():
    """Create a complete table with separate objects."""
    
    # Dimensions (meters) - Thicker for farmhouse style
    table_width = 1.8
    table_depth = 0.9
    table_height = 0.5
    top_thickness = 0.08  # Thicker top
    leg_size = 0.08  # Thicker legs
    
    # Calculate the Z position for the top of the table
    table_top_z = table_height
    
    # === TABLE TOP ===
    # Position the table top at the correct height
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, table_top_z))
    top = bpy.context.active_object
    top.name = "TableTop"
    top.scale = (table_width/2, table_depth/2, top_thickness/2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # === LEG SETUP ===
    leg_height = table_height + 0.17 # Legs go from ground (0) to table top
    leg_inset_x = 0.50  # Distance from edge
    leg_inset_y = 0.30
    # Calculate leg positions
    leg_positions = [
        (-table_width/2 + leg_inset_x, -table_depth/2 + leg_inset_y),  # Front Left
        (table_width/2 - leg_inset_x, -table_depth/2 + leg_inset_y),   # Front Right
        (-table_width/2 + leg_inset_x, table_depth/2 - leg_inset_y),   # Back Left
        (table_width/2 - leg_inset_x, table_depth/2 - leg_inset_y)     # Back Right
    ]
    
    all_parts = [top]
    
    # Create all four legs
    for i, (leg_x, leg_y) in enumerate(leg_positions, 1):
        # Position leg so its bottom is at z=0 and top touches table
        leg_z = leg_height / 2
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(leg_x, leg_y, leg_z))
        leg = bpy.context.active_object
        leg.name = f"Leg{i}"
        leg.scale = (leg_size/2, leg_size/2, leg_height/2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        all_parts.append(leg)
    
    # === APPLY SMOOTH SHADING TO ALL ===
    for obj in all_parts:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        
        # Add bevel modifier for rounded edges - slightly larger for rustic look
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.008
        bevel.segments = 3
        bevel.limit_method = 'ANGLE'
        bevel.angle_limit = math.radians(30)
        
        # Add subdivision for smoothness
        subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 2
    
    # === CREATE DARK WALNUT WOOD MATERIAL ===
    mat = bpy.data.materials.new(name="WalnutMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Dark walnut color
    bsdf.inputs['Base Color'].default_value = (0.25, 0.15, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6  # More matte/rustic
    
    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    # Mapping for grain
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (8, 8, 8)
    
    # Noise texture for more natural wood grain
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    
    # Color ramp for darker wood tones
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (0.15, 0.08, 0.04, 1.0)  # Very dark brown
    ramp.color_ramp.elements[1].color = (0.35, 0.22, 0.12, 1.0)  # Medium walnut
    
    # Bump for more pronounced texture
    bump = nodes.new('ShaderNodeBump')
    bump.location = (-200, -200)
    bump.inputs['Strength'].default_value = 0.2  # Stronger bump for rustic look
    
    # Connect nodes
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # === ASSIGN MATERIAL TO ALL PARTS ===
    for obj in all_parts:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    
    # === DO NOT JOIN - Keep as separate objects ===
    print(f"Created table with {len(all_parts)} separate objects")
    print(f"  - 1 table top at z={table_top_z}")
    print(f"  - 4 legs from z=0 to z={leg_height}")
    
    return all_parts


def setup_lighting_and_camera():
    """Setup simple lighting and camera."""
    
    # Lights
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    light1 = bpy.context.active_object
    light1.data.energy = 500
    light1.data.size = 3
    light1.rotation_euler = (math.radians(55), 0, math.radians(135))
    
    bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
    light2 = bpy.context.active_object
    light2.data.energy = 200
    light2.data.size = 4
    light2.rotation_euler = (math.radians(60), 0, math.radians(220))
    
    # Camera
    bpy.ops.object.camera_add(location=(3, -3, 2.5))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(70), 0, math.radians(45))
    camera.data.lens = 50
    bpy.context.scene.camera = camera
    
    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080


def main():
    """Main function."""
    print("=== Creating Rustic Farmhouse Table (SEPARATE OBJECTS) ===")
    
    cleanup_scene()
    print("✓ Scene cleaned")
    
    table_parts = create_simple_realistic_table()
    print("✓ Table created with separate objects")
    print("  - Table top and legs are independent objects")
    print("  - Legs positioned from ground (z=0) to table top")
    
    setup_lighting_and_camera()
    print("✓ Lighting and camera setup")
    
    print("\n=== Complete! ===")
    print("Objects in scene:")
    print("  - TableTop (separate object)")
    print("  - Leg1, Leg2, Leg3, Leg4 (separate objects)")
    print("Press Numpad 0 for camera view")
    print("Press Z > Rendered to preview")


if __name__ == "__main__":
    main()