import bpy
import math

# ============================================
# MODERN GLASS TABLE WITH CHROME LEGS
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


def create_modern_glass_table():
    """Create a complete glass table with chrome legs."""
    
    # Dimensions (meters)
    table_width = 1.8
    table_depth = 0.9
    table_height = 0.5
    top_thickness = 0.08  # Thicker glass top
    leg_size = 0.04  # Slightly thinner legs
    
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
    legs = []
    
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
        legs.append(leg)
    
    # === APPLY SMOOTH SHADING TO ALL ===
    for obj in all_parts:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        
        # Add bevel modifier for rounded edges
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.008  # More pronounced beveling
        bevel.segments = 4
        bevel.limit_method = 'ANGLE'
        bevel.angle_limit = math.radians(30)
        
        # Add subdivision for smoothness
        subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 2
        subsurf.render_levels = 2
    
    # === CREATE GLASS MATERIAL ===
    glass_mat = bpy.data.materials.new(name="GlassMaterial")
    glass_mat.use_nodes = True
    nodes = glass_mat.node_tree.nodes
    links = glass_mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Glass properties
    bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)  # Clear white
    bsdf.inputs['Roughness'].default_value = 0.0  # Perfect smoothness
    bsdf.inputs['IOR'].default_value = 1.52  # Glass IOR
    bsdf.inputs['Alpha'].default_value = 0.1  # Very transparent
    
    # Connect
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Enable transparency
    glass_mat.blend_method = 'BLEND'
    glass_mat.use_screen_refraction = True
    
    # === CREATE CHROME MATERIAL ===
    chrome_mat = bpy.data.materials.new(name="ChromeMaterial")
    chrome_mat.use_nodes = True
    nodes = chrome_mat.node_tree.nodes
    links = chrome_mat.node_tree.links
    nodes.clear()
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Chrome properties
    bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.9, 1.0)  # Slight blue tint
    bsdf.inputs['Metallic'].default_value = 1.0  # Full metallic
    bsdf.inputs['Roughness'].default_value = 0.05  # Very shiny
    
    # Connect
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # === ASSIGN MATERIALS ===
    # Glass to table top
    if top.data.materials:
        top.data.materials[0] = glass_mat
    else:
        top.data.materials.append(glass_mat)
    
    # Chrome to legs
    for leg in legs:
        if leg.data.materials:
            leg.data.materials[0] = chrome_mat
        else:
            leg.data.materials.append(chrome_mat)
    
    print(f"Created glass table with {len(all_parts)} separate objects")
    print(f"  - 1 glass table top at z={table_top_z}")
    print(f"  - 4 chrome legs from z=0 to z={leg_height}")
    
    return all_parts


def setup_lighting_and_camera():
    """Setup simple lighting and camera."""
    
    # Lights
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    light1 = bpy.context.active_object
    light1.data.energy = 600  # Brighter for glass reflections
    light1.data.size = 3
    light1.rotation_euler = (math.radians(55), 0, math.radians(135))
    
    bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
    light2 = bpy.context.active_object
    light2.data.energy = 300
    light2.data.size = 4
    light2.rotation_euler = (math.radians(60), 0, math.radians(220))
    
    # Additional light for glass transparency
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
    sun = bpy.context.active_object
    sun.data.energy = 3
    sun.rotation_euler = (math.radians(30), 0, 0)
    
    # Camera
    bpy.ops.object.camera_add(location=(3.2, -3.2, 2.2))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(68), 0, math.radians(48))
    camera.data.lens = 50
    bpy.context.scene.camera = camera
    
    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 256  # Higher samples for glass
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = True


def main():
    """Main function."""
    print("=== Creating Modern Glass Table ===")
    
    cleanup_scene()
    print("✓ Scene cleaned")
    
    table_parts = create_modern_glass_table()
    print("✓ Glass table created with separate objects")
    print("  - Glass top and chrome legs are independent objects")
    print("  - Legs positioned from ground (z=0) to table top")
    
    setup_lighting_and_camera()
    print("✓ Lighting and camera setup")
    
    print("\n=== Complete! ===")
    print("Objects in scene:")
    print("  - TableTop (glass material)")
    print("  - Leg1, Leg2, Leg3, Leg4 (chrome material)")
    print("Press Numpad 0 for camera view")
    print("Press Z > Rendered to preview")


if __name__ == "__main__":
    main()