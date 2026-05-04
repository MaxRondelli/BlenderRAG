import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Function to create cylindrical segment with ridges
def create_cactus_segment(name, radius, height, location, segments=8):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments,
        radius=radius,
        depth=height,
        location=location
    )
    segment = bpy.context.active_object
    segment.name = name
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=3)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    mesh = segment.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    for vert in bm.verts:
        x, y, z = vert.co
        angle = math.atan2(y, x)
        ridge_offset = abs(math.sin(angle * segments / 2)) * 0.08
        vert.co.x *= (1 + ridge_offset)
        vert.co.y *= (1 + ridge_offset)
    
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.shade_smooth()
    return segment

# Create very tall main trunk
main_trunk = create_cactus_segment("MainTrunk", 0.45, 5.5, (0, 0, 2.75), segments=14)

# Create multiple arms at different heights
left_arm_low = create_cactus_segment("LeftArmLow", 0.28, 1.2, (-0.6, 0, 1.5), segments=10)
left_arm_low.rotation_euler = (0, math.radians(75), 0)

left_arm_mid = create_cactus_segment("LeftArmMid", 0.25, 1.8, (-0.9, 0, 2.8), segments=10)
left_arm_mid.rotation_euler = (0, math.radians(-5), 0)

right_arm_low = create_cactus_segment("RightArmLow", 0.3, 1.4, (0.65, 0, 1.8), segments=10)
right_arm_low.rotation_euler = (0, math.radians(-70), 0)

right_arm_high = create_cactus_segment("RightArmHigh", 0.26, 2.0, (1.0, 0, 3), segments=10)
right_arm_high.rotation_euler = (0, math.radians(10), 0)

top_segment = create_cactus_segment("TopSegment", 0.4, 0.9, (0, 0, 5.7), segments=14)

def create_spine(location, rotation):
    bpy.ops.mesh.primitive_cone_add(
        vertices=4,
        radius1=0.018,
        radius2=0.001,
        depth=0.18,
        location=location,
        rotation=rotation
    )
    spine = bpy.context.active_object
    spine.name = "Spine"
    return spine

all_parts = [main_trunk]
num_spine_rows = 18
spines_per_row = 18

for row in range(num_spine_rows):
    z = 0.4 + (row * 5.0 / num_spine_rows)
    for i in range(spines_per_row):
        angle = (i / spines_per_row) * 2 * math.pi
        radius = 0.47
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        rot_z = angle
        rot_y = math.radians(random.uniform(70, 85))
        spine = create_spine((x, y, z), (0, rot_y, rot_z))
        all_parts.append(spine)

for arm in [left_arm_low, left_arm_mid, right_arm_low, right_arm_high]:
    for i in range(20):
        local_z = random.uniform(-0.5, 0.5)
        angle = random.uniform(0, 2 * math.pi)
        radius = 0.3
        local_x = math.cos(angle) * radius
        local_y = math.sin(angle) * radius
        world_pos = arm.matrix_world @ Vector((local_x, local_y, local_z))
        rot_z = angle
        rot_y = math.radians(random.uniform(70, 85))
        spine = create_spine(world_pos, (0, rot_y, rot_z))
        all_parts.append(spine)

def create_cactus_material():
    mat = bpy.data.materials.new(name="CactusMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    bump = nodes.new('ShaderNodeBump')
    
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 6.0
    
    color_ramp.color_ramp.elements[0].color = (0.18, 0.38, 0.16, 1)
    color_ramp.color_ramp.elements[1].color = (0.28, 0.52, 0.22, 1)
    
    bump.inputs['Strength'].default_value = 0.3
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    bsdf.inputs['Roughness'].default_value = 0.7
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_spine_material():
    mat = bpy.data.materials.new(name="SpineMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.88, 0.78, 0.62, 1)
        bsdf.inputs['Roughness'].default_value = 0.6
    return mat

cactus_mat = create_cactus_material()
spine_mat = create_spine_material()

for part in [main_trunk, left_arm_low, left_arm_mid, right_arm_low, right_arm_high, top_segment]:
    part.data.materials.append(cactus_mat)

for part in all_parts:
    if "Spine" in part.name:
        part.data.materials.append(spine_mat)

bpy.ops.object.select_all(action='DESELECT')
for obj in all_parts + [left_arm_low, left_arm_mid, right_arm_low, right_arm_high, top_segment]:
    obj.select_set(True)

bpy.context.view_layer.objects.active = main_trunk
bpy.ops.object.join()
main_trunk.name = "TallSaguaroCactus"

bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.72, 0.62, 0.42, 1)
    ground_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

bpy.ops.object.camera_add(location=(6, -6, 4))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='SUN', location=(6, -6, 12))
sun = bpy.context.active_object
sun.data.energy = 4.2
sun.rotation_euler = (math.radians(50), math.radians(30), 0)

print("Tall Saguaro Cactus created successfully!")