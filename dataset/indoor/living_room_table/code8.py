import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Table dimensions (in meters) - slightly thicker for more substantial look
table_length = 1.2
table_width = 0.6
table_height = 0.4
top_thickness = 0.04  # Increased from 0.03
shelf_height = 0.15
shelf_thickness = 0.04  # Increased from 0.03
frame_width = 0.035  # Increased from 0.03

# Materials
def create_mahogany_material():
    """Create a mahogany wood material for the tabletop and shelf"""
    mat = bpy.data.materials.new(name="Mahogany")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add nodes
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.35, 0.15, 0.08, 1.0)  # Rich mahogany color
    node_bsdf.inputs['Roughness'].default_value = 0.3  # Smoother finish
    node_bsdf.inputs['IOR'].default_value = 1.4
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    # Link nodes
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_copper_material():
    """Create a brushed copper material for the frame"""
    mat = bpy.data.materials.new(name="BrushedCopper")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add nodes
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.72, 0.45, 0.20, 1.0)  # Copper color
    node_bsdf.inputs['Metallic'].default_value = 0.95
    node_bsdf.inputs['Roughness'].default_value = 0.4  # Brushed finish
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    # Link nodes
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

# Create materials
mahogany_mat = create_mahogany_material()
copper_mat = create_copper_material()

# Create tabletop
bpy.ops.mesh.primitive_cube_add(size=1)
tabletop = bpy.context.active_object
tabletop.name = "Tabletop"
tabletop.dimensions = (table_length, table_width, top_thickness)
tabletop.location = (0, 0, table_height - top_thickness/2)
tabletop.data.materials.append(mahogany_mat)

# Create shelf
bpy.ops.mesh.primitive_cube_add(size=1)
shelf = bpy.context.active_object
shelf.name = "Shelf"
shelf.dimensions = (table_length - 2*frame_width, table_width - 2*frame_width, shelf_thickness)
shelf.location = (0, 0, shelf_height + shelf_thickness/2)
shelf.data.materials.append(mahogany_mat)

# Create metal frame legs (4 vertical legs)
leg_positions = [
    (table_length/2 - frame_width/2, table_width/2 - frame_width/2),
    (table_length/2 - frame_width/2, -(table_width/2 - frame_width/2)),
    (-(table_length/2 - frame_width/2), table_width/2 - frame_width/2),
    (-(table_length/2 - frame_width/2), -(table_width/2 - frame_width/2))
]

legs = []
for i, (x, y) in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1)
    leg = bpy.context.active_object
    leg.name = f"Leg_{i+1}"
    leg.dimensions = (frame_width, frame_width, table_height)
    leg.location = (x, y, table_height/2)
    leg.data.materials.append(copper_mat)
    legs.append(leg)

# Create horizontal frame pieces (top)
# Long sides (2)
for y_pos in [table_width/2 - frame_width/2, -(table_width/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_long = bpy.context.active_object
    frame_long.name = "Frame_Top_Long"
    frame_long.dimensions = (table_length - 2*frame_width, frame_width, frame_width)
    frame_long.location = (0, y_pos, table_height - frame_width/2)
    frame_long.data.materials.append(copper_mat)

# Short sides (2)
for x_pos in [table_length/2 - frame_width/2, -(table_length/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_short = bpy.context.active_object
    frame_short.name = "Frame_Top_Short"
    frame_short.dimensions = (frame_width, table_width - 2*frame_width, frame_width)
    frame_short.location = (x_pos, 0, table_height - frame_width/2)
    frame_short.data.materials.append(copper_mat)

# Create horizontal frame pieces (shelf level)
# Long sides (2)
for y_pos in [table_width/2 - frame_width/2, -(table_width/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_long = bpy.context.active_object
    frame_long.name = "Frame_Shelf_Long"
    frame_long.dimensions = (table_length - 2*frame_width, frame_width, frame_width)
    frame_long.location = (0, y_pos, shelf_height - frame_width/2)
    frame_long.data.materials.append(copper_mat)

# Short sides (2)
for x_pos in [table_length/2 - frame_width/2, -(table_length/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_short = bpy.context.active_object
    frame_short.name = "Frame_Shelf_Short"
    frame_short.dimensions = (frame_width, table_width - 2*frame_width, frame_width)
    frame_short.location = (x_pos, 0, shelf_height - frame_width/2)
    frame_short.data.materials.append(copper_mat)

# Optional: Join all frame pieces into one object
# Select all objects with "Frame" or "Leg" in their name
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.data.objects:
    if "Frame" in obj.name or "Leg" in obj.name:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

# Join selected objects
if len(bpy.context.selected_objects) > 0:
    bpy.ops.object.join()
    bpy.context.active_object.name = "Copper_Frame"

# Set up camera
bpy.ops.object.camera_add(location=(2, -2, 1.5), rotation=(math.radians(65), 0, math.radians(45)))
camera = bpy.context.active_object
camera.data.lens = 50
bpy.context.scene.camera = camera

# Set up lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0

# Add a softer fill light
bpy.ops.object.light_add(type='AREA', location=(-3, 3, 5))
area_light = bpy.context.active_object
area_light.data.energy = 100
area_light.data.size = 5

# Set render engine to Cycles for better material preview
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Frame the camera to see the table
bpy.ops.object.select_all(action='DESELECT')
tabletop.select_set(True)
bpy.context.view_layer.objects.active = tabletop

print("Mahogany and copper coffee table created successfully!")
print(f"Dimensions: {table_length}m x {table_width}m x {table_height}m")