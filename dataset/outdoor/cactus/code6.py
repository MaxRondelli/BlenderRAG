import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create organ pipe cactus - multiple vertical stems from single base
def create_organ_pipe_stem(name, radius, height, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12,
        radius=radius,
        depth=height,
        location=location
    )
    stem = bpy.context.active_object
    stem.name = name
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=4)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add ridges
    mesh = stem.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    for vert in bm.verts:
        x, y, z = vert.co
        angle = math.atan2(y, x)
        ridge_offset = abs(math.sin(angle * 6)) * 0.06
        vert.co.x *= (1 + ridge_offset)
        vert.co.y *= (1 + ridge_offset)
    
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.shade_smooth()
    
    return stem

# Create multiple stems at different positions and heights
stems = []

# Center stems (tallest)
stem1 = create_organ_pipe_stem("Stem1", 0.22, 3.5, (0, 0, 1.75))
stems.append(stem1)

stem2 = create_organ_pipe_stem("Stem2", 0.2, 3.2, (0.35, 0, 1.6))
stems.append(stem2)

stem3 = create_organ_pipe_stem("Stem3", 0.21, 3.0, (-0.3, 0.15, 1.5))
stems.append(stem3)

# Outer ring of stems
stem4 = create_organ_pipe_stem("Stem4", 0.19, 2.8, (0.5, 0.3, 1.4))
stems.append(stem4)

stem5 = create_organ_pipe_stem("Stem5", 0.2, 2.6, (-0.45, -0.25, 1.3))
stems.append(stem5)

stem6 = create_organ_pipe_stem("Stem6", 0.18, 2.5, (0.25, -0.4, 1.25))
stems.append(stem6)

stem7 = create_organ_pipe_stem("Stem7", 0.19, 2.7, (-0.15, 0.45, 1.35))
stems.append(stem7)

stem8 = create_organ_pipe_stem("Stem8", 0.17, 2.4, (0.6, -0.1, 1.2))
stems.append(stem8)

# Create shared base
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.7,
    depth=0.4,
    location=(0, 0, 0.2)
)
base = bpy.context.active_object
base.name = "Base"
bpy.ops.object.shade_smooth()

def create_spine(location, rotation):
    bpy.ops.mesh.primitive_cone_add(
        vertices=4,
        radius1=0.012,
        radius2=0.0005,
        depth=0.15,
        location=location,
        rotation=rotation
    )
    spine = bpy.context.active_object
    spine.name = "Spine"
    return spine

# Add spines to each stem
all_spines = []

for stem in stems:
    # Number of spine rows based on stem height
    stem_height = stem.dimensions.z
    num_rows = int(stem_height * 4)
    spines_per_row = 12
    
    for row in range(num_rows):
        z_local = -stem_height/2 + (row * stem_height / num_rows)
        z_world = stem.location.z + z_local
        
        for i in range(spines_per_row):
            angle = (i / spines_per_row) * 2 * math.pi
            radius = stem.dimensions.x / 2 + 0.02
            
            x = stem.location.x + math.cos(angle) * radius
            y = stem.location.y + math.sin(angle) * radius
            
            rot_z = angle
            rot_y = math.radians(random.uniform(70, 85))
            
            spine = create_spine((x, y, z_world), (0, rot_y, rot_z))
            all_spines.append(spine)

# Add spines to base
num_base_rows = 3
for row in range(num_base_rows):
    z = 0.05 + (row * 0.3 / num_base_rows)
    for i in range(20):
        angle = (i / 20) * 2 * math.pi
        radius = 0.72
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        
        rot_z = angle
        rot_y = math.radians(random.uniform(70, 85))
        
        spine = create_spine((x, y, z), (0, rot_y, rot_z))
        all_spines.append(spine)

# Create materials
def create_organ_pipe_material():
    mat = bpy.data.materials.new(name="OrganPipeMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    bump = nodes.new('ShaderNodeBump')
    
    noise.inputs['Scale'].default_value = 9.0
    noise.inputs['Detail'].default_value = 7.0
    
    # Light green color
    color_ramp.color_ramp.elements[0].color = (0.25, 0.45, 0.22, 1)
    color_ramp.color_ramp.elements[1].color = (0.35, 0.55, 0.30, 1)
    
    bump.inputs['Strength'].default_value = 0.25
    
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
        bsdf.inputs['Base Color'].default_value = (0.85, 0.80, 0.68, 1)
        bsdf.inputs['Roughness'].default_value = 0.55
    return mat

organ_pipe_mat = create_organ_pipe_material()
spine_mat = create_spine_material()

# Apply materials
for stem in stems + [base]:
    stem.data.materials.append(organ_pipe_mat)

for spine in all_spines:
    spine.data.materials.append(spine_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = stems + [base] + all_spines

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = stem1
bpy.ops.object.join()
stem1.name = "OrganPipeCactus"

# Create ground
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
ground = bpy.context.active_object

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.68, 0.58, 0.40, 1)
    ground_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

# Camera
bpy.ops.object.camera_add(location=(5, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(50), math.radians(30), 0)

print("Organ Pipe Cactus created successfully!")