import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Simple steel gazebo parameters
diameter = 3.0
num_posts = 4
floor_height = 0.2
post_height = 2.4
post_size = 0.08

# Square concrete platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, floor_height/2))
platform = bpy.context.active_object
platform.scale = (diameter, diameter, floor_height)
platform.name = "Concrete_Platform"

# Four corner steel posts
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (diameter/2 - post_size)
        y = y_side * (diameter/2 - post_size)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, floor_height + post_height/2))
        post = bpy.context.active_object
        post.scale = (post_size, post_size, post_height)
        post.name = f"Steel_Post_{x_side}_{y_side}"

# Simple horizontal beams
z_beam = floor_height + post_height

# Four perimeter beams
for direction in ['x', 'y']:
    for offset in [-1, 1]:
        if direction == 'x':
            x, y = 0, offset * (diameter/2 - post_size)
            scale = (diameter - 2*post_size, post_size, post_size)
        else:
            x, y = offset * (diameter/2 - post_size), 0
            scale = (post_size, diameter - 2*post_size, post_size)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_beam))
        beam = bpy.context.active_object
        beam.scale = scale
        beam.name = f"Beam_{direction}_{offset}"

# Flat roof
roof_thickness = 0.06
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_beam + post_size/2 + roof_thickness/2))
roof = bpy.context.active_object
roof.scale = (diameter + 0.2, diameter + 0.2, roof_thickness)
roof.name = "Metal_Roof"

# Simple cable railings (horizontal wires)
z_rail_1 = floor_height + 0.5
z_rail_2 = floor_height + 1.0

for side in ['north', 'south', 'east', 'west']:
    if side == 'north':
        x1, y1 = -(diameter/2-post_size), (diameter/2-post_size)
        x2, y2 = (diameter/2-post_size), (diameter/2-post_size)
    elif side == 'south':
        x1, y1 = (diameter/2-post_size), -(diameter/2-post_size)
        x2, y2 = -(diameter/2-post_size), -(diameter/2-post_size)
    elif side == 'east':
        x1, y1 = (diameter/2-post_size), (diameter/2-post_size)
        x2, y2 = (diameter/2-post_size), -(diameter/2-post_size)
    else:  # west
        x1, y1 = -(diameter/2-post_size), -(diameter/2-post_size)
        x2, y2 = -(diameter/2-post_size), (diameter/2-post_size)
    
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2
    length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    rotation = math.atan2(y2-y1, x2-x1)
    
    for z_rail in [z_rail_1, z_rail_2]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=length, location=(x_mid, y_mid, z_rail))
        cable = bpy.context.active_object
        cable.rotation_euler[1] = math.pi/2
        cable.rotation_euler[0] = rotation
        cable.name = f"Cable_{side}_{z_rail}"

# Simple bench on one side
bench_width = diameter - 0.8
bench_depth = 0.4
bench_height = 0.45
bench_y = diameter/2 - bench_depth/2 - 0.3

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, bench_y, floor_height + bench_height/2))
bench = bpy.context.active_object
bench.scale = (bench_width, bench_depth, bench_height)
bench.name = "Wood_Bench"

# Materials
mat_steel = bpy.data.materials.new(name="Steel_Gray")
mat_steel.use_nodes = True
nodes = mat_steel.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.62, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.3

mat_concrete = bpy.data.materials.new(name="Concrete_Gray")
mat_concrete.use_nodes = True
nodes = mat_concrete.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.55, 0.55, 0.55, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

mat_wood = bpy.data.materials.new(name="Natural_Wood")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.5, 0.4, 0.3, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Platform' in obj.name:
            obj.data.materials.append(mat_concrete)
        elif 'Bench' in obj.name:
            obj.data.materials.append(mat_wood)
        else:
            obj.data.materials.append(mat_steel)

print("Simple steel gazebo created!")
