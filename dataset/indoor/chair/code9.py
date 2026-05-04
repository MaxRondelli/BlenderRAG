import bpy
import math

# -------------------------
# Helper: Clear Scene
# -------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -------------------------
# Units (Modified for variation)
# -------------------------
LEG_HEIGHT = 0.45
SEAT_WIDTH = 0.46  # Wider than original
SEAT_DEPTH = 0.42  # Slightly deeper
SEAT_THICKNESS = 0.035  # Slightly thicker
LEG_THICKNESS = 0.045  # Thicker legs
STRETCHER_THICKNESS = 0.03  # Thicker stretchers
BACK_HEIGHT = 0.50
BACK_THICKNESS = 0.025  # Thicker back
SLAT_WIDTH = 0.035  # Thicker slats
SLAT_SPACING = 0.04

# -------------------------
# Materials (Rich Mahogany)
# -------------------------
wood = bpy.data.materials.new(name="Mahogany_Wood")
wood.use_nodes = True
wood.node_tree.nodes.clear()

# Add shader nodes
bsdf = wood.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
output = wood.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
noise = wood.node_tree.nodes.new(type='ShaderNodeTexNoise')
ramp = wood.node_tree.nodes.new(type='ShaderNodeValToRGB')

# Configure noise texture
noise.inputs['Scale'].default_value = 25.0
noise.inputs['Detail'].default_value = 8.0
noise.inputs['Roughness'].default_value = 0.6

# Configure color ramp for mahogany tones
ramp.color_ramp.elements[0].color = (0.25, 0.12, 0.08, 1.0)  # Dark mahogany
ramp.color_ramp.elements[1].color = (0.45, 0.25, 0.18, 1.0)  # Light mahogany

# Configure BSDF
bsdf.inputs['Base Color'].default_value = (0.35, 0.18, 0.12, 1.0)
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.location = (400, 0)

# Link nodes
links = wood.node_tree.links
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

def apply_mat(obj):
    obj.data.materials.append(wood)

# -------------------------
# Seat
# -------------------------
bpy.ops.mesh.primitive_cube_add()
seat = bpy.context.active_object
seat.name = "Seat"
seat.scale = (SEAT_WIDTH/2, SEAT_DEPTH/2, SEAT_THICKNESS/2)
seat.location = (0, 0, LEG_HEIGHT)
apply_mat(seat)

# -------------------------
# Legs
# -------------------------
leg_positions = [
    ( SEAT_WIDTH/2 - LEG_THICKNESS/2,  SEAT_DEPTH/2 - LEG_THICKNESS/2),
    (-SEAT_WIDTH/2 + LEG_THICKNESS/2,  SEAT_DEPTH/2 - LEG_THICKNESS/2),
    ( SEAT_WIDTH/2 - LEG_THICKNESS/2, -SEAT_DEPTH/2 + LEG_THICKNESS/2),
    (-SEAT_WIDTH/2 + LEG_THICKNESS/2, -SEAT_DEPTH/2 + LEG_THICKNESS/2),
]

legs = []
for i, (x, y) in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add()
    leg = bpy.context.active_object
    leg.name = f"Leg_{i}"
    leg.scale = (LEG_THICKNESS/2, LEG_THICKNESS/2, LEG_HEIGHT/2)
    leg.location = (x, y, LEG_HEIGHT/2)
    apply_mat(leg)
    legs.append(leg)

# -------------------------
# Stretchers
# -------------------------
def add_stretcher(length, x, y, z, axis='X'):
    bpy.ops.mesh.primitive_cube_add()
    stretcher = bpy.context.active_object
    stretcher.scale = (
        length/2 if axis == 'X' else STRETCHER_THICKNESS/2,
        length/2 if axis == 'Y' else STRETCHER_THICKNESS/2,
        STRETCHER_THICKNESS/2
    )
    stretcher.location = (x, y, z)
    apply_mat(stretcher)

# Side stretchers
stretcher_z = LEG_HEIGHT * 0.45
add_stretcher(SEAT_WIDTH - LEG_THICKNESS, 0,  SEAT_DEPTH/2 - LEG_THICKNESS/2, stretcher_z, axis='X')
add_stretcher(SEAT_WIDTH - LEG_THICKNESS, 0, -SEAT_DEPTH/2 + LEG_THICKNESS/2, stretcher_z, axis='X')

# Front/back stretchers
add_stretcher(SEAT_DEPTH - LEG_THICKNESS,  SEAT_WIDTH/2 - LEG_THICKNESS/2, 0, stretcher_z, axis='Y')
add_stretcher(SEAT_DEPTH - LEG_THICKNESS, -SEAT_WIDTH/2 + LEG_THICKNESS/2, 0, stretcher_z, axis='Y')

# -------------------------
# Back Posts
# -------------------------
for x in (-SEAT_WIDTH/2 + LEG_THICKNESS/2, SEAT_WIDTH/2 - LEG_THICKNESS/2):
    bpy.ops.mesh.primitive_cube_add()
    post = bpy.context.active_object
    post.scale = (LEG_THICKNESS/2, LEG_THICKNESS/2, (LEG_HEIGHT + BACK_HEIGHT)/2)
    post.location = (x, -SEAT_DEPTH/2 + LEG_THICKNESS/2, (LEG_HEIGHT + BACK_HEIGHT)/2)
    apply_mat(post)

# -------------------------
# Top Back Rail
# -------------------------
bpy.ops.mesh.primitive_cube_add()
top_rail = bpy.context.active_object
top_rail.scale = (SEAT_WIDTH/2, BACK_THICKNESS/2, BACK_THICKNESS/2)
top_rail.location = (0, -SEAT_DEPTH/2, LEG_HEIGHT + BACK_HEIGHT - BACK_THICKNESS)
apply_mat(top_rail)

# -------------------------
# Back Slats (Thicker)
# -------------------------
slat_y = -SEAT_DEPTH/2 + BACK_THICKNESS
slat_z_start = LEG_HEIGHT + 0.08
slat_count = 5

for i in range(slat_count):
    x = -SEAT_WIDTH/2 + 0.08 + i * (SLAT_WIDTH + SLAT_SPACING)
    
    bpy.ops.mesh.primitive_cube_add()
    slat = bpy.context.active_object
    slat.scale = (SLAT_WIDTH/2, BACK_THICKNESS/2, (BACK_HEIGHT - 0.1)/2)
    slat.location = (x, slat_y, slat_z_start + (BACK_HEIGHT - 0.1)/2)
    apply_mat(slat)

# -------------------------
# Bottom Back Rail
# -------------------------
bpy.ops.mesh.primitive_cube_add()
bottom_rail = bpy.context.active_object
bottom_rail.name = "Bottom_Back_Rail"
bottom_rail.scale = (SEAT_WIDTH/2, BACK_THICKNESS/2, BACK_THICKNESS/2)
bottom_rail.location = (0, -SEAT_DEPTH/2, LEG_HEIGHT + 0.08)
apply_mat(bottom_rail)

# -------------------------
# Camera Setup
# -------------------------
bpy.ops.object.camera_add()
camera = bpy.context.active_object
camera.location = (1.2, -1.5, 1.0)
camera.rotation_euler = (1.1, 0, 0.8)

# -------------------------
# Lighting
# -------------------------
bpy.ops.object.light_add(type='SUN')
sun = bpy.context.active_object
sun.location = (2, -2, 3)
sun.data.energy = 3.0

# -------------------------
# Shade Smooth
# -------------------------
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

print("✅ Mahogany chair variation created successfully!")