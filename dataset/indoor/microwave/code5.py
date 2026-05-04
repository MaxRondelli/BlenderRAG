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
# Outer shell - Changed to sleek black
outer_shell = create_box(
    "Microwave_Shell",
    (0, 0, micro_height/2),
    (micro_width, micro_depth, micro_height),
    (0.15, 0.15, 0.18, 1),  # Dark blue-black
    metallic=0.6,
    roughness=0.1
)

# Inner cavity (the cooking chamber) - Darker interior
cavity_width = micro_width - 0.06
cavity_depth = micro_depth - 0.15  # Less deep due to electronics in back
cavity_height = micro_height - 0.06
cavity_offset_back = 0.045  # Offset toward back

inner_cavity = create_box(
    "Inner_Cavity",
    (0, cavity_offset_back, micro_height/2),
    (cavity_width, cavity_depth, cavity_height),
    (0.05, 0.05, 0.05, 1),  # Even darker interior
    metallic=0.1,
    roughness=0.8
)

# --- DOOR ---
door_thickness = 0.04
door_width = micro_width - 0.18  # Narrower to leave space for control panel on right
door_height = micro_height - 0.04
door_x_offset = -micro_depth/2 + door_thickness/2

# Door outer frame - Match black shell
door_frame = create_box(
    "Door_Frame",
    (-0.065, door_x_offset, micro_height/2),  # Offset left to make room for control panel
    (door_width, door_thickness, door_height),
    (0.15, 0.15, 0.18, 1),  # Match shell color
    metallic=0.6,
    roughness=0.1
)

# Door window (mesh screen look)
window_width = door_width - 0.08
window_height = door_height - 0.10
window_y = door_x_offset - door_thickness/2 + 0.005

door_window = create_box(
    "Door_Window",
    (-0.065, window_y, micro_height/2 + 0.02),  # Match door offset
    (window_width, 0.01, window_height),
    (0.02, 0.02, 0.02, 1),  # Darker glass/mesh
    metallic=0.3,
    roughness=0.2
)

# Door handle (horizontal bar) - Enhanced metallic finish
handle_width = door_width - 0.15
handle_height = 0.025
handle_depth = 0.02
handle_y = door_x_offset - door_thickness/2 - handle_depth/2
handle_z = micro_height - 0.08

door_handle = create_box(
    "Door_Handle",
    (-0.065, handle_y, handle_z),  # Match door offset
    (handle_width, handle_depth, handle_height),
    (0.7, 0.7, 0.75, 1),  # Bright metallic
    metallic=0.9,
    roughness=0.1
)

# Handle end caps (cylindrical) - Enhanced metallic
handle_left_cap = create_cylinder(
    "Handle_Cap_Left",
    (-0.065 - handle_width/2, handle_y, handle_z),  # Match door offset
    handle_height/2,
    handle_depth,
    (0.7, 0.7, 0.75, 1),  # Bright metallic
    metallic=0.9,
    roughness=0.1
)
handle_left_cap.rotation_euler = (math.pi/2, 0, 0)

handle_right_cap = create_cylinder(
    "Handle_Cap_Right",
    (-0.065 + handle_width/2, handle_y, handle_z),  # Match door offset
    handle_height/2,
    handle_depth,
    (0.7, 0.7, 0.75, 1),  # Bright metallic
    metallic=0.9,
    roughness=0.1
)
handle_right_cap.rotation_euler = (math.pi/2, 0, 0)

# --- CONTROL PANEL (Right side) ---
# FIXED: Position control panel at the same Y position as the door (front face)
# This ensures it's mounted on the front surface, to the right of the door
panel_width = 0.12
panel_height = micro_height - 0.05
panel_depth = 0.03
panel_x = micro_width/2 - panel_width/2 - 0.02  # Further to the right with more offset
# FIXED: Set panel_y to match the door's front position
panel_y = door_x_offset  # Same Y position as door, not centered
panel_z = micro_height/2

control_panel = create_box(
    "Control_Panel",
    (panel_x, panel_y, panel_z),
    (panel_width, panel_depth, panel_height),
    (0.08, 0.08, 0.08, 1),  # Darker control panel
    metallic=0.3,
    roughness=0.3
)

# --- DISPLAY SCREEN ---
display_width = panel_width - 0.02
display_height = 0.04
# FIXED: Position display in front of the control panel
display_y = panel_y - panel_depth/2 - 0.002
display_z = panel_z + panel_height/2 - display_height/2 - 0.02

display_screen = create_box(
    "Display_Screen",
    (panel_x, display_y, display_z),
    (display_width, 0.005, display_height),
    (0.8, 0.4, 0.1, 1),  # Amber display
    metallic=0.0,
    roughness=0.0
)

# --- NUMBER PAD (3x4 grid) ---
button_size = 0.015
button_spacing = 0.022
button_depth = 0.008
button_start_z = display_z - display_height/2 - 0.03

# Create 12 buttons (1-9, 0, Start, Stop) - Enhanced metallic buttons
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
        (0.6, 0.6, 0.65, 1),  # Metallic buttons
        metallic=0.8,
        roughness=0.2
    )
    button.rotation_euler = (math.pi/2, 0, 0)

# --- DOOR BUTTON (Opens door) ---
# This button is now on the control panel on the right side
door_button_size = 0.025
door_button_y = panel_y - panel_depth/2 - 0.008
door_button_z = button_start_z - 4 * button_spacing - 0.01

door_open_button = create_box(
    "Door_Open_Button",
    (panel_x, door_button_y, door_button_z),
    (panel_width - 0.03, 0.012, door_button_size),
    (0.7, 0.2, 0.1, 1),  # Amber/orange button
    metallic=0.5,
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
    (0.9, 0.9, 0.92, 1),  # Slightly blue-tinted glass
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
    (0.4, 0.4, 0.4, 1),
    metallic=0.6,
    roughness=0.3
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
        (0.5, 0.5, 0.5, 1),
        metallic=0.5,
        roughness=0.4
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
    (0.3, 0.3, 0.3, 1),
    metallic=0.7,
    roughness=0.2
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
    (0.3, 0.3, 0.3, 1),
    metallic=0.7,
    roughness=0.2
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
    (0.08, 0.08, 0.08, 1),
    metallic=0.0,
    roughness=0.9
)
cord_1.rotation_euler = (math.pi/2, 0, 0)

# Cord segment 2 (going down)
cord_2 = create_cylinder(
    "Power_Cord_2",
    (cord_exit_x, cord_exit_y + 0.05, 0.025),
    cord_radius,
    0.05,
    (0.08, 0.08, 0.08, 1),
    metallic=0.0,
    roughness=0.9
)

# Cord segment 3 (along surface)
cord_3 = create_cylinder(
    "Power_Cord_3",
    (cord_exit_x - 0.025, cord_exit_y + 0.05, 0.002),
    cord_radius,
    0.05,
    (0.08, 0.08, 0.08, 1),
    metallic=0.0,
    roughness=0.9
)
cord_3.rotation_euler = (0, math.pi/2, 0)

# Power plug
plug = create_box(
    "Power_Plug",
    (cord_exit_x - 0.05, cord_exit_y + 0.05, 0.005),
    (0.03, 0.015, 0.01),
    (0.12, 0.12, 0.12, 1),
    metallic=0.3,
    roughness=0.5
)

# --- BRAND LOGO (embossed on door) ---
logo_text_z = micro_height/2 - 0.05

brand_logo = create_box(
    "Brand_Logo",
    (-0.065, window_y - 0.003, logo_text_z),  # Match door offset
    (0.08, 0.002, 0.012),
    (0.8, 0.8, 0.85, 1),  # Bright metallic logo
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
    (1.0, 0.8, 0.6, 1),  # Warmer amber light
    metallic=0.0,
    roughness=0.0
)

# Add emission to interior light
light_mat = interior_light.data.materials[0]
light_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (1.0, 0.8, 0.6, 1)
light_mat.node_tree.nodes["Principled BSDF"].inputs['Emission Strength'].default_value = 8.0

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
        (0.1, 0.1, 0.1, 1),
        metallic=0.0,
        roughness=0.95
    )

# --- SCENE SETUP ---

# Lighting
light_data = bpy.data.lights.new(name="Key_Light", type='AREA')
light_data.energy = 150
light_data.size = 0.5
light_object = bpy.data.objects.new(name="Key_Light", object_data=light_data)
bpy.context.collection.objects.link(light_object)
light_object.location = (0.5, -0.6, 0.8)
light_object.rotation_euler = (math.radians(60), 0, math.radians(-30))

# Fill light
fill_light_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
fill_light_data.energy = 80
fill_light_data.size = 0.4
fill_light_object = bpy.data.objects.new(name="Fill_Light", object_data=fill_light_data)
bpy.context.collection.objects.link(fill_light_object)
fill_light_object.location = (-0.4, -0.5, 0.6)
fill_light_object.rotation_euler = (math.radians(70), 0, math.radians(30))

# Camera
camera_data = bpy.data.cameras.new(name="Microwave_Camera")
camera_object = bpy.data.objects.new("Microwave_Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
camera_object.location = (0.45, -0.55, 0.35)
camera_object.rotation_euler = (math.radians(75), 0, math.radians(40))

# Set as active camera
bpy.context.scene.camera = camera_object

# Set render settings for better preview
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 60)
print("MODERN BLACK MICROWAVE GENERATED SUCCESSFULLY!")
print("=" * 60)
print("\nVariations applied:")
print("  ✓ Sleek black exterior finish")
print("  ✓ Enhanced metallic accents on handle and buttons")
print("  ✓ Warmer amber display and interior lighting")
print("=" * 60)