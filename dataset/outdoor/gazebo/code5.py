import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Simple wooden pergola parameters
length = 3.5
width = 2.5
floor_height = 0.15
post_height = 2.3
post_size = 0.12

# Wooden deck platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, floor_height/2))
deck = bpy.context.active_object
deck.scale = (length, width, floor_height)
deck.name = "Wood_Deck"

# Four corner posts
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (length/2 - post_size/2)
        y = y_side * (width/2 - post_size/2)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, floor_height + post_height/2))
        post = bpy.context.active_object
        post.scale = (post_size, post_size, post_height)
        post.name = f"Wood_Post_{x_side}_{y_side}"

# Horizontal beams
z_beam = floor_height + post_height

# Main beams along length
for y_side in [-1, 1]:
    y = y_side * (width/2 - post_size/2)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, z_beam))
    beam = bpy.context.active_object
    beam.scale = (length, post_size, post_size * 0.8)
    beam.name = f"Main_Beam_Y_{y_side}"

# Cross beams
num_cross = 6
for i in range(num_cross):
    x = -length/2 + (i + 1) * (length / (num_cross + 1))
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, z_beam + post_size/2))
    cross_beam = bpy.context.active_object
    cross_beam.scale = (post_size * 0.7, width, post_size * 0.7)
    cross_beam.name = f"Cross_Beam_{i+1}"

# Simple bench
bench_width = length - 0.6
bench_depth = 0.35
bench_height = 0.4

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -width/2 + 0.3, floor_height + bench_height/2))
bench_seat = bpy.context.active_object
bench_seat.scale = (bench_width, bench_depth, bench_height)
bench_seat.name = "Bench_Seat"

# Backrest
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -width/2 + 0.15, floor_height + bench_height + 0.25))
backrest = bpy.context.active_object
backrest.scale = (bench_width, 0.06, 0.5)
backrest.name = "Bench_Backrest"

# Simple planter boxes at corners
planter_size = 0.3
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (length/2 + 0.25)
        y = y_side * (width/2 + 0.25)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, floor_height + planter_size/2))
        planter = bpy.context.active_object
        planter.scale = (planter_size, planter_size, planter_size)
        planter.name = f"Planter_Box_{x_side}_{y_side}"

# Materials
mat_wood = bpy.data.materials.new(name="Cedar_Wood")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.6, 0.45, 0.3, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

mat_planter = bpy.data.materials.new(name="Terracotta_Pot")
mat_planter.use_nodes = True
nodes = mat_planter.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.7, 0.4, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Planter' in obj.name:
            obj.data.materials.append(mat_planter)
        else:
            obj.data.materials.append(mat_wood)

print("Simple wooden pergola created!")
