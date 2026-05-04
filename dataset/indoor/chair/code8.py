import bpy
import bmesh
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
SEAT_WIDTH = 0.42
SEAT_DEPTH = 0.40
SEAT_THICKNESS = 0.04  # Increased from 0.03
LEG_THICKNESS = 0.045  # Slightly increased
STRETCHER_THICKNESS = 0.028  # Slightly increased
BACK_HEIGHT = 0.50
BACK_THICKNESS = 0.025  # Increased from 0.02
SLAT_WIDTH = 0.025
SLAT_SPACING = 0.04

# -------------------------
# Materials (Dark Walnut)
# -------------------------
wood = bpy.data.materials.new(name="DarkWalnut")
wood.use_nodes = True
nodes = wood.node_tree.nodes
links = wood.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Add Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)

# Add output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)

# Add noise texture for wood grain
noise = nodes.new(type='ShaderNodeTexNoise')
noise.location = (-600, 0)
noise.inputs['Scale'].default_value = 12.0
noise.inputs['Detail'].default_value = 8.0
noise.inputs['Roughness'].default_value = 0.6

# Add ColorRamp for wood colors
ramp = nodes.new(type='ShaderNodeValToRGB')
ramp.location = (-300, 0)

# Set wood color stops - dark walnut
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.15, 0.08, 0.05, 1.0)  # Dark brown
ramp.color_ramp.elements[1].position = 1.0
ramp.color_ramp.elements[1].color = (0.35, 0.22, 0.15, 1.0)  # Medium brown

# Connect nodes
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

# Set material properties
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['IOR'].default_value = 1.4

# Connect to output
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

def apply_mat(obj):
    obj.data.materials.append(wood)

def add_rounded_edges(obj):
    """Add subtle rounding to edges"""
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # Add bevel modifier for rounded edges
    bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel_mod.width = 0.002
    bevel_mod.segments = 3
    
    obj.select_set(False)

# -------------------------
# Seat
# -------------------------
bpy.ops.mesh.primitive_cube_add()
seat = bpy.context.active_object
seat.name = "Seat"
seat.scale = (SEAT_WIDTH/2, SEAT_DEPTH/2, SEAT_THICKNESS/2)
seat.location = (0, 0, LEG_HEIGHT)
apply_mat(seat)
add_rounded_edges(seat)

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
    add_rounded_edges(leg)
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
    add_rounded_edges(stretcher)

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
    add_rounded_edges(post)

# -------------------------
# Top Back Rail
# -------------------------
bpy.ops.mesh.primitive_cube_add()
top_rail = bpy.context.active_object
top_rail.scale = (SEAT_WIDTH/2, BACK_THICKNESS/2, BACK_THICKNESS/2)
top_rail.location = (0, -SEAT_DEPTH/2, LEG_HEIGHT + BACK_HEIGHT - BACK_THICKNESS)
apply_mat(top_rail)
add_rounded_edges(top_rail)

# -------------------------
# Back Slats
# -------------------------
slat_y = -SEAT_DEPTH/2 + BACK_THICKNESS
slat_z_start = LEG_HEIGHT + 0.08
slat_count = 5

for i in range(slat_count):
    x = -SEAT_WIDTH/2 + 0.07 + i * (SLAT_WIDTH + SLAT_SPACING)
    
    bpy.ops.mesh.primitive_cube_add()
    slat = bpy.context.active_object
    slat.scale = (SLAT_WIDTH/2, BACK_THICKNESS/2, (BACK_HEIGHT - 0.1)/2)
    slat.location = (x, slat_y, slat_z_start + (BACK_HEIGHT - 0.1)/2)
    apply_mat(slat)
    add_rounded_edges(slat)

# -------------------------
# Bottom Back Rail
# -------------------------
bpy.ops.mesh.primitive_cube_add()
bottom_rail = bpy.context.active_object
bottom_rail.name = "Bottom_Back_Rail"
bottom_rail.scale = (SEAT_WIDTH/2, BACK_THICKNESS/2, BACK_THICKNESS/2)
bottom_rail.location = (0, -SEAT_DEPTH/2, LEG_HEIGHT + 0.08)
apply_mat(bottom_rail)
add_rounded_edges(bottom_rail)

# -------------------------
# Shade Smooth
# -------------------------
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

# -------------------------
# Camera Setup
# -------------------------
bpy.ops.object.camera_add(location=(1.5, -2.0, 1.2))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.8)

# Set as active camera
bpy.context.scene.camera = camera

# -------------------------
# Lighting
# -------------------------
bpy.ops.object.light_add(type='SUN', location=(3, 3, 5))
sun = bpy.context.active_object
sun.data.energy = 5.0

print("✅ Dark walnut chair variation created successfully!")