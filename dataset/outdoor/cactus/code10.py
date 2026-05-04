import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create Moon Cactus (grafted cactus) - colorful ball on green stem
def create_stem_segment(name, radius, height, location):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=radius,
        depth=height,
        location=location
    )
    segment = bpy.context.active_object
    segment.name = name
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add subtle ridges
    mesh = segment.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    for vert in bm.verts:
        x, y, z = vert.co
        angle = math.atan2(y, x)
        ridge_offset = abs(math.sin(angle * 4)) * 0.05
        vert.co.x *= (1 + ridge_offset)
        vert.co.y *= (1 + ridge_offset)
    
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.shade_smooth()
    
    return segment

# Create green base stem (rootstock - usually Hylocereus)
base_stem = create_stem_segment("BaseStem", 0.15, 0.6, (0, 0, 0.3))

# Create colorful top ball (scion - Gymnocalycium mihanovichii)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.25,
    location=(0, 0, 0.75),
    segments=16,
    ring_count=12
)
moon_ball = bpy.context.active_object
moon_ball.name = "MoonBall"
moon_ball.scale = (1, 1, 0.85)  # Slightly flattened

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=2)
bpy.ops.object.mode_set(mode='OBJECT')

# Add ribs to moon ball
mesh = moon_ball.data
bm = bmesh.new()
bm.from_mesh(mesh)

num_ribs = 8

for vert in bm.verts:
    x, y, z = vert.co
    
    # Skip extreme top/bottom
    if abs(z) > 0.18:
        continue
    
    angle = math.atan2(y, x)
    
    # Create ribs
    rib_pattern = abs(math.sin(angle * num_ribs / 2))
    ridge_depth = rib_pattern * 0.08
    
    factor = 1 - ridge_depth + (rib_pattern * 0.1)
    vert.co.x *= factor
    vert.co.y *= factor

bm.to_mesh(mesh)
bm.free()
bpy.ops.object.shade_smooth()

# Create graft union (visible connection point)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.16,
    depth=0.08,
    location=(0, 0, 0.6)
)
graft_union = bpy.context.active_object
graft_union.name = "GraftUnion"
bpy.ops.object.shade_smooth()

# Add minimal spines to base stem only
all_spines = []

def create_tiny_spine(location, rotation):
    bpy.ops.mesh.primitive_cone_add(
        vertices=3,
        radius1=0.004,
        radius2=0.0003,
        depth=0.06,
        location=location,
        rotation=rotation
    )
    spine = bpy.context.active_object
    spine.name = "Spine"
    return spine

# Add spines only to base stem
num_rows = 4
spines_per_row = 8

for row in range(num_rows):
    z = 0.1 + (row * 0.4 / num_rows)
    
    for i in range(spines_per_row):
        angle = (i / spines_per_row) * 2 * math.pi
        radius = 0.16
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        
        rot_z = angle
        rot_y = math.radians(random.uniform(70, 85))
        
        spine = create_tiny_spine((x, y, z), (0, rot_y, rot_z))
        all_spines.append(spine)

# Create materials
def create_base_stem_material():
    mat = bpy.data.materials.new(name="BaseStemMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 10.0
    
    # Dark green base
    color_ramp.color_ramp.elements[0].color = (0.15, 0.30, 0.18, 1)
    color_ramp.color_ramp.elements[1].color = (0.22, 0.40, 0.24, 1)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.65
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_moon_ball_material():
    mat = bpy.data.materials.new(name="MoonBallMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 8.0
    
    # Bright red/pink/orange (can be customized)
    # Using red variant here
    color_ramp.color_ramp.elements[0].color = (0.85, 0.12, 0.25, 1)
    color_ramp.color_ramp.elements[1].color = (0.95, 0.25, 0.35, 1)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.5
    
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_graft_material():
    mat = bpy.data.materials.new(name="GraftMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Brown/tan graft union
        bsdf.inputs['Base Color'].default_value = (0.55, 0.45, 0.35, 1)
        bsdf.inputs['Roughness'].default_value = 0.8
    return mat

def create_spine_material():
    mat = bpy.data.materials.new(name="SpineMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.75, 0.70, 0.60, 1)
        bsdf.inputs['Roughness'].default_value = 0.6
    return mat

base_mat = create_base_stem_material()
moon_mat = create_moon_ball_material()
graft_mat = create_graft_material()
spine_mat = create_spine_material()

# Apply materials
base_stem.data.materials.append(base_mat)
moon_ball.data.materials.append(moon_mat)
graft_union.data.materials.append(graft_mat)

for spine in all_spines:
    spine.data.materials.append(spine_mat)

# Create small pot
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.22,
    depth=0.15,
    location=(0, 0, 0.075)
)
pot = bpy.context.active_object
pot.name = "Pot"
pot.scale = (1, 1, 1.2)

# Pot material
pot_mat = bpy.data.materials.new(name="PotMaterial")
pot_mat.use_nodes = True
pot_nodes = pot_mat.node_tree.nodes
pot_bsdf = pot_nodes.get("Principled BSDF")
if pot_bsdf:
    # Terracotta pot
    pot_bsdf.inputs['Base Color'].default_value = (0.65, 0.35, 0.25, 1)
    pot_bsdf.inputs['Roughness'].default_value = 0.85
pot.data.materials.append(pot_mat)

# Join cactus parts (not pot)
bpy.ops.object.select_all(action='DESELECT')
cactus_parts = [base_stem, moon_ball, graft_union] + all_spines

for obj in cactus_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = base_stem
bpy.ops.object.join()
base_stem.name = "MoonCactus"

# Create simple table/surface
bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, -0.05))
table = bpy.context.active_object
table.name = "Table"
table.scale = (1, 1, 0.05)

table_mat = bpy.data.materials.new(name="TableMaterial")
table_mat.use_nodes = True
table_nodes = table_mat.node_tree.nodes
table_bsdf = table_nodes.get("Principled BSDF")
if table_bsdf:
    table_bsdf.inputs['Base Color'].default_value = (0.75, 0.68, 0.60, 1)
    table_bsdf.inputs['Roughness'].default_value = 0.4
table.data.materials.append(table_mat)

# Camera
bpy.ops.object.camera_add(location=(1.2, -1.2, 0.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting - indoor style
bpy.ops.object.light_add(type='AREA', location=(1, -1, 2))
area_light = bpy.context.active_object
area_light.data.energy = 150
area_light.data.size = 1.0
area_light.rotation_euler = (math.radians(45), 0, math.radians(45))

# Add fill light
bpy.ops.object.light_add(type='AREA', location=(-0.8, 0.8, 1.5))
fill_light = bpy.context.active_object
fill_light.data.energy = 80
fill_light.data.size = 0.8
fill_light.rotation_euler = (math.radians(60), 0, math.radians(-135))

print("Moon Cactus created successfully!")