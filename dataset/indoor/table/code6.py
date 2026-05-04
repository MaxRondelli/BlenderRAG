import bpy
import math

# ============================================
# MODERN METAL TABLE - SEPARATE OBJECTS
# Industrial style with steel material and thicker legs
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


def create_modern_metal_table():
    """Create a complete metal table with separate objects."""
    
    # Dimensions (meters) - adjusted for industrial look
    table_width = 1.8
    table_depth = 0.9
    table_height = 0.5
    top_thickness = 0.03  # Thinner top
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
        
        # Add bevel modifier for rounded edges
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.003  # Smaller bevel for sharper industrial look
        bevel.segments = 2
        bevel.limit_method = 'ANGLE'
        bevel.angle_limit = math.radians(30)
        
        # Add subdivision for smoothness
        subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 1  # Less subdivision for more angular look
        subsurf.render_levels = 2
    
    # === CREATE METAL MATERIAL ===
    mat = bpy.data.materials.new(name="MetalMaterial")
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
    
    # Metal properties - dark steel
    bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.18, 1.0)  # Dark steel blue
    bsdf.inputs['Metallic'].default_value = 0.9  # High metallic
    bsdf.inputs['Roughness'].default_value = 0.2  # Somewhat polished
    
    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    # Mapping for surface texture
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (15, 15, 15)
    
    # Noise texture for metal surface variation
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 0)
    noise.inputs['Scale'].default_value = 25.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.5
    
    # Color ramp for metal variation
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].color = (0.12, 0.12, 0.15, 1.0)  # Darker areas
    ramp.color_ramp.elements[1].color = (0.18, 0.18, 0.22, 1.0)  # Lighter areas
    
    # Mix node for subtle color variation
    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-100, 0)
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.3
    
    # Bump for surface detail
    bump = nodes.new('ShaderNodeBump')
    bump.location = (-200, -200)
    bump.inputs['Strength'].default_value = 0.05  # Subtle surface detail
    
    # Connect nodes
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], mix.inputs['Color2'])
    mix.inputs['Color1'].default_value = (0.15, 0.15, 0.18, 1.0)
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
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
    print(f"Created metal table with {len(all_parts)} separate objects")
    print(f"  - 1 table top at z={table_top_z}")
    print(f"  - 4 legs from z=0 to z={leg_height}")
    
    return all_parts


def setup_lighting_and_camera():
    """Setup lighting and camera for metal table."""
    
    # Lights - adjusted for metal reflections
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    light1 = bpy.context.active_object
    light1.data.energy = 600  # Brighter for metal reflections
    light1.data.size = 3
    light1.rotation_euler = (math.radians(55), 0, math.radians(135))
    
    bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
    light2 = bpy.context.active_object
    light2.data.energy = 300
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
    print("=== Creating Modern Metal Table (SEPARATE OBJECTS) ===")
    
    cleanup_scene()
    print("✓ Scene cleaned")
    
    table_parts = create_modern_metal_table()
    print("✓ Metal table created with separate objects")
    print("  - Table top and legs are independent objects")
    print("  - Industrial steel material applied")
    
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