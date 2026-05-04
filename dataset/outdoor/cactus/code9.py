import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create simple Aloe Vera - rosette of thick pointed leaves
def create_aloe_leaf(name, length, width, location, rotation):
    # Create simple leaf from cube
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=location,
        rotation=rotation
    )
    leaf = bpy.context.active_object
    leaf.name = name
    leaf.scale = (width, 0.15, length)
    
    # Taper the leaf
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mesh = leaf.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    for vert in bm.verts:
        z = vert.co.z
        # Taper toward tip
        if z > 0:
            taper = 1 - (z / 0.5) * 0.6
            vert.co.x *= taper
    
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.shade_smooth()
    
    return leaf

# Create rosette of leaves (simple arrangement)
leaves = []
num_leaves = 12

for i in range(num_leaves):
    angle = (i / num_leaves) * 2 * math.pi
    
    # Position leaves in rosette
    x_offset = math.cos(angle) * 0.1
    y_offset = math.sin(angle) * 0.1
    z_base = 0.15
    
    # Leaf parameters
    leaf_length = random.uniform(0.35, 0.45)
    leaf_width = random.uniform(0.08, 0.12)
    
    # Calculate leaf position and rotation
    leaf_z = z_base + leaf_length / 2
    rot_x = 0
    rot_y = math.radians(random.uniform(25, 40))  # Outward angle
    rot_z = angle
    
    leaf = create_aloe_leaf(
        f"Leaf_{i}",
        leaf_length,
        leaf_width,
        (x_offset, y_offset, leaf_z),
        (rot_x, rot_y, rot_z)
    )
    leaves.append(leaf)

# Create simple center/base
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.12,
    depth=0.15,
    location=(0, 0, 0.075)
)
center = bpy.context.active_object
center.name = "Center"
bpy.ops.object.shade_smooth()

# Add small white spots on leaves (simple spheres)
spots = []
for leaf in leaves[:8]:  # Only on some leaves to keep it simple
    for s in range(5):
        # Random position on leaf
        local_x = random.uniform(-0.05, 0.05)
        local_z = random.uniform(0, 0.3)
        
        spot_pos = leaf.matrix_world @ Vector((local_x, 0.08, local_z))
        
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.012,
            location=spot_pos,
            segments=6,
            ring_count=4
        )
        spot = bpy.context.active_object
        spot.name = "Spot"
        spot.scale = (1, 0.5, 1)
        spots.append(spot)

# Create materials
def create_aloe_material():
    mat = bpy.data.materials.new(name="AloeMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Gray-green aloe color
        bsdf.inputs['Base Color'].default_value = (0.38, 0.50, 0.35, 1)
        bsdf.inputs['Roughness'].default_value = 0.5
    return mat

def create_spot_material():
    mat = bpy.data.materials.new(name="SpotMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # White spots
        bsdf.inputs['Base Color'].default_value = (0.85, 0.88, 0.82, 1)
        bsdf.inputs['Roughness'].default_value = 0.6
    return mat

aloe_mat = create_aloe_material()
spot_mat = create_spot_material()

# Apply materials
for leaf in leaves + [center]:
    leaf.data.materials.append(aloe_mat)

for spot in spots:
    spot.data.materials.append(spot_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = leaves + [center] + spots

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = center
bpy.ops.object.join()
center.name = "AloeVera"

# Create simple pot
bpy.ops.mesh.primitive_cylinder_add(
    vertices=12,
    radius=0.22,
    depth=0.18,
    location=(0, 0, 0.09)
)
pot = bpy.context.active_object
pot.name = "Pot"

pot_mat = bpy.data.materials.new(name="PotMaterial")
pot_mat.use_nodes = True
pot_nodes = pot_mat.node_tree.nodes
pot_bsdf = pot_nodes.get("Principled BSDF")
if pot_bsdf:
    # Simple terracotta
    pot_bsdf.inputs['Base Color'].default_value = (0.70, 0.40, 0.28, 1)
    pot_bsdf.inputs['Roughness'].default_value = 0.8
pot.data.materials.append(pot_mat)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 0))
ground = bpy.context.active_object

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.75, 0.70, 0.65, 1)
    ground_bsdf.inputs['Roughness'].default_value = 0.7
ground.data.materials.append(ground_mat)

# Camera
bpy.ops.object.camera_add(location=(1.5, -1.5, 0.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

# Simple lighting
bpy.ops.object.light_add(type='SUN', location=(2, -2, 4))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.rotation_euler = (math.radians(50), math.radians(30), 0)

print("Aloe Vera created successfully!")