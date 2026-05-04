import bpy
import math
import random

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Plant dimensions (in meters)
pot_radius = 0.15
pot_height = 0.18
pot_rim_height = 0.02
soil_height = 0.03
stem_height = 0.5
stem_radius = 0.008
num_leaves = 16
leaf_length = 0.15
leaf_width = 0.08

# Set random seed for reproducible plant generation
random.seed(42)

# Materials
def create_ceramic_material():
    """Create a bright blue ceramic pot material"""
    mat = bpy.data.materials.new(name="Ceramic")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.15, 0.4, 0.8, 1.0)  # Bright blue
    node_bsdf.inputs['Roughness'].default_value = 0.2
    node_bsdf.inputs['Metallic'].default_value = 0.0
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_soil_material():
    """Create a dark soil material"""
    mat = bpy.data.materials.new(name="Soil")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.15, 0.1, 0.08, 1.0)  # Dark brown
    node_bsdf.inputs['Roughness'].default_value = 0.95
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_stem_material():
    """Create a green/brown stem material"""
    mat = bpy.data.materials.new(name="Stem")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.2, 0.4, 0.15, 1.0)  # Dark green
    node_bsdf.inputs['Roughness'].default_value = 0.6
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

def create_leaf_material():
    """Create a vibrant green leaf material"""
    mat = bpy.data.materials.new(name="Leaf")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 0.2, 1.0)  # Bright green
    node_bsdf.inputs['Roughness'].default_value = 0.4
    
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_output.location = (200, 0)
    
    mat.node_tree.links.new(node_bsdf.outputs['BSDF'], node_output.inputs['Surface'])
    
    return mat

# Create materials
ceramic_mat = create_ceramic_material()
soil_mat = create_soil_material()
stem_mat = create_stem_material()
leaf_mat = create_leaf_material()

# Create pot (using a cylinder with a slight taper)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=1)
pot = bpy.context.active_object
pot.name = "Pot"
pot.dimensions = (pot_radius * 2, pot_radius * 2, pot_height)
pot.location = (0, 0, pot_height/2)
pot.data.materials.append(ceramic_mat)

# Add taper modifier to pot for realistic shape
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Scale top of pot slightly outward for rim effect
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Select top vertices and scale them
for v in pot.data.vertices:
    if v.co.z > pot_height * 0.4:
        v.select = True

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.transform.resize(value=(1.1, 1.1, 1.0))
bpy.ops.object.mode_set(mode='OBJECT')

# Create pot rim
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=1)
pot_rim = bpy.context.active_object
pot_rim.name = "Pot_Rim"
pot_rim.dimensions = (pot_radius * 2.2, pot_radius * 2.2, pot_rim_height)
pot_rim.location = (0, 0, pot_height + pot_rim_height/2)
pot_rim.data.materials.append(ceramic_mat)

# Create soil
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=1)
soil = bpy.context.active_object
soil.name = "Soil"
soil.dimensions = (pot_radius * 1.8, pot_radius * 1.8, soil_height)
soil.location = (0, 0, pot_height + soil_height/2)
soil.data.materials.append(soil_mat)

# Add slight noise to soil surface for realism
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

for v in soil.data.vertices:
    if v.co.z > 0:
        v.co.z += random.uniform(-0.005, 0.005)

bpy.ops.object.mode_set(mode='OBJECT')

# Create main stem
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1, depth=1)
stem = bpy.context.active_object
stem.name = "Stem"
stem.dimensions = (stem_radius * 2, stem_radius * 2, stem_height)
stem.location = (0, 0, pot_height + soil_height + stem_height/2)
stem.data.materials.append(stem_mat)

# Add slight curve to stem for natural look
bpy.ops.object.modifier_add(type='SIMPLE_DEFORM')
stem.modifiers["SimpleDeform"].deform_method = 'BEND'
stem.modifiers["SimpleDeform"].angle = math.radians(10)
stem.modifiers["SimpleDeform"].deform_axis = 'Y'
bpy.ops.object.modifier_apply(modifier="SimpleDeform")

# Create leaves arranged in a spiral pattern
leaves = []
stem_top_z = pot_height + soil_height + stem_height

for i in range(num_leaves):
    # Calculate position along stem (leaves at different heights)
    height_ratio = 0.3 + (i / num_leaves) * 0.7  # Leaves in upper 70% of stem
    leaf_z = pot_height + soil_height + stem_height * height_ratio
    
    # Spiral angle
    angle = (i / num_leaves) * math.pi * 4  # Multiple rotations
    
    # Create leaf using a flattened sphere (ellipsoid)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1)
    leaf = bpy.context.active_object
    leaf.name = f"Leaf_{i+1}"
    
    # Scale to create leaf shape
    leaf.dimensions = (leaf_width, leaf_length, 0.01)
    
    # Position leaf
    offset_distance = stem_radius + leaf_length/3
    leaf_x = math.cos(angle) * offset_distance
    leaf_y = math.sin(angle) * offset_distance
    leaf.location = (leaf_x, leaf_y, leaf_z)
    
    # Rotate leaf to point outward and slightly up
    leaf.rotation_euler = (
        math.radians(60 + random.uniform(-10, 10)),  # Tilt up
        0,
        angle + math.radians(random.uniform(-15, 15))  # Face outward with variation
    )
    
    leaf.data.materials.append(leaf_mat)
    leaves.append(leaf)
    
    # Add smooth shading to leaf
    bpy.ops.object.shade_smooth()

# Add smooth shading to all cylindrical objects
for obj in [pot, pot_rim, soil, stem]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

# Optional: Join pot components
bpy.ops.object.select_all(action='DESELECT')
pot.select_set(True)
pot_rim.select_set(True)
bpy.context.view_layer.objects.active = pot
bpy.ops.object.join()
pot.name = "Pot_Complete"

# Optional: Join all leaves into one object
bpy.ops.object.select_all(action='DESELECT')
for leaf in leaves:
    leaf.select_set(True)
if len(leaves) > 0:
    bpy.context.view_layer.objects.active = leaves[0]
    bpy.ops.object.join()
    bpy.context.active_object.name = "Leaves"

# Create collection for organization
collection = bpy.data.collections.new("Potted_Plant")
bpy.context.scene.collection.children.link(collection)

# Move all plant objects to collection
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if obj.name not in bpy.context.scene.collection.objects:
            continue
        bpy.context.scene.collection.objects.unlink(obj)
        collection.objects.link(obj)

# Set up camera
camera_distance = 0.8
camera_height = 0.4
bpy.ops.object.camera_add(
    location=(camera_distance, -camera_distance, camera_height),
    rotation=(math.radians(75), 0, math.radians(45))
)
camera = bpy.context.active_object
camera.data.lens = 50
bpy.context.scene.camera = camera

# Set up lighting
# Main sunlight
bpy.ops.object.light_add(type='SUN', location=(3, -3, 5))
sun = bpy.context.active_object
sun.data.energy = 2.5
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# Softer fill light
bpy.ops.object.light_add(type='AREA', location=(-2, 2, 3))
area_light = bpy.context.active_object
area_light.data.energy = 80
area_light.data.size = 3

# Set render engine to Cycles for better materials
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Set background to white for clean look
bpy.context.scene.world.use_nodes = True
bg_node = bpy.context.scene.world.node_tree.nodes['Background']
bg_node.inputs['Color'].default_value = (1, 1, 1, 1)
bg_node.inputs['Strength'].default_value = 1.0

print("Potted plant created successfully!")
print(f"Pot dimensions: {pot_radius*2}m diameter x {pot_height}m height")
print(f"Plant height: {stem_height}m with {num_leaves} leaves")