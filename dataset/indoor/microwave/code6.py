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

# MICROWAVE DIMENSIONS
# Standard countertop microwave: 55cm W x 35cm D x 28cm H (wider to accommodate control panel)
micro_width = 0.55
micro_depth = 0.35
micro_height = 0.28
micro_base_y = 0  # Center point

# --- MAIN BODY ---
# Outer shell - BLACK STAINLESS STEEL
outer_shell = create_box(
    "Microwave_Shell",
    (0, 0, micro_height/2),
    (micro_width, micro_depth, micro_height),
    (0.15, 0.15, 0.18, 1),  # Dark metallic black
    metallic=0.8,
    roughness=0.15
)

# Inner cavity (the cooking chamber)
cavity_width = micro_width - 0.06
cavity_depth = micro_depth - 0.15  # Less deep due to electronics in back
cavity_height = micro_height - 0.06
cavity_offset_back = 0.045  # Offset toward back

inner_cavity = create_box(
    "Inner_Cavity",
    (0, cavity_offset_back, micro_height/2),
    (cavity_width, cavity_depth, cavity_height),
    (0.05, 0.05, 0.08, 1),  # Slightly blue-tinted dark interior
    metallic=0.1,
    roughness=0.9
)

# --- DOOR ---
door_thickness = 0.04
door_width = micro_width - 0.18  # Narrower to leave space for control panel on right
door_height = micro_height - 0.04
door_x_offset = -micro_depth/2 + door_thickness/2

# Door outer frame - BLACK STAINLESS STEEL
door_frame = create_box(
    "Door_Frame",
    (-0.065, door_x_offset, micro_height/2),  # Offset left to make room for control panel
    (door_width, door_thickness, door_height),
    (0.12, 0.12, 0.15, 1),  # Matching black stainless
    metallic=0.8,
    roughness=0.15
)

# Door window (mesh screen look)
window_width = door_width - 0.08
window_height = door_height - 0.10
window_y = door_x_offset - door_thickness/2 + 0.005

door_window = create_box(
    "Door_Window",
    (-0.065, window_y, micro_height/2 + 0.02),  # Match door offset
    (window_width, 0.01, window_height),
    (0.02, 0.02, 0.05, 1),  # Slightly blue-tinted dark glass
    metallic=0.2,
    roughness=0.2
)

# Door handle (horizontal bar) - BRUSHED STEEL
handle_width = door_width - 0.15
handle_height = 0.025
handle_depth = 0.02
handle_y = door_x_offset - door_thickness/2 - handle_depth/2
handle_z = micro_height - 0.08

door_handle = create_box(
    "Door_Handle",
    (-0.065, handle_y, handle_z),  # Match door offset
    (handle_width, handle_depth, handle_height),
    (0.35, 0.35, 0.4, 1),  # Brushed steel look
    metallic=0.9,
    roughness=0.2
)

# Handle end caps (cylindrical)
handle_left_cap = create_cylinder(
    "Handle_Cap_Left",
    (-0.065 - handle_width/2, handle_y, handle_z),  # Match door offset
    handle_height/2,
    handle_depth,
    (0.35, 0.35, 0.4, 1),
    metallic=0.9,
    roughness=0.2
)
handle_left_cap.rotation_euler = (math.pi/2, 0, 0)

handle_right_cap = create_cylinder(
    "Handle_Cap_Right",
    (-0.065 + handle_width/2, handle_y, handle_z),  # Match door offset
    handle_height/2,
    handle_depth,
    (0.35, 0.35, 0.4, 1),
    metallic=0.9,
    roughness=0.2
)
handle_right_cap.rotation_euler = (math.pi/2, 0, 0)

# --- CONTROL PANEL (Right side) - BLACK STAINLESS ---
panel_width = 0.12
panel_height = micro_height - 0.05
panel_depth = 0.03
panel_x = micro_width/2 - panel_width/2 - 0.02  # Further to the right with more offset
panel_y = door_x_offset  # Same Y position as door, not centered
panel_z = micro_height/2

control_panel = create_box(
    "Control_Panel",
    (panel_x, panel_y, panel_z),
    (panel_width, panel_depth, panel_height),
    (0.08, 0.08, 0.12, 1),  # Very dark with slight blue tint
    metallic=0.7,
    roughness=0.3
)

# --- DISPLAY SCREEN - BLUE LED ---
display_width = panel_width - 0.02
display_height = 0.04
display_y = panel_y - panel_depth/2 - 0.002
display_z = panel_z + panel_height/2 - display_height/2 - 0.02

display_screen = create_box(
    "Display_Screen",
    (panel_x, display_y, display_z),
    (display_width, 0.005, display_height),
    (0.0, 0.2, 1.0, 1),  # Bright blue LED display
    metallic=0.0,
    roughness=0.1
)

# Add blue emission to display
display_mat = display_screen.data.materials[0]
display_mat.node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 3.0

# --- NUMBER PAD (3x4 grid) - TOUCH BUTTONS ---
button_size = 0.015
button_spacing = 0.022
button_depth = 0.005  # Thinner for touch button look
button_start_z = display_z - display_height/2 - 0.03

# Create 12 buttons (1-9, 0, Start, Stop)
button_positions = []
for row in range(4):
    for col in range(3):
        x = panel_x - button_spacing + col * button_spacing
        z = button_start_z - row * button_spacing
        button_positions.append((x, z))

for i, (x, z) in enumerate(button_positions):
    button = create_cylinder(
        f"Button_{i+1}",
        (x, display_y - button_depth/2 - 0.005, z),
        button_size/2,
        button_depth,
        (0.2, 0.2, 0.25, 1),  # Dark touch buttons
        metallic=0.6,
        roughness=0.4
    )
    button.rotation_euler = (math.pi/2, 0, 0)

# --- DOOR BUTTON (Opens door) ---
door_button_size = 0.025
door_button_y = panel_y - panel_depth/2 - 0.008
door_button_z = button_start_z - 4 * button_spacing - 0.01

door_open_button = create_box(
    "Door_Open_Button",
    (panel_x, door_button_y, door_button_z),
    (panel_width - 0.03, 0.012, door_button_size),
    (0.8, 0.2, 0.1, 1),  # Orange accent color for open button
    metallic=0.4,
    roughness=0.3
)

# --- TURNTABLE (Inside cavity) ---
turntable_radius = 0.13
turntable_thickness = 0.008
turntable_y = cavity_offset_back
turntable_z = 0.035  # Just above cavity floor

turntable = create_cylinder(
    "Turntable",
    (0, turntable_y, turntable_z),
    turntable_radius,
    turntable_thickness,
    (0.9, 0.9, 0.95, 1),  # Slightly blue-tinted glass
    metallic=0.0,
    roughness=0.05
)

# Turntable support hub (center)
hub_radius = 0.015
hub_height = 0.02
hub_z = 0.025

turntable_hub = create_cylinder(
    "Turntable_Hub",
    (0, turntable_y, hub_z),
    hub_radius,
    hub_height,
    (0.2, 0.2, 0.25, 1),
    metallic=0.6,
    roughness=0.4
)

# Turntable roller wheels (3 small wheels supporting the plate)
roller_radius = 0.008
roller_height = 0.008
roller_offset_radius = 0.09

for i in range(3):
    angle = (i * 120) * math.pi / 180
    roller_x = roller_offset_radius * math.cos(angle)
    roller_y = turntable_y + roller_offset_radius * math.sin(angle)
    
    roller = create_cylinder(
        f"Roller_{i+1}",
        (roller_x, roller_y, 0.027),
        roller_radius,
        roller_height,
        (0.3, 0.3, 0.35, 1),
        metallic=0.5,
        roughness=0.5
    )

# --- VENTILATION GRILLES (Top and Side) ---
# Top vent
vent_top_width = micro_width - 0.1
vent_top_depth = 0.08
vent_top_y = micro_depth/2 - vent_top_depth/2 - 0.02
vent_top_z = micro_height

top_vent = create_box(
    "Top_Vent",
    (0, vent_top_y, vent_top_z - 0.002),
    (vent_top_width, vent_top_depth, 0.005),
    (0.1, 0.1, 0.15, 1),  # Dark with blue tint
    metallic=0.7,
    roughness=0.3
)

# Side vent (right side, near back)
vent_side_width = 0.005
vent_side_depth = 0.15
vent_side_height = micro_height - 0.08
vent_side_x = micro_width/2 - 0.002
vent_side_y = micro_depth/2 - vent_side_depth/2 - 0.03

side_vent = create_box(
    "Side_Vent",
    (vent_side_x, vent_side_y, micro_height/2),
    (vent_side_width, vent_side_depth, vent_side_height),
    (0.1, 0.1, 0.15, 1),
    metallic=0.7,
    roughness=0.3
)

# --- POWER CORD ---
# Cord exit point at back
cord_radius = 0.004
cord_exit_x = -0.05
cord_exit_y = micro_depth/2
cord_exit_z = 0.05

# Cord segment 1 (coming out of microwave)
cord_1 = create_cylinder(
    "Power_Cord_1",
    (cord_exit_x, cord_exit_y + 0.025, cord_exit_z),
    cord_radius,
    0.05,
    (0.05, 0.05, 0.08, 1),  # Dark blue cord
    metallic=0.0,
    roughness=0.8
)
cord_1.rotation_euler = (math.pi/2, 0, 0)

# Cord segment 2 (going down)
cord_2 = create_cylinder(
    "Power_Cord_2",
    (cord_exit_x, cord_exit_y + 0.05, 0.025),
    cord_radius,
    0.05,
    (0.05, 0.05, 0.08, 1),
    metallic=0.0,
    roughness=0.8
)

# Cord segment 3 (along surface)
cord_3 = create_cylinder(
    "Power_Cord_3",
    (cord_exit_x - 0.025, cord_exit_y + 0.05, 0.002),
    cord_radius,
    0.05,
    (0.05, 0.05, 0.08, 1),
    metallic=0.0,
    roughness=0.8
)
cord_3.rotation_euler = (0, math.pi/2, 0)

# Power plug
plug = create_box(
    "Power_Plug",
    (cord_exit_x - 0.05, cord_exit_y + 0.05, 0.005),
    (0.03, 0.015, 0.01),
    (0.1, 0.1, 0.12, 1),
    metallic=0.3,
    roughness=0.6
)

# --- BRAND LOGO (embossed on door) ---
logo_text_z = micro_height/2 - 0.05

brand_logo = create_box(
    "Brand_Logo",
    (-0.065, window_y - 0.003, logo_text_z),  # Match door offset
    (0.08, 0.002, 0.012),
    (0.6, 0.6, 0.65, 1),  # Brushed metal logo
    metallic=0.9,
    roughness=0.1
)

# --- INTERIOR LIGHT (inside cavity) ---
light_width = 0.03
light_height = 0.01
light_depth = 0.01
light_x = cavity_width/2 - light_width/2 - 0.02
light_y = cavity_offset_back + cavity_depth/2 - light_depth/2 - 0.01
light_z = micro_height - 0.04

interior_light = create_box(
    "Interior_Light",
    (light_x, light_y, light_z),
    (light_width, light_depth, light_height),
    (1.0, 0.98, 0.9, 1),  # Cool white LED
    metallic=0.0,
    roughness=0.0
)

# Add emission to interior light
light_mat = interior_light.data.materials[0]
light_mat.node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 6.0

# --- FEET (4 rubber feet at bottom corners) ---
foot_radius = 0.01
foot_height = 0.008
foot_offset_x = micro_width/2 - 0.03
foot_offset_y = micro_depth/2 - 0.03

feet_positions = [
    (-foot_offset_x, -foot_offset_y, foot_height/2),
    (foot_offset_x, -foot_offset_y, foot_height/2),
    (-foot_offset_x, foot_offset_y, foot_height/2),
    (foot_offset_x, foot_offset_y, foot_height/2)
]

for i, pos in enumerate(feet_positions):
    foot = create_cylinder(
        f"Foot_{i+1}",
        pos,
        foot_radius,
        foot_height,
        (0.08, 0.08, 0.12, 1),  # Dark blue-tinted rubber
        metallic=0.0,
        roughness=0.9
    )

print("=" * 60)
print("MODERN BLACK STAINLESS STEEL MICROWAVE GENERATED!")
print("=" * 60)