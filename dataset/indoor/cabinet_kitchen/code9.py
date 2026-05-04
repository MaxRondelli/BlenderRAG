import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Helper function to create a box with specific dimensions
def create_box(name, location, dimensions, color, metallic=0.0, roughness=0.5):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (dimensions[0]/2, dimensions[1]/2, dimensions[2]/2)
    
    # Create and assign material
    mat = bpy.data.materials.new(name=f"{name}_material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    obj.data.materials.append(mat)
    return obj

# Helper function to create cylinder
def create_cylinder(name, location, radius, depth, color, metallic=0.0, roughness=0.5):
    bpy.ops.mesh.primitive_cylinder_add(location=location, radius=radius, depth=depth)
    obj = bpy.context.active_object
    obj.name = name
    
    mat = bpy.data.materials.new(name=f"{name}_material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    obj.data.materials.append(mat)
    return obj

# CABINET MATERIALS - Darker espresso finish
wood_color = (0.18, 0.12, 0.08, 1)  # Dark espresso wood
wood_metallic = 0.05
wood_roughness = 0.2

door_color = (0.20, 0.14, 0.10, 1)  # Slightly lighter espresso for doors
door_metallic = 0.05
door_roughness = 0.15

handle_color = (0.85, 0.85, 0.88, 1)  # Polished stainless steel
handle_metallic = 0.95
handle_roughness = 0.1

shelf_color = (0.19, 0.13, 0.09, 1)
shelf_metallic = 0.0
shelf_roughness = 0.3

# STANDARD CABINET DIMENSIONS
lower_cabinet_height = 0.90
lower_cabinet_depth = 0.60
upper_cabinet_height = 0.70
upper_cabinet_depth = 0.35
cabinet_thickness = 0.025  # Slightly thicker cabinet walls

# COUNTERTOP - Black granite
counter_height = lower_cabinet_height
counter_thickness = 0.04
countertop_color = (0.12, 0.12, 0.15, 1)  # Deep black granite
countertop_metallic = 0.7
countertop_roughness = 0.05

# ========================================
# LOWER CABINETS
# ========================================

def create_lower_cabinet(name, position, width):
    """Create a complete lower cabinet with doors, shelves, and hardware"""
    x, y, z = position
    
    # Cabinet body parts
    cabinet_parts = []
    
    # Back panel (now facing the wall)
    back = create_box(
        f"{name}_Back",
        (x, y + lower_cabinet_depth/2 - cabinet_thickness/2, z + lower_cabinet_height/2),
        (width, cabinet_thickness, lower_cabinet_height),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(back)
    
    # Left side panel
    left_side = create_box(
        f"{name}_Left_Side",
        (x - width/2 + cabinet_thickness/2, y, z + lower_cabinet_height/2),
        (cabinet_thickness, lower_cabinet_depth, lower_cabinet_height),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(left_side)
    
    # Right side panel
    right_side = create_box(
        f"{name}_Right_Side",
        (x + width/2 - cabinet_thickness/2, y, z + lower_cabinet_height/2),
        (cabinet_thickness, lower_cabinet_depth, lower_cabinet_height),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(right_side)
    
    # Bottom panel
    bottom = create_box(
        f"{name}_Bottom",
        (x, y, z + cabinet_thickness/2),
        (width - 2*cabinet_thickness, lower_cabinet_depth - cabinet_thickness, cabinet_thickness),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(bottom)
    
    # Top panel (under countertop)
    top = create_box(
        f"{name}_Top",
        (x, y, z + lower_cabinet_height - cabinet_thickness/2),
        (width - 2*cabinet_thickness, lower_cabinet_depth - cabinet_thickness, cabinet_thickness),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(top)
    
    # Internal shelf
    shelf = create_box(
        f"{name}_Shelf",
        (x, y, z + lower_cabinet_height/2),
        (width - 2*cabinet_thickness - 0.02, lower_cabinet_depth - cabinet_thickness - 0.02, cabinet_thickness),
        shelf_color, shelf_metallic, shelf_roughness
    )
    cabinet_parts.append(shelf)
    
    # Doors (2 doors) - now facing outward
    door_width = (width - 0.01) / 2  # Small gap between doors
    door_height = lower_cabinet_height - 0.04
    door_y = y - lower_cabinet_depth/2 + 0.01
    
    # Left door
    left_door = create_box(
        f"{name}_Door_Left",
        (x - width/4, door_y, z + lower_cabinet_height/2),
        (door_width, cabinet_thickness, door_height),
        door_color, door_metallic, door_roughness
    )
    cabinet_parts.append(left_door)
    
    # Right door
    right_door = create_box(
        f"{name}_Door_Right",
        (x + width/4, door_y, z + lower_cabinet_height/2),
        (door_width, cabinet_thickness, door_height),
        door_color, door_metallic, door_roughness
    )
    cabinet_parts.append(right_door)
    
    # Door handles - now on the outside (sleeker design)
    handle_height = 0.012
    handle_width = 0.15
    handle_depth = 0.03
    handle_y = door_y - cabinet_thickness/2 - handle_depth/2
    handle_z = z + lower_cabinet_height - 0.15
    
    # Left door handle
    left_handle = create_box(
        f"{name}_Handle_Left",
        (x - width/4, handle_y, handle_z),
        (handle_width, handle_depth, handle_height),
        handle_color, handle_metallic, handle_roughness
    )
    cabinet_parts.append(left_handle)
    
    # Right door handle
    right_handle = create_box(
        f"{name}_Handle_Right",
        (x + width/4, handle_y, handle_z),
        (handle_width, handle_depth, handle_height),
        handle_color, handle_metallic, handle_roughness
    )
    cabinet_parts.append(right_handle)
    
    # Toe kick (recessed bottom) - now facing outward
    toe_kick_height = 0.10
    toe_kick_depth = 0.08
    toe_kick = create_box(
        f"{name}_Toe_Kick",
        (x, y - lower_cabinet_depth/2 + toe_kick_depth/2, z + toe_kick_height/2),
        (width - 2*cabinet_thickness, toe_kick_depth, toe_kick_height),
        (0.10, 0.08, 0.06, 1), 0.0, 0.8
    )
    cabinet_parts.append(toe_kick)
    
    return cabinet_parts

# ========================================
# UPPER CABINETS
# ========================================

def create_upper_cabinet(name, position, width):
    """Create a complete upper cabinet with glass doors and interior lighting"""
    x, y, z = position
    
    cabinet_parts = []
    
    # Back panel (now facing the wall)
    back = create_box(
        f"{name}_Back",
        (x, y + upper_cabinet_depth/2 - cabinet_thickness/2, z + upper_cabinet_height/2),
        (width, cabinet_thickness, upper_cabinet_height),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(back)
    
    # Left side panel
    left_side = create_box(
        f"{name}_Left_Side",
        (x - width/2 + cabinet_thickness/2, y, z + upper_cabinet_height/2),
        (cabinet_thickness, upper_cabinet_depth, upper_cabinet_height),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(left_side)
    
    # Right side panel
    right_side = create_box(
        f"{name}_Right_Side",
        (x + width/2 - cabinet_thickness/2, y, z + upper_cabinet_height/2),
        (cabinet_thickness, upper_cabinet_depth, upper_cabinet_height),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(right_side)
    
    # Bottom panel
    bottom = create_box(
        f"{name}_Bottom",
        (x, y, z + cabinet_thickness/2),
        (width - 2*cabinet_thickness, upper_cabinet_depth - cabinet_thickness, cabinet_thickness),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(bottom)
    
    # Top panel
    top = create_box(
        f"{name}_Top",
        (x, y, z + upper_cabinet_height - cabinet_thickness/2),
        (width - 2*cabinet_thickness, upper_cabinet_depth - cabinet_thickness, cabinet_thickness),
        wood_color, wood_metallic, wood_roughness
    )
    cabinet_parts.append(top)
    
    # Internal shelves (2 shelves for upper cabinets)
    shelf_1 = create_box(
        f"{name}_Shelf_1",
        (x, y, z + upper_cabinet_height * 0.33),
        (width - 2*cabinet_thickness - 0.02, upper_cabinet_depth - cabinet_thickness - 0.02, cabinet_thickness),
        shelf_color, shelf_metallic, shelf_roughness
    )
    cabinet_parts.append(shelf_1)
    
    shelf_2 = create_box(
        f"{name}_Shelf_2",
        (x, y, z + upper_cabinet_height * 0.66),
        (width - 2*cabinet_thickness - 0.02, upper_cabinet_depth - cabinet_thickness - 0.02, cabinet_thickness),
        shelf_color, shelf_metallic, shelf_roughness
    )
    cabinet_parts.append(shelf_2)
    
    # Glass doors (2 doors) - now facing outward
    door_width = (width - 0.01) / 2
    door_height = upper_cabinet_height - 0.04
    door_y = y - upper_cabinet_depth/2 + 0.01
    
    # Left glass door
    left_door_frame = create_box(
        f"{name}_Door_Left_Frame",
        (x - width/4, door_y, z + upper_cabinet_height/2),
        (door_width, cabinet_thickness, door_height),
        door_color, door_metallic, door_roughness
    )
    cabinet_parts.append(left_door_frame)
    
    # Glass insert for left door
    left_glass = create_box(
        f"{name}_Door_Left_Glass",
        (x - width/4, door_y - 0.005, z + upper_cabinet_height/2),
        (door_width - 0.04, 0.005, door_height - 0.04),
        (0.8, 0.85, 0.9, 0.3),  # Translucent glass
        0.1, 0.05
    )
    cabinet_parts.append(left_glass)
    
    # Right glass door
    right_door_frame = create_box(
        f"{name}_Door_Right_Frame",
        (x + width/4, door_y, z + upper_cabinet_height/2),
        (door_width, cabinet_thickness, door_height),
        door_color, door_metallic, door_roughness
    )
    cabinet_parts.append(right_door_frame)
    
    # Glass insert for right door
    right_glass = create_box(
        f"{name}_Door_Right_Glass",
        (x + width/4, door_y - 0.005, z + upper_cabinet_height/2),
        (door_width - 0.04, 0.005, door_height - 0.04),
        (0.8, 0.85, 0.9, 0.3),  # Translucent glass
        0.1, 0.05
    )
    cabinet_parts.append(right_glass)
    
    # Door knobs (small round knobs for upper cabinets) - now on the outside
    knob_radius = 0.014
    knob_depth = 0.025
    knob_y = door_y - cabinet_thickness/2 - knob_depth/2
    knob_z = z + upper_cabinet_height/2
    
    # Left door knob
    left_knob = create_cylinder(
        f"{name}_Knob_Left",
        (x - width/4 + door_width/2 - 0.05, knob_y, knob_z),
        knob_radius, knob_depth,
        handle_color, handle_metallic, handle_roughness
    )
    left_knob.rotation_euler = (math.pi/2, 0, 0)
    cabinet_parts.append(left_knob)
    
    # Right door knob
    right_knob = create_cylinder(
        f"{name}_Knob_Right",
        (x + width/4 - door_width/2 + 0.05, knob_y, knob_z),
        knob_radius, knob_depth,
        handle_color, handle_metallic, handle_roughness
    )
    right_knob.rotation_euler = (math.pi/2, 0, 0)
    cabinet_parts.append(right_knob)
    
    # Under-cabinet lighting strip - now on the outside bottom
    light_strip = create_box(
        f"{name}_Light_Strip",
        (x, y - upper_cabinet_depth/2 + 0.03, z - 0.01),
        (width - 0.10, 0.04, 0.015),
        (1.0, 0.98, 0.95, 1),
        0.0, 0.1
    )
    # Add emission to light strip
    light_mat = light_strip.data.materials[0]
    light_mat.node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 3.0
    cabinet_parts.append(light_strip)
    
    return cabinet_parts

# ========================================
# CREATE CABINET LAYOUT
# ========================================
# --- LOWER CABINETS ROW ---
lower_y = -0.35  # Distance from wall (now facing outward from wall)
lower_z = 0  # Ground level

# Lower cabinet 1 (Corner - Left)
lower_1_width = 0.80
lower_1_x = -1.40
create_lower_cabinet("Lower_Cabinet_1", (lower_1_x, lower_y, lower_z), lower_1_width)

# Lower cabinet 2 (Center-Left)
lower_2_width = 0.80
lower_2_x = -0.60
create_lower_cabinet("Lower_Cabinet_2", (lower_2_x, lower_y, lower_z), lower_2_width)

# Lower cabinet 3 (Center - Sink cabinet, slightly larger)
lower_3_width = 0.90
lower_3_x = 0.25
create_lower_cabinet("Lower_Cabinet_Sink", (lower_3_x, lower_y, lower_z), lower_3_width)

# Lower cabinet 4 (Right)
lower_4_width = 0.80
lower_4_x = 1.10
create_lower_cabinet("Lower_Cabinet_4", (lower_4_x, lower_y, lower_z), lower_4_width)

# --- COUNTERTOP (Spans across all lower cabinets) ---
countertop_width = 3.20
countertop_x = -0.15
countertop_z = counter_height

countertop = create_box(
    "Countertop",
    (countertop_x, lower_y, countertop_z),
    (countertop_width, lower_cabinet_depth, counter_thickness),
    countertop_color, countertop_metallic, countertop_roughness
)

# Countertop backsplash (now at the back)
backsplash_height = 0.15
backsplash = create_box(
    "Backsplash",
    (countertop_x, lower_y + lower_cabinet_depth/2 - 0.01, countertop_z + counter_thickness/2 + backsplash_height/2),
    (countertop_width, 0.02, backsplash_height),
    (0.15, 0.15, 0.18, 1), 0.6, 0.1
)

# ========================================
# SCENE SETUP
# ========================================

# Main ceiling light
light_data = bpy.data.lights.new(name="Main_Light", type='AREA')
light_data.energy = 150
light_data.size = 1.0
light_object = bpy.data.objects.new(name="Main_Light", object_data=light_data)
bpy.context.collection.objects.link(light_object)
light_object.location = (0, 0, 2.5)

# Fill light from side
fill_light_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
fill_light_data.energy = 80
fill_light_data.size = 0.6
fill_light_object = bpy.data.objects.new(name="Fill_Light", object_data=fill_light_data)
bpy.context.collection.objects.link(fill_light_object)
fill_light_object.location = (2.5, 0, 1.8)
fill_light_object.rotation_euler = (0, math.radians(-60), 0)

# Camera (adjusted to view cabinets from the front)
camera_data = bpy.data.cameras.new(name="Cabinet_Camera")
camera_object = bpy.data.objects.new("Cabinet_Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
camera_object.location = (0, -2.5, 1.3)
camera_object.rotation_euler = (math.radians(85), 0, 0)

# Set as active camera
bpy.context.scene.camera = camera_object

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128