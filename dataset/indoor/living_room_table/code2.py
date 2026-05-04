import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Table dimensions (in meters) - slightly thicker surfaces
table_length = 1.2
table_width = 0.6
table_height = 0.4
top_thickness = 0.04  # Increased from 0.03
shelf_height = 0.15
shelf_thickness = 0.04  # Increased from 0.03
frame_width = 0.03

# Materials
def create_cherry_wood_material():
    """Create a rich cherry wood material for the tabletop and shelf"""
    mat = bpy.data.materials.new(name="CherryWood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add nodes
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.45, 0.2, 0.15, 1.0)  # Rich cherry wood color
    node_bsdf.inputs['Roughness'].default_value = 0.3  # Smoother finish
    node_bsdf.inputs['IOR'].default_value = 1.5
    
    # Add noise texture for wood grain
    noise_texture = nodes.new(type='ShaderNodeTexNoise')
    noise_texture.location = (-200, 0)
    noise_texture.inputs['Scale'].default_value = 15.0
    noise_texture.inputs['Detail'].default_value = 10.0
    
    # Add color ramp for wood grain contrast
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (0, 0)
    color_ramp.color_ramp.elements[0].color = (0.35, 0.15, 0.1, 1.0)  # Dark cherry
    color_ramp.color_ramp.elements[1].color = (0.55, 0.25, 0.2, 1.0)  # Light cherry
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (500, 0)
    
    # Link nodes
    links = mat.node_tree.links
    links.new(noise_texture.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_copper_material():
    """Create a brushed copper material for the frame"""
    mat = bpy.data.materials.new(name="BrushedCopper")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Add nodes
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.72, 0.45, 0.2, 1.0)  # Copper color
    node_bsdf.inputs['Metallic'].default_value = 0.8
    node_bsdf.inputs['Roughness'].default_value = 0.4  # Brushed finish
    
    # Add noise for brushed texture
    noise_texture = nodes.new(type='ShaderNodeTexNoise')
    noise_texture.location = (-200, 0)
    noise_texture.inputs['Scale'].default_value = 50.0
    noise_texture.inputs['Detail'].default_value = 15.0
    
    # Mix noise with base roughness
    mix_node = nodes.new(type='ShaderNodeMix')
    mix_node.location = (0, 0)
    mix_node.data_type = 'RGBA'
    mix_node.inputs['Factor'].default_value = 0.3
    mix_node.inputs[6].default_value = (0.4, 0.4, 0.4, 1.0)
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (500, 0)
    
    # Link nodes
    links = mat.node_tree.links
    links.new(noise_texture.outputs['Color'], mix_node.inputs[7])
    links.new(mix_node.outputs['Result'], node_bsdf.inputs['Roughness'])
    links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

# Create materials
wood_mat = create_cherry_wood_material()
metal_mat = create_copper_material()

# Create tabletop
bpy.ops.mesh.primitive_cube_add(size=1)
tabletop = bpy.context.active_object
tabletop.name = "Tabletop"
tabletop.dimensions = (table_length, table_width, top_thickness)
tabletop.location = (0, 0, table_height - top_thickness/2)
tabletop.data.materials.append(wood_mat)

# Create shelf
bpy.ops.mesh.primitive_cube_add(size=1)
shelf = bpy.context.active_object
shelf.name = "Shelf"
shelf.dimensions = (table_length - 2*frame_width, table_width - 2*frame_width, shelf_thickness)
shelf.location = (0, 0, shelf_height + shelf_thickness/2)
shelf.data.materials.append(wood_mat)

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
    leg.data.materials.append(metal_mat)
    legs.append(leg)

# Create horizontal frame pieces (top)
# Long sides (2)
for y_pos in [table_width/2 - frame_width/2, -(table_width/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_long = bpy.context.active_object
    frame_long.name = "Frame_Top_Long"
    frame_long.dimensions = (table_length - 2*frame_width, frame_width, frame_width)
    frame_long.location = (0, y_pos, table_height - frame_width/2)
    frame_long.data.materials.append(metal_mat)

# Short sides (2)
for x_pos in [table_length/2 - frame_width/2, -(table_length/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_short = bpy.context.active_object
    frame_short.name = "Frame_Top_Short"
    frame_short.dimensions = (frame_width, table_width - 2*frame_width, frame_width)
    frame_short.location = (x_pos, 0, table_height - frame_width/2)
    frame_short.data.materials.append(metal_mat)

# Create horizontal frame pieces (shelf level)
# Long sides (2)
for y_pos in [table_width/2 - frame_width/2, -(table_width/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_long = bpy.context.active_object
    frame_long.name = "Frame_Shelf_Long"
    frame_long.dimensions = (table_length - 2*frame_width, frame_width, frame_width)
    frame_long.location = (0, y_pos, shelf_height - frame_width/2)
    frame_long.data.materials.append(metal_mat)

# Short sides (2)
for x_pos in [table_length/2 - frame_width/2, -(table_length/2 - frame_width/2)]:
    bpy.ops.mesh.primitive_cube_add(size=1)
    frame_short = bpy.context.active_object
    frame_short.name = "Frame_Shelf_Short"
    frame_short.dimensions = (frame_width, table_width - 2*frame_width, frame_width)
    frame_short.location = (x_pos, 0, shelf_height - frame_width/2)
    frame_short.data.materials.append(metal_mat)

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
bpy.ops.object.camera_add(location=(2.2, -2.2, 1.8), rotation=(math.radians(60), 0, math.radians(45)))
camera = bpy.context.active_object
camera.data.lens = 45
bpy.context.scene.camera = camera

# Set up lighting
bpy.ops.object.light_add(type='SUN', location=(4, -4, 8))
sun = bpy.context.active_object
sun.data.energy = 3.0

# Add a warm fill light
bpy.ops.object.light_add(type='AREA', location=(-2, 2, 4))
area_light = bpy.context.active_object
area_light.data.energy = 80
area_light.data.size = 4
area_light.data.color = (1.0, 0.9, 0.7)

# Set render engine to Cycles for better material preview
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Frame the camera to see the table
bpy.ops.object.select_all(action='DESELECT')
tabletop.select_set(True)
bpy.context.view_layer.objects.active = tabletop

print("Cherry wood coffee table with copper frame created successfully!")
print(f"Dimensions: {table_length}m x {table_width}m x {table_height}m")