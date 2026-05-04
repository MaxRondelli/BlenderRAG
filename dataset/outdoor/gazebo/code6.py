import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Simple canvas canopy gazebo parameters
base_size = 3.0
floor_height = 0.15
post_height = 2.5
post_radius = 0.06

# Wooden platform (square)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, floor_height/2))
platform = bpy.context.active_object
platform.scale = (base_size, base_size, floor_height)
platform.name = "Wood_Platform"

# Four corner poles (metal pipes)
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (base_size/2 - 0.2)
        y = y_side * (base_size/2 - 0.2)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=post_radius, depth=post_height, location=(x, y, floor_height + post_height/2))
        pole = bpy.context.active_object
        pole.name = f"Metal_Pole_{x_side}_{y_side}"

# Simple canvas canopy (draped fabric)
z_canopy = floor_height + post_height - 0.2
canopy_droop = 0.4

# Center of canopy (droops down)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_canopy - canopy_droop/2))
canopy_center = bpy.context.active_object
canopy_center.scale = (base_size - 0.5, base_size - 0.5, 0.02)
canopy_center.name = "Canvas_Center"

# Four triangular sections from center to corners (fabric drape)
for i, (x_side, y_side) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
    x_corner = x_side * (base_size/2)
    y_corner = y_side * (base_size/2)
    
    # Create draped section
    x_mid = x_corner / 2
    y_mid = y_corner / 2
    z_mid = z_canopy - canopy_droop/4
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mid, y_mid, z_mid))
    drape = bpy.context.active_object
    length = math.sqrt((base_size/2)**2 + (base_size/2)**2)
    drape.scale = (length/1.5, length/1.5, 0.02)
    drape.rotation_euler[2] = math.atan2(y_corner, x_corner)
    drape.name = f"Canvas_Drape_{i+1}"

# Decorative ropes/ties at corners
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (base_size/2 - 0.1)
        y = y_side * (base_size/2 - 0.1)
        
        # Rope from pole top to canopy edge
        bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.3, location=(x, y, z_canopy + 0.15))
        rope = bpy.context.active_object
        rope.name = f"Tie_Rope_{x_side}_{y_side}"

# Simple floor cushions
cushion_radius = 0.35
cushion_height = 0.1

for i, (x, y) in enumerate([(0.6, 0.6), (-0.6, 0.6), (0.6, -0.6), (-0.6, -0.6)]):
    bpy.ops.mesh.primitive_cylinder_add(radius=cushion_radius, depth=cushion_height, location=(x, y, floor_height + cushion_height/2))
    cushion = bpy.context.active_object
    cushion.name = f"Floor_Cushion_{i+1}"

# Low central table
table_radius = 0.4
table_height = 0.3

bpy.ops.mesh.primitive_cylinder_add(radius=table_radius, depth=0.04, location=(0, 0, floor_height + table_height))
table_top = bpy.context.active_object
table_top.name = "Table_Top"

# Three simple legs
for i in range(3):
    angle = (2 * math.pi / 3) * i
    x_leg = math.cos(angle) * (table_radius - 0.1)
    y_leg = math.sin(angle) * (table_radius - 0.1)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=table_height, location=(x_leg, y_leg, floor_height + table_height/2))
    leg = bpy.context.active_object
    leg.name = f"Table_Leg_{i+1}"

# Materials
mat_canvas = bpy.data.materials.new(name="White_Canvas")
mat_canvas.use_nodes = True
nodes = mat_canvas.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.95, 0.93, 0.88, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9

mat_metal = bpy.data.materials.new(name="Black_Metal")
mat_metal.use_nodes = True
nodes = mat_metal.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.4

mat_wood = bpy.data.materials.new(name="Light_Wood")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.7, 0.6, 0.45, 1.0)
bsdf.inputs['Roughness'].default_value = 0.75

mat_cushion = bpy.data.materials.new(name="Blue_Cushion")
mat_cushion.use_nodes = True
nodes = mat_cushion.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.2, 0.4, 0.6, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Canvas' in obj.name:
            obj.data.materials.append(mat_canvas)
        elif 'Pole' in obj.name or 'Rope' in obj.name or 'Table_Leg' in obj.name:
            obj.data.materials.append(mat_metal)
        elif 'Cushion' in obj.name:
            obj.data.materials.append(mat_cushion)
        else:
            obj.data.materials.append(mat_wood)

print("Simple canvas canopy gazebo created!")
