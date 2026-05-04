import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_wood_material(name, base_color, roughness=0.7):
    """Create a procedural wood material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = base_color
    principled.inputs['Roughness'].default_value = roughness
    
    # Add texture coordinate and mapping
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (4, 4, 4)
    
    # Wood texture for base color
    wood_tex = nodes.new(type='ShaderNodeTexWave')
    wood_tex.location = (-400, 100)
    wood_tex.wave_type = 'BANDS'
    wood_tex.bands_direction = 'Z'
    wood_tex.inputs['Scale'].default_value = 2.5
    wood_tex.inputs['Distortion'].default_value = 3.0
    wood_tex.inputs['Detail'].default_value = 3.0
    
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 100)
    color_ramp.color_ramp.elements[0].color = (base_color[0] * 0.5, base_color[1] * 0.5, base_color[2] * 0.5, 1)
    color_ramp.color_ramp.elements[1].color = base_color
    
    # Bump for wood grain
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    noise_tex.location = (-400, -200)
    noise_tex.inputs['Scale'].default_value = 18.0
    noise_tex.inputs['Detail'].default_value = 6.0
    
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (-200, -200)
    bump.inputs['Strength'].default_value = 0.4
    
    # Link nodes
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wood_tex.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])
    links.new(wood_tex.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
    links.new(noise_tex.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], principled.inputs['Normal'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_wooden_window():
    """Create a rustic wooden window with thicker frame"""
    
    # ============ DIMENSIONS (in meters) ============
    TOTAL_WIDTH = 1.2        # Total outer width
    TOTAL_HEIGHT = 1.2       # Total outer height
    FRAME_DEPTH = 0.08       # Depth (Z direction)
    FRAME_THICKNESS = 0.13   # Thicker outer frame for rustic look
    MUNTIN_THICKNESS = 0.07  # Thicker center dividers
    GLASS_THICKNESS = 0.004  # Glass thickness
    GLASS_RECESS = 0.025     # How far back glass sits from front
    
    # Calculate inner dimensions
    INNER_WIDTH = TOTAL_WIDTH - (2 * FRAME_THICKNESS)
    INNER_HEIGHT = TOTAL_HEIGHT - (2 * FRAME_THICKNESS)
    
    # Create darker oak wood material
    wood_mat = create_wood_material(
        "DarkOakMaterial",
        base_color=(0.12, 0.08, 0.04, 1.0),  # Darker oak color
        roughness=0.7  # More rough for rustic feel
    )
    
    all_wood_objects = []
    
    # ============ OUTER FRAME (4 pieces) ============
    
    # TOP FRAME - spans full width
    bpy.ops.mesh.primitive_cube_add(size=1)
    top = bpy.context.active_object
    top.name = "TopFrame"
    top.dimensions = (TOTAL_WIDTH, FRAME_THICKNESS, FRAME_DEPTH)
    top.location = (0, TOTAL_HEIGHT/2 - FRAME_THICKNESS/2, 0)
    top.data.materials.append(wood_mat)
    all_wood_objects.append(top)
    
    # BOTTOM FRAME - spans full width
    bpy.ops.mesh.primitive_cube_add(size=1)
    bottom = bpy.context.active_object
    bottom.name = "BottomFrame"
    bottom.dimensions = (TOTAL_WIDTH, FRAME_THICKNESS, FRAME_DEPTH)
    bottom.location = (0, -TOTAL_HEIGHT/2 + FRAME_THICKNESS/2, 0)
    bottom.data.materials.append(wood_mat)
    all_wood_objects.append(bottom)
    
    # LEFT FRAME - spans inner height only
    bpy.ops.mesh.primitive_cube_add(size=1)
    left = bpy.context.active_object
    left.name = "LeftFrame"
    left.dimensions = (FRAME_THICKNESS, INNER_HEIGHT, FRAME_DEPTH)
    left.location = (-TOTAL_WIDTH/2 + FRAME_THICKNESS/2, 0, 0)
    left.data.materials.append(wood_mat)
    all_wood_objects.append(left)
    
    # RIGHT FRAME - spans inner height only
    bpy.ops.mesh.primitive_cube_add(size=1)
    right = bpy.context.active_object
    right.name = "RightFrame"
    right.dimensions = (FRAME_THICKNESS, INNER_HEIGHT, FRAME_DEPTH)
    right.location = (TOTAL_WIDTH/2 - FRAME_THICKNESS/2, 0, 0)
    right.data.materials.append(wood_mat)
    all_wood_objects.append(right)
    
    # ============ CENTER MUNTINS (Dividers) ============
    
    # VERTICAL MUNTIN - divides window left/right
    bpy.ops.mesh.primitive_cube_add(size=1)
    v_muntin = bpy.context.active_object
    v_muntin.name = "VerticalMuntin"
    v_muntin.dimensions = (MUNTIN_THICKNESS, INNER_HEIGHT, FRAME_DEPTH)
    v_muntin.location = (0, 0, 0)
    v_muntin.data.materials.append(wood_mat)
    all_wood_objects.append(v_muntin)
    
    # HORIZONTAL MUNTIN - divides window top/bottom
    bpy.ops.mesh.primitive_cube_add(size=1)
    h_muntin = bpy.context.active_object
    h_muntin.name = "HorizontalMuntin"
    h_muntin.dimensions = (INNER_WIDTH, MUNTIN_THICKNESS, FRAME_DEPTH)
    h_muntin.location = (0, 0, 0)
    h_muntin.data.materials.append(wood_mat)
    all_wood_objects.append(h_muntin)
    
    # ============ GLASS MATERIAL (Slightly Tinted) ============
    glass_mat = bpy.data.materials.new(name="TintedGlass")
    glass_mat.use_nodes = True
    glass_nodes = glass_mat.node_tree.nodes
    glass_nodes.clear()
    
    output_node = glass_nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (200, 0)
    
    glass_node = glass_nodes.new(type='ShaderNodeBsdfGlass')
    glass_node.location = (0, 0)
    glass_node.inputs['IOR'].default_value = 1.52
    glass_node.inputs['Roughness'].default_value = 0.02
    glass_node.inputs['Color'].default_value = (0.85, 0.9, 0.95, 1.0)  # Slightly blue-tinted
    
    glass_mat.node_tree.links.new(glass_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    # ============ GLASS PANES (4 quadrants) ============
    
    # Size of each pane (with small gap around edges)
    PANE_WIDTH = (INNER_WIDTH - MUNTIN_THICKNESS) / 2 - 0.01
    PANE_HEIGHT = (INNER_HEIGHT - MUNTIN_THICKNESS) / 2 - 0.01
    
    # Positions (center of each quadrant)
    X_OFFSET = (INNER_WIDTH - MUNTIN_THICKNESS) / 4
    Y_OFFSET = (INNER_HEIGHT - MUNTIN_THICKNESS) / 4
    
    panes = [
        ("TopLeft", -X_OFFSET, Y_OFFSET),
        ("TopRight", X_OFFSET, Y_OFFSET),
        ("BottomLeft", -X_OFFSET, -Y_OFFSET),
        ("BottomRight", X_OFFSET, -Y_OFFSET)
    ]
    
    for name, x, y in panes:
        bpy.ops.mesh.primitive_cube_add(size=1)
        pane = bpy.context.active_object
        pane.name = f"Glass_{name}"
        pane.dimensions = (PANE_WIDTH, PANE_HEIGHT, GLASS_THICKNESS)
        pane.location = (x, y, -GLASS_RECESS)
        pane.data.materials.append(glass_mat)
    
    # ============ APPLY MODIFIERS TO WOOD ============
    for obj in all_wood_objects:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Larger bevel for rustic rounded edges
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = 0.005
        bevel.segments = 3
        bevel.limit_method = 'ANGLE'
        bevel.angle_limit = math.radians(30)
        
        # Subdivision for smooth surface
        subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = 1
        subsurf.render_levels = 2
        
        obj.select_set(False)
    
    # ============ JOIN WOODEN PARTS ============
    bpy.ops.object.select_all(action='DESELECT')
    for obj in all_wood_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = all_wood_objects[0]
    bpy.ops.object.join()
    
    window = bpy.context.active_object
    window.name = "RusticWoodenWindow"
    
    # ============ SCENE SETUP ============
    
    # Camera
    bpy.ops.object.camera_add(location=(0, -2.5, 0))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.camera = camera
    
    # Lighting
    bpy.ops.object.light_add(type='SUN', location=(3, -4, 8))
    sun = bpy.context.active_object
    sun.data.energy = 2.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    
    bpy.ops.object.light_add(type='AREA', location=(-2, -2, 2))
    area = bpy.context.active_object
    area.data.energy = 100
    area.data.size = 2
    
    # Render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    
    print("\n" + "="*60)
    print("RUSTIC WOODEN WINDOW CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"Outer Dimensions: {TOTAL_WIDTH}m × {TOTAL_HEIGHT}m × {FRAME_DEPTH}m")
    print(f"Frame Thickness: {FRAME_THICKNESS}m")
    print(f"Inner Opening: {INNER_WIDTH:.3f}m × {INNER_HEIGHT:.3f}m")
    print(f"Muntin Thickness: {MUNTIN_THICKNESS}m")
    print(f"Glass Panes: 4 (2×2 grid) - Tinted")
    print("="*60 + "\n")
    
    return window

# Create the window
window = create_wooden_window()

# Set viewport shading
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'