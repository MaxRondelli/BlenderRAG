import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create simple Jade Plant (Crassula ovata) - tree-like succulent
def create_jade_leaf(location, rotation, size=1):
    # Create simple oval leaf from sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.08 * size,
        location=location,
        segments=8,
        ring_count=6
    )
    leaf = bpy.context.active_object
    leaf.name = "Leaf"
    leaf.scale = (1.2, 0.3, 1)  # Flatten to make oval
    leaf.rotation_euler = rotation
    bpy.ops.object.shade_smooth()
    return leaf

# Create simple trunk
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.06,
    depth=0.4,
    location=(0, 0, 0.2)
)
trunk = bpy.context.active_object
trunk.name = "Trunk"
bpy.ops.object.shade_smooth()

# Create main branches (simple cylinders)
branches = [trunk]

# Branch 1 - right
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.045,
    depth=0.25,
    location=(0.12, 0, 0.5),
    rotation=(0, math.radians(40), 0)
)
branch1 = bpy.context.active_object
branch1.name = "Branch1"
branches.append(branch1)

# Branch 2 - left
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.045,
    depth=0.28,
    location=(-0.1, 0.05, 0.52),
    rotation=(0, math.radians(-35), math.radians(15))
)
branch2 = bpy.context.active_object
branch2.name = "Branch2"
branches.append(branch2)

# Branch 3 - front
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.04,
    depth=0.22,
    location=(0.02, -0.08, 0.48),
    rotation=(0, math.radians(-30), math.radians(-25))
)
branch3 = bpy.context.active_object
branch3.name = "Branch3"
branches.append(branch3)

# Shade branches smooth
for branch in branches:
    bpy.context.view_layer.objects.active = branch
    bpy.ops.object.shade_smooth()

# Add leaf pairs at branch ends
leaves = []

# Leaves on branch 1
for i in range(3):
    angle = (i / 3) * 2 * math.pi
    offset = 0.08 + i * 0.03
    
    leaf_pos = Vector((0.23, 0, 0.62)) + Vector((
        math.cos(angle) * 0.06,
        math.sin(angle) * 0.06,
        offset
    ))
    
    leaf = create_jade_leaf(
        leaf_pos,
        (random.uniform(-0.2, 0.2), random.uniform(-0.3, 0.3), angle),
        random.uniform(0.9, 1.1)
    )
    leaves.append(leaf)

# Leaves on branch 2
for i in range(3):
    angle = (i / 3) * 2 * math.pi
    offset = 0.08 + i * 0.03
    
    leaf_pos = Vector((-0.2, 0.08, 0.64)) + Vector((
        math.cos(angle) * 0.06,
        math.sin(angle) * 0.06,
        offset
    ))
    
    leaf = create_jade_leaf(
        leaf_pos,
        (random.uniform(-0.2, 0.2), random.uniform(-0.3, 0.3), angle),
        random.uniform(0.9, 1.1)
    )
    leaves.append(leaf)

# Leaves on branch 3
for i in range(2):
    angle = (i / 2) * 2 * math.pi
    offset = 0.06 + i * 0.03
    
    leaf_pos = Vector((0.03, -0.17, 0.57)) + Vector((
        math.cos(angle) * 0.05,
        math.sin(angle) * 0.05,
        offset
    ))
    
    leaf = create_jade_leaf(
        leaf_pos,
        (random.uniform(-0.2, 0.2), random.uniform(-0.3, 0.3), angle),
        random.uniform(0.8, 1.0)
    )
    leaves.append(leaf)

# Add leaves on trunk
for i in range(2):
    angle = random.uniform(0, 2 * math.pi)
    
    leaf_pos = Vector((
        math.cos(angle) * 0.08,
        math.sin(angle) * 0.08,
        0.35
    ))
    
    leaf = create_jade_leaf(
        leaf_pos,
        (random.uniform(-0.2, 0.2), random.uniform(-0.3, 0.3), angle),
        0.8
    )
    leaves.append(leaf)

# Create materials
def create_trunk_material():
    mat = bpy.data.materials.new(name="TrunkMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Brown woody trunk
        bsdf.inputs['Base Color'].default_value = (0.35, 0.25, 0.18, 1)
        bsdf.inputs['Roughness'].default_value = 0.8
    return mat

def create_leaf_material():
    mat = bpy.data.materials.new(name="LeafMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Glossy jade green
        bsdf.inputs['Base Color'].default_value = (0.25, 0.48, 0.28, 1)
        bsdf.inputs['Roughness'].default_value = 0.2
        
    return mat

trunk_mat = create_trunk_material()
leaf_mat = create_leaf_material()

# Apply materials
for branch in branches:
    branch.data.materials.append(trunk_mat)

for leaf in leaves:
    leaf.data.materials.append(leaf_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = branches + leaves

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = trunk
bpy.ops.object.join()
trunk.name = "JadePlant"

# Create simple pot
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.18,
    depth=0.15,
    location=(0, 0, 0.075)
)
pot = bpy.context.active_object
pot.name = "Pot"

pot_mat = bpy.data.materials.new(name="PotMaterial")
pot_mat.use_nodes = True
pot_nodes = pot_mat.node_tree.nodes
pot_bsdf = pot_nodes.get("Principled BSDF")
if pot_bsdf:
    # Brown ceramic pot
    pot_bsdf.inputs['Base Color'].default_value = (0.45, 0.35, 0.25, 1)
    pot_bsdf.inputs['Roughness'].default_value = 0.6
pot.data.materials.append(pot_mat)

# Create simple table
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, -0.03))
table = bpy.context.active_object
table.name = "Table"
table.scale = (1, 1, 0.03)

table_mat = bpy.data.materials.new(name="TableMaterial")
table_mat.use_nodes = True
table_nodes = table_mat.node_tree.nodes
table_bsdf = table_nodes.get("Principled BSDF")
if table_bsdf:
    # Light wood
    table_bsdf.inputs['Base Color'].default_value = (0.78, 0.68, 0.55, 1)
    table_bsdf.inputs['Roughness'].default_value = 0.5
table.data.materials.append(table_mat)

# Camera
bpy.ops.object.camera_add(location=(1.2, -1.2, 0.6))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

# Simple lighting
bpy.ops.object.light_add(type='SUN', location=(2, -2, 3))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(55), math.radians(25), 0)

print("Jade Plant created successfully!")