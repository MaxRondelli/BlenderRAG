import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Simple garden arbor parameters
width = 2.5
depth = 2.0
floor_height = 0.12
post_height = 2.2
lattice_spacing = 0.2

# Brick paver base
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, floor_height/2))
base = bpy.context.active_object
base.scale = (width, depth, floor_height)
base.name = "Brick_Base"

# Four wooden posts
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (width/2 - 0.08)
        y = y_side * (depth/2 - 0.08)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, floor_height + post_height/2))
        post = bpy.context.active_object
        post.scale = (0.1, 0.1, post_height)
        post.name = f"Wood_Post_{x_side}_{y_side}"

# Simple lattice panels on back and sides
z_lattice_mid = floor_height + post_height/2

# Back panel


# Simple flat roof with overhang
z_roof = floor_height + post_height
roof_thickness = 0.08

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_roof + roof_thickness/2))
roof = bpy.context.active_object
roof.scale = (width + 0.3, depth + 0.3, roof_thickness)
roof.name = "Wood_Roof"

# Hanging plant hooks
for x_side in [-1, 1]:
    x_hook = x_side * (width/2 - 0.3)
    
    # Hook arm
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.15, location=(x_hook, 0, floor_height))
    hook = bpy.context.active_object
    hook.name = f"Plant_Hook_{x_side}"
    
    # Hanging basket
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.2, location=(x_hook, 0, floor_height))
    basket = bpy.context.active_object
    basket.scale[2] = 0.8
    basket.name = f"Hanging_Basket_{x_side}"
    
    # Simple plant
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(x_hook, 0, floor_height))
    plant = bpy.context.active_object
    plant.scale[2] = 0.7
    plant.name = f"Hanging_Plant_{x_side}"

# Simple bench
bench_width = width - 0.6
bench_depth = 0.35
bench_height = 0.42

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, depth/2 - 0.3, floor_height + bench_height/2))
bench = bpy.context.active_object
bench.scale = (bench_width, bench_depth, bench_height)
bench.name = "Garden_Bench"

# Materials
mat_wood = bpy.data.materials.new(name="White_Painted_Wood")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.92, 1.0)
bsdf.inputs['Roughness'].default_value = 0.6

mat_brick = bpy.data.materials.new(name="Red_Brick")
mat_brick.use_nodes = True
nodes = mat_brick.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.6, 0.3, 0.2, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9

mat_basket = bpy.data.materials.new(name="Wicker_Basket")
mat_basket.use_nodes = True
nodes = mat_basket.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.55, 0.4, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

mat_plant = bpy.data.materials.new(name="Green_Foliage")
mat_plant.use_nodes = True
nodes = mat_plant.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.2, 0.5, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Base' in obj.name or 'Brick' in obj.name:
            obj.data.materials.append(mat_brick)
        elif 'Basket' in obj.name:
            obj.data.materials.append(mat_basket)
        elif 'Plant' in obj.name:
            obj.data.materials.append(mat_plant)
        else:
            obj.data.materials.append(mat_wood)

print("Simple garden arbor created!")
