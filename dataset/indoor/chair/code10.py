import bpy

# -------------------------
# Helper: Clear Scene
# -------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -------------------------
# Units (Slightly refined proportions)
# -------------------------
LEG_HEIGHT = 0.47
SEAT_WIDTH = 0.44
SEAT_DEPTH = 0.42
SEAT_THICKNESS = 0.035
LEG_THICKNESS = 0.045
STRETCHER_THICKNESS = 0.028
BACK_HEIGHT = 0.52
BACK_THICKNESS = 0.025
SLAT_WIDTH = 0.028
SLAT_SPACING = 0.045

# -------------------------
# Materials
# -------------------------
wood = bpy.data.materials.new(name="MahoganyWood")
wood.use_nodes = True
nodes = wood.node_tree.nodes
links = wood.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')  # ← Fixed this line
output = nodes.new(type='ShaderNodeOutputMaterial')
noise = nodes.new(type='ShaderNodeTexNoise')
ramp = nodes.new(type='ShaderNodeValToRGB')
mix = nodes.new(type='ShaderNodeMix')

# Position nodes
bsdf.location = (300, 0)
output.location = (500, 0)
noise.location = (-300, 0)
ramp.location = (-100, 0)
mix.location = (100, 0)

# Configure nodes
noise.inputs['Scale'].default_value = 15.0
noise.inputs['Detail'].default_value = 8.0

# Color ramp for wood grain
ramp.color_ramp.elements[0].color = (0.15, 0.08, 0.04, 1.0)  # Dark mahogany
ramp.color_ramp.elements[1].color = (0.32, 0.18, 0.08, 1.0)  # Medium mahogany

# Mix node setup
mix.data_type = 'RGBA'
mix.blend_type = 'MIX'
mix.inputs['Factor'].default_value = 0.7
mix.inputs[6].default_value = (0.45, 0.28, 0.12, 1.0)  # Golden highlight

# BSDF properties
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['Metallic'].default_value = 0.0

# Connect nodes
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], mix.inputs[7])
links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
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
bpy.ops.object.camera_add(location=(1.2, -1.8, 1.5))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.6)

# Set camera as active
bpy.context.scene.camera = camera

print("✅ Mahogany chair created successfully!")