import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create Bishop's Cap Cactus (Astrophytum) - star-shaped when viewed from top
bpy.ops.mesh.primitive_cylinder_add(
    vertices=5,  # Pentagon shape - 5 ribs
    radius=0.5,
    depth=0.9,
    location=(0, 0, 0.45)
)
bishops_cap = bpy.context.active_object
bishops_cap.name = "BishopsCapBody"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=4)
bpy.ops.object.mode_set(mode='OBJECT')

# Create star shape with prominent ribs
mesh = bishops_cap.data
bm = bmesh.new()
bm.from_mesh(mesh)

for vert in bm.verts:
    x, y, z = vert.co
    angle = math.atan2(y, x)
    
    # Create very prominent ribs (star pattern)
    rib_pattern = abs(math.sin(angle * 2.5))  # 5 ribs
    ridge_height = rib_pattern ** 2 * 0.25
    
    # Make ribs more pronounced
    factor = 1 + ridge_height
    vert.co.x *= factor
    vert.co.y *= factor
    
    # Round the top
    if z > 0.2:
        taper = 1 - ((z - 0.2) / 0.25) * 0.3
        vert.co.x *= taper
        vert.co.y *= taper

bm.to_mesh(mesh)
bm.free()
bpy.ops.object.shade_smooth()

# Add white woolly scales (characteristic white dots)
def create_wool_scale(location):
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1,
        radius=0.02,
        location=location
    )
    scale = bpy.context.active_object
    scale.name = "WoolScale"
    return scale

# Add scattered white scales across surface
wool_scales = []
num_scale_rows = 12
scales_per_row = 15

for row in range(num_scale_rows):
    z = 0.1 + (row * 0.7 / num_scale_rows)
    
    for i in range(scales_per_row):
        angle = (i / scales_per_row) * 2 * math.pi + random.uniform(-0.2, 0.2)
        
        # Position on ribs
        rib_offset = abs(math.sin(angle * 2.5)) * 0.15
        radius = 0.5 + rib_offset + random.uniform(-0.05, 0.05)
        
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        
        scale = create_wool_scale((x, y, z))
        wool_scales.append(scale)

# Create large yellow flower on top
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.2,
    location=(0, 0, 0.95),
    segments=12,
    ring_count=8
)
flower_center = bpy.context.active_object
flower_center.name = "FlowerCenter"
flower_center.scale = (1, 1, 0.4)

# Create yellow petals
for i in range(10):
    angle = (i / 10) * 2 * math.pi
    x = math.cos(angle) * 0.28
    y = math.sin(angle) * 0.28
    
    bpy.ops.mesh.primitive_cube_add(location=(x, y, 0.97))
    petal = bpy.context.active_object
    petal.name = f"Petal_{i}"
    petal.scale = (0.15, 0.08, 0.03)
    petal.rotation_euler = (0, 0, angle)

# Create materials
def create_bishops_cap_material():
    mat = bpy.data.materials.new(name="BishopsCapMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 10.0
    
    # Bluish-green with slight gray tint
    color_ramp.color_ramp.elements[0].color = (0.25, 0.35, 0.30, 1)
    color_ramp.color_ramp.elements[1].color = (0.35, 0.45, 0.38, 1)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.7
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_wool_material():
    mat = bpy.data.materials.new(name="WoolMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # White woolly scales
        bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.92, 1)
        bsdf.inputs['Roughness'].default_value = 0.95
    return mat

def create_yellow_flower_material():
    mat = bpy.data.materials.new(name="YellowFlowerMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        # Bright yellow flower
        bsdf.inputs['Base Color'].default_value = (0.95, 0.85, 0.20, 1)
        bsdf.inputs['Roughness'].default_value = 0.3
    return mat

bishops_mat = create_bishops_cap_material()
wool_mat = create_wool_material()
flower_mat = create_yellow_flower_material()

# Apply materials
bishops_cap.data.materials.append(bishops_mat)
flower_center.data.materials.append(flower_mat)

for scale in wool_scales:
    scale.data.materials.append(wool_mat)

for i in range(10):
    petal_obj = bpy.data.objects.get(f"Petal_{i}")
    if petal_obj:
        petal_obj.data.materials.append(flower_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = [bishops_cap, flower_center] + wool_scales + [bpy.data.objects.get(f"Petal_{i}") for i in range(10) if bpy.data.objects.get(f"Petal_{i}")]

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = bishops_cap
bpy.ops.object.join()
bishops_cap.name = "BishopsCapCactus"

# Create ground
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
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
bpy.ops.object.camera_add(location=(2, -2, 1.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(45))
bpy.context.scene.camera = camera

# Lighting
bpy.ops.object.light_add(type='SUN', location=(3, -3, 6))
sun = bpy.context.active_object
sun.data.energy = 4.3
sun.rotation_euler = (math.radians(50), math.radians(30), 0)

print("Bishop's Cap Cactus created successfully!")