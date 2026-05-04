import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_pad(name, size, location, rotation=(0, 0, 0)):
    # Create flattened sphere for pad
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=size,
        location=location,
        segments=16,
        ring_count=12
    )
    pad = bpy.context.active_object
    pad.name = name
    pad.scale = (1, 0.3, 1)
    pad.rotation_euler = rotation
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=1)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    
    return pad

# Create prickly pear pads at different heights and angles
pad1 = create_pad("Pad1", 0.5, (0, 0, 0.5), (0, 0, 0))
pad2 = create_pad("Pad2", 0.45, (0.4, 0, 1.0), (0, math.radians(15), math.radians(20)))
pad3 = create_pad("Pad3", 0.42, (0.7, -0.15, 1.5), (0, math.radians(-10), math.radians(35)))
pad4 = create_pad("Pad4", 0.48, (-0.35, 0.1, 1.05), (0, math.radians(20), math.radians(-25)))
pad5 = create_pad("Pad5", 0.4, (-0.6, 0, 1.6), (0, math.radians(10), math.radians(-15)))
pad6 = create_pad("Pad6", 0.38, (0.2, 0.12, 1.85), (0, math.radians(-5), math.radians(10)))

all_pads = [pad1, pad2, pad3, pad4, pad5, pad6]

def create_spine_cluster(location, normal):
    spines = []
    # Create small cluster of spines
    for i in range(3):
        offset_x = random.uniform(-0.03, 0.03)
        offset_y = random.uniform(-0.03, 0.03)
        
        spine_loc = (
            location[0] + offset_x,
            location[1] + offset_y,
            location[2]
        )
        
        bpy.ops.mesh.primitive_cone_add(
            vertices=3,
            radius1=0.008,
            radius2=0.0005,
            depth=0.12,
            location=spine_loc
        )
        spine = bpy.context.active_object
        spine.name = "Spine"
        
        # Random slight rotation
        spine.rotation_euler = (
            random.uniform(-0.3, 0.3),
            random.uniform(-0.3, 0.3),
            random.uniform(0, math.pi * 2)
        )
        
        spines.append(spine)
    
    return spines

# Add spine clusters to each pad
all_spines = []

for pad in all_pads:
    # Get some random points on the pad surface
    num_clusters = 12
    
    for i in range(num_clusters):
        # Random spherical coordinates
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        
        # Convert to cartesian on sphere surface
        r = 0.5 * pad.scale[0]
        local_x = r * math.sin(phi) * math.cos(theta)
        local_y = r * math.sin(phi) * math.sin(theta) * pad.scale[1]
        local_z = r * math.cos(phi) * pad.scale[2]
        
        # Transform to world space
        world_pos = pad.matrix_world @ Vector((local_x, local_y, local_z))
        
        cluster_spines = create_spine_cluster(world_pos, (local_x, local_y, local_z))
        all_spines.extend(cluster_spines)

# Create small fruits on some pads
fruit_objects = []
for i in range(4):
    fruit_pad = random.choice([pad2, pad3, pad4, pad6])
    
    angle = random.uniform(0, 2 * math.pi)
    fruit_x = math.cos(angle) * 0.35
    fruit_z = math.sin(angle) * 0.35
    
    world_pos = fruit_pad.matrix_world @ Vector((fruit_x, 0.15, fruit_z))
    
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.08,
        location=world_pos,
        segments=8,
        ring_count=6
    )
    fruit = bpy.context.active_object
    fruit.name = f"Fruit_{i}"
    fruit.scale = (1, 0.8, 1)
    fruit_objects.append(fruit)

# Create materials
def create_pad_material():
    mat = bpy.data.materials.new(name="PadMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 12.0
    
    color_ramp.color_ramp.elements[0].color = (0.22, 0.42, 0.20, 1)
    color_ramp.color_ramp.elements[1].color = (0.32, 0.55, 0.28, 1)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.7
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_fruit_material():
    mat = bpy.data.materials.new(name="FruitMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.15, 0.25, 1)
        bsdf.inputs['Roughness'].default_value = 0.3
    return mat

def create_spine_material():
    mat = bpy.data.materials.new(name="SpineMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.92, 0.88, 0.75, 1)
        bsdf.inputs['Roughness'].default_value = 0.5
    return mat

pad_mat = create_pad_material()
fruit_mat = create_fruit_material()
spine_mat = create_spine_material()

for pad in all_pads:
    pad.data.materials.append(pad_mat)

for spine in all_spines:
    spine.data.materials.append(spine_mat)

for fruit in fruit_objects:
    fruit.data.materials.append(fruit_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = all_pads + all_spines + fruit_objects

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = pad1
bpy.ops.object.join()
pad1.name = "PricklyPearCactus"

bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
ground = bpy.context.active_object

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.70, 0.60, 0.42, 1)
    ground_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

bpy.ops.object.camera_add(location=(3, -3, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='SUN', location=(4, -4, 8))
sun = bpy.context.active_object
sun.data.energy = 4.3
sun.rotation_euler = (math.radians(50), math.radians(30), 0)

print("Prickly Pear Cactus created successfully!")