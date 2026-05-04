import bpy
import bmesh
import math

# -------------------------
# Helper: Clear Scene
# -------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -------------------------
# Units (slightly increased for robustness)
# -------------------------
LEG_HEIGHT = 0.45
SEAT_WIDTH = 0.44  # Slightly wider
SEAT_DEPTH = 0.42  # Slightly deeper
SEAT_THICKNESS = 0.04  # Thicker seat
LEG_THICKNESS = 0.045  # Thicker legs
STRETCHER_THICKNESS = 0.03  # Thicker stretchers
BACK_HEIGHT = 0.50
BACK_THICKNESS = 0.025  # Slightly thicker back
SLAT_WIDTH = 0.028  # Slightly wider slats
SLAT_SPACING = 0.04

# -------------------------
# Materials
# -------------------------
# Rich mahogany wood material
mahogany_wood = bpy.data.materials.new(name="Mahogany_Wood")
mahogany_wood.use_nodes = True
nodes = mahogany_wood.node_tree.nodes
links = mahogany_wood.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Add Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (300, 0)

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (600, 0)

# Add Noise Texture for wood grain
noise = nodes.new(type='ShaderNodeTexNoise')
noise.location = (-300, 100)
noise.inputs['Scale'].default_value = 25.0
noise.inputs['Detail'].default_value = 15.0

# Add ColorRamp for wood color variation
ramp = nodes.new(type='ShaderNodeValToRGB')
ramp.location = (0, 100)
ramp.color_ramp.elements[0].color = (0.2, 0.08, 0.05, 1.0)  # Dark mahogany
ramp.color_ramp.elements[1].color = (0.45, 0.15, 0.08, 1.0)  # Light mahogany

# Set material properties
bsdf.inputs['Base Color'].default_value = (0.35, 0.12, 0.06, 1.0)  # Rich mahogany color
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['IOR'].default_value = 1.5

# Connect nodes
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Golden metal material for stretchers
gold_metal = bpy.data.materials.new(name="Gold_Metal")
gold_metal.use_nodes = True
gold_nodes = gold_metal.node_tree.nodes
gold_links = gold_metal.node_tree.links

# Clear default nodes
for node in gold_nodes:
    gold_nodes.remove(node)

# Add nodes for metal material
gold_bsdf = gold_nodes.new(type='ShaderNodeBsdfPrincipled')
gold_bsdf.location = (0, 0)
gold_output = gold_nodes.new(type='ShaderNodeOutputMaterial')
gold_output.location = (300, 0)

# Set gold metal properties
gold_bsdf.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)  # Gold color
gold_bsdf.inputs['Metallic'].default_value = 1.0
gold_bsdf.inputs['Roughness'].default_value = 0.1

gold_links.new(gold_bsdf.outputs['BSDF'], gold_output.inputs['Surface'])

def apply_wood_mat(obj):
    obj.data.materials.append(mahogany_wood)

def apply_metal_mat(obj):
    obj.data.materials.append(gold_metal)

# -------------------------
# Seat
# -------------------------
bpy.ops.mesh.primitive_cube_add()
seat = bpy.context.active_object
seat.name = "Seat"
seat.scale = (SEAT_WIDTH/2, SEAT_DEPTH/2, SEAT_THICKNESS/2)
seat.location = (0, 0, LEG_HEIGHT)
apply_wood_mat(seat)

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
    apply_wood_mat(leg)
    legs.append(leg)

# -------------------------
# Stretchers (Golden Metal)
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
    apply_metal_mat(stretcher)

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
    apply_wood_mat(post)

# -------------------------
# Top Back Rail
# -------------------------
bpy.ops.mesh.primitive_cube_add()
top_rail = bpy.context.active_object
top_rail.scale = (SEAT_WIDTH/2, BACK_THICKNESS/2, BACK_THICKNESS/2)
top_rail.location = (0, -SEAT_DEPTH/2, LEG_HEIGHT + BACK_HEIGHT - BACK_THICKNESS)
apply_wood_mat(top_rail)

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
    apply_wood_mat(slat)

# -------------------------
# Bottom Back Rail
# -------------------------
bpy.ops.mesh.primitive_cube_add()
bottom_rail = bpy.context.active_object
bottom_rail.name = "Bottom_Back_Rail"
bottom_rail.scale = (SEAT_WIDTH/2, BACK_THICKNESS/2, BACK_THICKNESS/2)
bottom_rail.location = (0, -SEAT_DEPTH/2, LEG_HEIGHT + 0.08)
apply_wood_mat(bottom_rail)

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
bpy.ops.object.camera_add(location=(1.2, -1.5, 1.8))
camera = bpy.context.active_object
camera.rotation_euler = (0.7, 0, 0.8)
bpy.context.scene.camera = camera

# -------------------------
# Lighting
# -------------------------
bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
sun = bpy.context.active_object
sun.data.energy = 3.0

print("✅ Mahogany chair with golden accents created successfully!")