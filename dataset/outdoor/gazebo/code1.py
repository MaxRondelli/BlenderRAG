import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Japanese pagoda gazebo parameters
base_size = 3.5
floor_height = 0.25
post_height = 2.8
post_size = 0.15
roof_layers = 3

# Square platform with slight elevation
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, floor_height/2))
platform = bpy.context.active_object
platform.scale = (base_size, base_size, floor_height)
platform.name = "Platform"

# Stone base steps
for i in range(2):
    step_size = base_size + (2-i) * 0.4
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -i * 0.15 - 0.075))
    step = bpy.context.active_object
    step.scale = (step_size, step_size, 0.15)
    step.name = f"Step_{i+1}"

# Four corner posts (square)
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (base_size/2 - 0.3)
        y = y_side * (base_size/2 - 0.3)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, floor_height + post_height/2))
        post = bpy.context.active_object
        post.scale = (post_size, post_size, post_height)
        post.name = f"Post_{x_side}_{y_side}"

# Horizontal beams connecting posts
z_beam = floor_height + post_height - 0.2
for direction in ['x', 'y']:
    for offset in [-1, 1]:
        if direction == 'x':
            x1, y1 = -(base_size/2 - 0.3), offset * (base_size/2 - 0.3)
            x2, y2 = (base_size/2 - 0.3), offset * (base_size/2 - 0.3)
        else:
            x1, y1 = offset * (base_size/2 - 0.3), -(base_size/2 - 0.3)
            x2, y2 = offset * (base_size/2 - 0.3), (base_size/2 - 0.3)
        
        x_mid, y_mid = (x1 + x2)/2, (y1 + y2)/2
        length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        rotation = math.atan2(y2-y1, x2-x1)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mid, y_mid, z_beam))
        beam = bpy.context.active_object
        beam.scale = (length, 0.12, 0.15)
        beam.rotation_euler[2] = rotation
        beam.name = f"Beam_{direction}_{offset}"

# Multi-tiered roof (typical Japanese style)
z_roof_base = z_beam + 0.1
for i in range(roof_layers):
    roof_size = base_size * (1.2 - i * 0.25)
    roof_thickness = 0.08
    z_layer = z_roof_base +i*0.1
    
    # Main roof layer (square with upturned corners)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_layer))
    roof_layer = bpy.context.active_object
    roof_layer.scale = (roof_size, roof_size, roof_thickness)
    roof_layer.name = f"Roof_Layer_{i+1}"
    
    # Upturned corners (characteristic of Asian architecture)
    for x_side in [-1, 1]:
        for y_side in [-1, 1]:
            x_corner = x_side * roof_size/2
            y_corner = y_side * roof_size/2
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x_corner, y_corner, z_layer + 0.15))
            corner = bpy.context.active_object
            corner.scale = (0.3, 0.3, 0.2)
            corner.rotation_euler[2] = math.pi/4
            corner.name = f"Corner_Upturn_L{i+1}_{x_side}_{y_side}"

# Decorative finial (sorin - Japanese spire ornament)
z_finial = z_roof_base + roof_layers * 0.1 

# Base ring
bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.03, location=(0, 0, z_finial))
finial_ring = bpy.context.active_object
finial_ring.name = "Finial_Ring"

# Central spire with rings
for i in range(5):
    ring_radius = 0.12 - i * 0.02
    z_ring = z_finial + 0.1 + i * 0.15
    
    bpy.ops.mesh.primitive_torus_add(major_radius=ring_radius, minor_radius=0.02, location=(0, 0, z_ring))
    ring = bpy.context.active_object
    ring.name = f"Spire_Ring_{i+1}"

# Top ornament (hoju - sacred jewel)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0, z_finial + 0.85))
jewel = bpy.context.active_object
jewel.scale[2] = 1.3
jewel.name = "Sacred_Jewel"

# Lattice panels between posts (shoji-inspired)
z_lattice = floor_height + post_height/2
for i, (x1, y1, x2, y2) in enumerate([
    (-(base_size/2-0.3), -(base_size/2-0.3), (base_size/2-0.3), -(base_size/2-0.3)),
    ((base_size/2-0.3), -(base_size/2-0.3), (base_size/2-0.3), (base_size/2-0.3)),
    ((base_size/2-0.3), (base_size/2-0.3), -(base_size/2-0.3), (base_size/2-0.3)),
    (-(base_size/2-0.3), (base_size/2-0.3), -(base_size/2-0.3), -(base_size/2-0.3))
]):
    x_mid, y_mid = (x1+x2)/2, (y1+y2)/2
    length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    rotation = math.atan2(y2-y1, x2-x1)
    
    # Horizontal lattice bars
    for j in range(4):
        z_bar = floor_height + 0.5 + j * 0.5
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mid, y_mid, z_bar))
        bar = bpy.context.active_object
        bar.scale = (length, 0.03, 0.03)
        bar.rotation_euler[2] = rotation
        bar.name = f"Lattice_H_{i}_{j}"

# Materials
mat_wood = bpy.data.materials.new(name="Dark_Wood")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.2, 0.15, 0.1, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

mat_roof = bpy.data.materials.new(name="Clay_Tiles")
mat_roof.use_nodes = True
nodes = mat_roof.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.3, 0.25, 0.2, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

mat_gold = bpy.data.materials.new(name="Gold_Finial")
mat_gold.use_nodes = True
nodes = mat_gold.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.85, 0.7, 0.2, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.2

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Roof' in obj.name or 'Corner' in obj.name:
            obj.data.materials.append(mat_roof)
        elif 'Finial' in obj.name or 'Spire' in obj.name or 'Jewel' in obj.name:
            obj.data.materials.append(mat_gold)
        else:
            obj.data.materials.append(mat_wood)

print("Japanese pagoda gazebo created!")
