import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create Fishhook Cactus - small columnar with hooked spines
bpy.ops.mesh.primitive_cylinder_add(
    vertices=13,
    radius=0.18,
    depth=0.8,
    location=(0, 0, 0.4)
)
fishhook = bpy.context.active_object
fishhook.name = "FishhookBody"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=3)
bpy.ops.object.mode_set(mode='OBJECT')

# Add prominent ribs
mesh = fishhook.data
bm = bmesh.new()
bm.from_mesh(mesh)

for vert in bm.verts:
    x, y, z = vert.co
    angle = math.atan2(y, x)
    
    # Create prominent ribs
    ridge_offset = abs(math.sin(angle * 6.5)) * 0.1
    vert.co.x *= (1 + ridge_offset)
    vert.co.y *= (1 + ridge_offset)

bm.to_mesh(mesh)
bm.free()
bpy.ops.object.shade_smooth()

# Create hooked spines (distinctive feature)
def create_hooked_spine(location, rotation):
    # Create straight part
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6,
        radius=0.006,
        depth=0.12,
        location=location,
        rotation=rotation
    )
    spine_base = bpy.context.active_object
    spine_base.name = "SpineBase"
    
    # Create hook at tip
    hook_offset = 0.065
    hook_loc = (
        location[0] + math.sin(rotation[1]) * hook_offset * math.cos(rotation[2]),
        location[1] + math.sin(rotation[1]) * hook_offset * math.sin(rotation[2]),
        location[2] + math.cos(rotation[1]) * hook_offset
    )
    
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.015,
        minor_radius=0.004,
        location=hook_loc,
        rotation=rotation
    )
    hook = bpy.context.active_object
    hook.name = "SpineHook"
    hook.scale = (1, 1, 0.4)
    
    return [spine_base, hook]

# Add dense fishhook spines
all_spine_parts = []
num_rows = 10
spines_per_row = 13

for row in range(num_rows):
    z = 0.1 + (row * 0.6 / num_rows)
    
    for i in range(spines_per_row):
        angle = (i / spines_per_row) * 2 * math.pi
        radius = 0.19
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        
        rot_z = angle
        rot_y = math.radians(random.uniform(65, 80))
        
        spine_parts = create_hooked_spine((x, y, z), (0, rot_y, rot_z))
        all_spine_parts.extend(spine_parts)

# Create small pink flower on top
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.12,
    location=(0, 0, 0.85),
    segments=10,
    ring_count=6
)
flower_center = bpy.context.active_object
flower_center.name = "FlowerCenter"
flower_center.scale = (1, 1, 0.5)

# Flower petals
for i in range(8):
    angle = (i / 8) * 2 * math.pi
    x = math.cos(angle) * 0.15
    y = math.sin(angle) * 0.15
    
    bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.87))
    petal = bpy.context.active_object
    petal.name = f"Petal_{i}"
    petal.scale = (0.1, 0.06, 0.03)
    petal.rotation_euler = (0, 0, angle)

# Create materials
def create_fishhook_material():
    mat = bpy.data.materials.new(name="FishhookMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 12.0
    
    # Dark green
    color_ramp.color_ramp.elements[0].color = (0.12, 0.28, 0.15, 1)
    color_ramp.color_ramp.elements[1].color = (0.18, 0.38, 0.20, 1)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_hooked_spine_material():
    mat = bpy.data.materials.new(name="HookedSpineMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Red-brown hooked spines
        bsdf.inputs['Base Color'].default_value = (0.65, 0.30, 0.25, 1)
        bsdf.inputs['Roughness'].default_value = 0.6
        
    return mat

def create_flower_material():
    mat = bpy.data.materials.new(name="FlowerMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Pink flower
        bsdf.inputs['Base Color'].default_value = (0.92, 0.45, 0.60, 1)
        bsdf.inputs['Roughness'].default_value = 0.4
    return mat

fishhook_mat = create_fishhook_material()
spine_mat = create_hooked_spine_material()
flower_mat = create_flower_material()

# Apply materials
fishhook.data.materials.append(fishhook_mat)
flower_center.data.materials.append(flower_mat)

for spine_part in all_spine_parts:
    spine_part.data.materials.append(spine_mat)

for i in range(8):
    petal_obj = bpy.data.objects.get(f"Petal_{i}")
    if petal_obj:
        petal_obj.data.materials.append(flower_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = [fishhook, flower_center] + all_spine_parts + [bpy.data.objects.get(f"Petal_{i}") for i in range(8) if bpy.data.objects.get(f"Petal_{i}")]

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = fishhook
bpy.ops.object.join()
fishhook.name = "FishhookCactus"

# Create ground
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, 0))
ground = bpy.context.active_object

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.70, 0.60, 0.42, 1)
    ground_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

# Camera
bpy.ops.object.camera_add(location=(1.5, -1.5, 0.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(2, -2, 4))
sun = bpy.context.active_object
sun.data.energy = 4.2
sun.rotation_euler = (math.radians(50), math.radians(30), 0)

print("Fishhook Cactus created successfully!")