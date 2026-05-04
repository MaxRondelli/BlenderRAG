import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Wardrobe dimensions (in meters) - based on typical proportions from image
WARDROBE_WIDTH = 1.50  # 150cm width (3 sections)
WARDROBE_DEPTH = 0.60  # 60cm depth
WARDROBE_HEIGHT = 2.00  # 200cm height

# Panel thickness - increased for modern look
PANEL_THICKNESS = 0.035  # 3.5cm (was 2.5cm)

# Door section (upper part with doors)
DOOR_HEIGHT = 1.40  # 140cm for door section
DOOR_GAP = 0.003  # 3mm gap between doors

# Drawer section (lower part)
DRAWER_SECTION_HEIGHT = WARDROBE_HEIGHT - DOOR_HEIGHT - PANEL_THICKNESS  # Remaining height for drawers + top
DRAWER_COUNT = 3  # 3 rows of drawers
DRAWER_ROWS = 2  # 2 drawers per row
DRAWER_GAP = 0.003  # 3mm gap
DRAWER_HEIGHT = (DRAWER_SECTION_HEIGHT - PANEL_THICKNESS * 2 - DRAWER_GAP * (DRAWER_COUNT - 1)) / DRAWER_COUNT

# Handle dimensions - slightly larger
HANDLE_WIDTH = 0.12  # 12cm (was 10cm)
HANDLE_HEIGHT = 0.018  # 1.8cm (was 1.5cm)
HANDLE_DEPTH = 0.030  # 3cm protrusion (was 2.5cm)

# Door handle dimensions (vertical) - slightly larger
DOOR_HANDLE_WIDTH = 0.018  # 1.8cm wide (was 1.5cm)
DOOR_HANDLE_HEIGHT = 0.18  # 18cm tall (was 15cm)
DOOR_HANDLE_DEPTH = 0.030  # 3cm protrusion (was 2.5cm)

def create_cube(name, dimensions, location):
    """Helper function to create a cube with specific dimensions and location"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = dimensions
    return obj

def create_wardrobe_frame():
    """Creates the main frame/carcass of the wardrobe"""
    parts = []
    interior_width = WARDROBE_WIDTH - PANEL_THICKNESS * 2
    interior_depth = WARDROBE_DEPTH - PANEL_THICKNESS
    
    # LEFT SIDE PANEL - full height from ground
    left_panel = create_cube(
        "LeftPanel",
        (PANEL_THICKNESS, WARDROBE_DEPTH, WARDROBE_HEIGHT),
        (-WARDROBE_WIDTH/2 + PANEL_THICKNESS/2, 0, WARDROBE_HEIGHT/2)
    )
    parts.append(left_panel)
    
    # RIGHT SIDE PANEL - full height from ground
    right_panel = create_cube(
        "RightPanel",
        (PANEL_THICKNESS, WARDROBE_DEPTH, WARDROBE_HEIGHT),
        (WARDROBE_WIDTH/2 - PANEL_THICKNESS/2, 0, WARDROBE_HEIGHT/2)
    )
    parts.append(right_panel)
    
    # BACK PANEL - full height from ground
    back_panel = create_cube(
        "BackPanel",
        (interior_width, PANEL_THICKNESS, WARDROBE_HEIGHT),
        (0, -WARDROBE_DEPTH/2 + PANEL_THICKNESS/2, WARDROBE_HEIGHT/2)
    )
    parts.append(back_panel)
    
    # TOP PANEL - horizontal at the top
    top_panel = create_cube(
        "TopPanel",
        (WARDROBE_WIDTH, WARDROBE_DEPTH, PANEL_THICKNESS),
        (0, 0, WARDROBE_HEIGHT - PANEL_THICKNESS/2)
    )
    parts.append(top_panel)
    
    # BOTTOM PANEL - horizontal on the ground
    bottom_panel = create_cube(
        "BottomPanel",
        (WARDROBE_WIDTH, WARDROBE_DEPTH, PANEL_THICKNESS),
        (0, 0, PANEL_THICKNESS/2)
    )
    parts.append(bottom_panel)
    
    # DIVIDER PANEL - separates door section from drawer section
    divider_z = DRAWER_SECTION_HEIGHT
    divider_panel = create_cube(
        "DividerPanel",
        (interior_width, interior_depth, PANEL_THICKNESS),
        (0, PANEL_THICKNESS/2, divider_z)
    )
    parts.append(divider_panel)
    
    return parts, divider_z

def create_doors(divider_z):
    """Creates the 3 wardrobe doors in the upper section"""
    doors = []
    door_count = 3
    door_width = (WARDROBE_WIDTH - PANEL_THICKNESS * 2 - DOOR_GAP * (door_count + 1)) / door_count
    door_thickness = 0.025  # 2.5cm thick doors (was 2cm)
    
    # Door section starts above the divider
    door_section_bottom = divider_z + PANEL_THICKNESS
    door_section_top = WARDROBE_HEIGHT - PANEL_THICKNESS
    door_height = door_section_top - door_section_bottom - DOOR_GAP * 2
    door_z_center = door_section_bottom + door_height/2 + DOOR_GAP
    
    door_y = WARDROBE_DEPTH/2 - door_thickness/2
    
    for i in range(door_count):
        # Calculate X position for each door
        start_x = -WARDROBE_WIDTH/2 + PANEL_THICKNESS + DOOR_GAP
        door_x = start_x + (i * (door_width + DOOR_GAP)) + door_width/2
        
        door = create_cube(
            f"Door_{i+1}",
            (door_width, door_thickness, door_height),
            (door_x, door_y, door_z_center)
        )
        
        # Add bevel for rounded edges
        bevel_mod = door.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = 0.002
        bevel_mod.segments = 2
        bpy.ops.object.shade_smooth()
        
        doors.append(door)
    
    return doors

def create_door_handles(doors):
    """Creates vertical handles for the doors"""
    handles = []
    
    for i, door in enumerate(doors):
        # Place handle on the side of each door
        # Alternate between left and right side based on door position
        if i == 0:  # Left door - handle on right
            handle_x_offset = door.dimensions.x/2 - 0.08
        elif i == 2:  # Right door - handle on left
            handle_x_offset = -door.dimensions.x/2 + 0.08
        else:  # Middle door - handle on left
            handle_x_offset = -door.dimensions.x/2 + 0.08
        
        handle = create_cube(
            f"DoorHandle_{i+1}",
            (DOOR_HANDLE_WIDTH, DOOR_HANDLE_DEPTH, DOOR_HANDLE_HEIGHT),
            (door.location.x + handle_x_offset,
             door.location.y + door.dimensions.y/2 + DOOR_HANDLE_DEPTH/2,
             door.location.z)
        )
        
        # Add bevel for rounded edges
        bevel_mod = handle.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = 0.005
        bevel_mod.segments = 4
        bpy.ops.object.shade_smooth()
        
        handles.append(handle)
    
    return handles

def create_drawers():
    """Creates the drawer section (3 rows, 3 columns)"""
    drawers = []
    interior_width = WARDROBE_WIDTH - PANEL_THICKNESS * 2
    drawer_width = (interior_width - DRAWER_GAP * 4) / 3  # 3 drawers per row
    drawer_depth = 0.025  # 2.5cm thick drawer fronts (was 2cm)
    
    drawer_y = WARDROBE_DEPTH/2 - drawer_depth/2
    
    # Create 3 rows of drawers
    for row in range(DRAWER_COUNT):
        # Calculate Z position for this row
        z_pos = PANEL_THICKNESS + (row * (DRAWER_HEIGHT + DRAWER_GAP)) + DRAWER_HEIGHT/2
        
        # Create 3 drawers in this row
        for col in range(3):
            start_x = -WARDROBE_WIDTH/2 + PANEL_THICKNESS + DRAWER_GAP
            drawer_x = start_x + (col * (drawer_width + DRAWER_GAP)) + drawer_width/2
            
            drawer = create_cube(
                f"Drawer_R{row+1}_C{col+1}",
                (drawer_width, drawer_depth, DRAWER_HEIGHT - DRAWER_GAP),
                (drawer_x, drawer_y, z_pos)
            )
            
            # Add bevel for rounded edges
            bevel_mod = drawer.modifiers.new(name="Bevel", type='BEVEL')
            bevel_mod.width = 0.001
            bevel_mod.segments = 2
            bpy.ops.object.shade_smooth()
            
            drawers.append(drawer)
    
    return drawers

def create_drawer_handles(drawers):
    """Creates handles for all drawers"""
    handles = []
    
    for i, drawer in enumerate(drawers):
        handle = create_cube(
            f"DrawerHandle_{i+1}",
            (HANDLE_WIDTH, HANDLE_DEPTH, HANDLE_HEIGHT),
            (drawer.location.x,
             drawer.location.y + drawer.dimensions.y/2 + HANDLE_DEPTH/2,
             drawer.location.z)
        )
        
        # Add bevel for rounded edges
        bevel_mod = handle.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = 0.004
        bevel_mod.segments = 4
        bpy.ops.object.shade_smooth()
        
        handles.append(handle)
    
    return handles

def create_white_lacquer_material(name):
    """Creates a white lacquer material with glossy finish"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (0, 0)
    
    # White lacquer properties
    principled_node.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)  # Pure white
    principled_node.inputs['Metallic'].default_value = 0.0
    principled_node.inputs['Roughness'].default_value = 0.05  # Very glossy
    principled_node.inputs['IOR'].default_value = 1.5
    
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    return mat

def create_metal_handle_material(name):
    """Creates a metallic silver material for handles"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (400, 0)
    
    principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_node.location = (0, 0)
    
    # Silver metallic properties
    principled_node.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1.0)  # Silver color
    principled_node.inputs['Metallic'].default_value = 1.0  # Full metallic
    principled_node.inputs['Roughness'].default_value = 0.15  # Slightly brushed metal
    principled_node.inputs['IOR'].default_value = 1.0
    
    links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])
    
    return mat

def apply_materials(frame_parts, doors, drawers, door_handles, drawer_handles):
    """Apply materials to components"""
    # Create materials
    white_lacquer_mat = create_white_lacquer_material("WhiteLacquer")
    metal_mat = create_metal_handle_material("MetalHandle")
    
    # Apply white lacquer to frame, doors, and drawers
    for obj in frame_parts + doors + drawers:
        if obj.data.materials:
            obj.data.materials[0] = white_lacquer_mat
        else:
            obj.data.materials.append(white_lacquer_mat)
    
    # Apply metal material to handles
    for obj in door_handles + drawer_handles:
        if obj.data.materials:
            obj.data.materials[0] = metal_mat
        else:
            obj.data.materials.append(metal_mat)

def setup_scene():
    """Set up lighting and camera"""
    # Position camera to view the wardrobe
    bpy.ops.object.camera_add(location=(3.5, -3.5, 2.5))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(70), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Key light
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    key_light = bpy.context.active_object
    key_light.data.energy = 300
    key_light.data.size = 3.0
    
    # Fill light
    bpy.ops.object.light_add(type='AREA', location=(-2.5, -2, 3))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 150
    fill_light.data.size = 2.0
    
    # Back light
    bpy.ops.object.light_add(type='AREA', location=(0, 3, 3))
    back_light = bpy.context.active_object
    back_light.data.energy = 100
    back_light.data.size = 2.0
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128

# Main execution
if __name__ == "__main__":
    print("Creating modern white lacquered wardrobe...")
    
    # Create all components
    frame_parts, divider_z = create_wardrobe_frame()
    doors = create_doors(divider_z)
    door_handles = create_door_handles(doors)
    drawers = create_drawers()
    drawer_handles = create_drawer_handles(drawers)
    
    # Apply materials
    apply_materials(frame_parts, doors, drawers, door_handles, drawer_handles)
    
    # Setup scene
    setup_scene()
    
    print("\nModern white lacquered wardrobe created successfully!")
    print(f"Dimensions: {WARDROBE_WIDTH*100:.0f}cm W x {WARDROBE_DEPTH*100:.0f}cm D x {WARDROBE_HEIGHT*100:.0f}cm H")
    print(f"3 doors in upper section with metallic handles")
    print(f"{DRAWER_COUNT} rows x 3 columns = {DRAWER_COUNT * 3} drawers total")
    print("White lacquer finish with silver metallic handles!")