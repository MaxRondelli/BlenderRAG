import bpy
import bmesh
import random
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create barrel cactus - short and wide
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.8,
    depth=1.5,
    location=(0, 0, 0.75)
)
barrel = bpy.context.active_object
barrel.name = "BarrelCactus"

# Taper the top
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=4)
bpy.ops.object.mode_set(mode='OBJECT')

mesh = barrel.data
bm = bmesh.new()
bm.from_mesh(mesh)

for vert in bm.verts:
    x, y, z = vert.co
    angle = math.atan2(y, x)
    
    # Create deep ridges
    ridge_offset = abs(math.sin(angle * 8)) * 0.15
    
    # Taper toward top
    if z > 0.3:
        taper = 1 - ((z - 0.3) / 0.45) * 0.25
        vert.co.x *= taper
        vert.co.y *= taper
    
    # Apply ridges
    vert.co.x *= (1 + ridge_offset)
    vert.co.y *= (1 + ridge_offset)

bm.to_mesh(mesh)
bm.free()
bpy.ops.object.shade_smooth()

# Create flower on top
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0, 0, 1.6), segments=16, ring_count=8)
flower_center = bpy.context.active_object
flower_center.name = "FlowerCenter"
flower_center.scale = (1, 1, 0.5)

# Create petals
for i in range(8):
    angle = (i / 8) * 2 * math.pi
    x = math.cos(angle) * 0.3
    y = math.sin(angle) * 0.3
    
    bpy.ops.mesh.primitive_cube_add(location=(x, y, 1.65))
    petal = bpy.context.active_object
    petal.name = f"Petal_{i}"
    petal.scale = (0.15, 0.08, 0.05)
    petal.rotation_euler = (0, 0, angle)

def create_spine(location, rotation):
    bpy.ops.mesh.primitive_cone_add(
        vertices=4,
        radius1=0.02,
        radius2=0.001,
        depth=0.25,
        location=location,
        rotation=rotation
    )
    spine = bpy.context.active_object
    spine.name = "Spine"
    return spine

# Add dense spines in rows following ridges
all_parts = [barrel, flower_center]
num_ridges = 16
num_rows = 10

for ridge in range(num_ridges):
    angle_base = (ridge / num_ridges) * 2 * math.pi
    
    for row in range(num_rows):
        z = 0.2 + (row * 1.2 / num_rows)
        
        # Calculate position on ridge
        ridge_radius = 0.8 + abs(math.sin(angle_base * 8)) * 0.12
        x = math.cos(angle_base) * ridge_radius
        y = math.sin(angle_base) * ridge_radius
        
        rot_z = angle_base
        rot_y = math.radians(random.uniform(75, 90))
        
        spine = create_spine((x, y, z), (0, rot_y, rot_z))
        all_parts.append(spine)

# Create materials
def create_barrel_material():
    mat = bpy.data.materials.new(name="BarrelCactusMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    noise = nodes.new('ShaderNodeTexNoise')
    color_ramp = nodes.new('ShaderNodeValToRGB')
    
    noise.inputs['Scale'].default_value = 10.0
    
    # Blue-green barrel cactus color
    color_ramp.color_ramp.elements[0].color = (0.12, 0.32, 0.22, 1)
    color_ramp.color_ramp.elements[1].color = (0.20, 0.45, 0.28, 1)
    
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.75
    
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat

def create_flower_material():
    mat = bpy.data.materials.new(name="FlowerMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.25, 0.35, 1)
        bsdf.inputs['Roughness'].default_value = 0.4
    return mat

def create_spine_material():
    mat = bpy.data.materials.new(name="SpineMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.90, 0.82, 0.65, 1)
        bsdf.inputs['Roughness'].default_value = 0.5
    return mat

barrel_mat = create_barrel_material()
flower_mat = create_flower_material()
spine_mat = create_spine_material()

barrel.data.materials.append(barrel_mat)
flower_center.data.materials.append(flower_mat)

for i in range(8):
    petal_obj = bpy.data.objects.get(f"Petal_{i}")
    if petal_obj:
        petal_obj.data.materials.append(flower_mat)
        all_parts.append(petal_obj)

for part in all_parts:
    if "Spine" in part.name:
        part.data.materials.append(spine_mat)

bpy.ops.object.select_all(action='DESELECT')
for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = barrel
bpy.ops.object.join()
barrel.name = "BarrelCactus"

bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
ground = bpy.context.active_object

ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.68, 0.58, 0.40, 1)
    ground_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(65), 0, math.radians(45))
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='SUN', location=(4, -4, 8))
sun = bpy.context.active_object
sun.data.energy = 4.5
sun.rotation_euler = (math.radians(45), math.radians(25), 0)

print("Barrel Cactus created successfully!")