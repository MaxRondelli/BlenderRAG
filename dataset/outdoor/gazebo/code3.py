import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Mediterranean pergola parameters
length = 4.0
width = 3.0
floor_height = 0.2
column_height = 2.5
column_size = 0.25
beam_spacing = 0.4

# Terracotta tile floor
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, floor_height/2))
floor = bpy.context.active_object
floor.scale = (length, width, floor_height)
floor.name = "Tile_Floor"

# Four stucco columns with classical proportions
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (length/2 - column_size/2)
        y = y_side * (width/2 - column_size/2)
        
        # Column shaft
        bpy.ops.mesh.primitive_cylinder_add(radius=column_size/2, depth=column_height, location=(x, y, floor_height + column_height/2))
        column = bpy.context.active_object
        column.name = f"Column_{x_side}_{y_side}"
        
        # Column base (larger)
        bpy.ops.mesh.primitive_cylinder_add(radius=column_size/1.5, depth=0.2, location=(x, y, floor_height + 0.1))
        base = bpy.context.active_object
        base.name = f"Column_Base_{x_side}_{y_side}"
        
        # Capital (flared top)
        bpy.ops.mesh.primitive_cylinder_add(radius=column_size/1.4, depth=0.25, location=(x, y, floor_height + column_height - 0.125))
        capital = bpy.context.active_object
        capital.scale[2] = 0.8
        capital.name = f"Capital_{x_side}_{y_side}"

# Main beams connecting columns
z_beam = floor_height + column_height

# Longitudinal beams (along length)
for y_side in [-1, 1]:
    y = y_side * (width/2 - column_size/2)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, z_beam))
    beam = bpy.context.active_object
    beam.scale = (length, column_size * 1.2, column_size)
    beam.name = f"Main_Beam_Long_{y_side}"

# Transverse beams (along width)
for x_side in [-1, 1]:
    x = x_side * (length/2 - column_size/2)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, z_beam))
    beam = bpy.context.active_object
    beam.scale = (column_size * 1.2, width, column_size)
    beam.name = f"Main_Beam_Trans_{x_side}"

# Cross-beams (rafters) creating shade pattern
num_cross_beams = int(length / beam_spacing)
z_rafter = z_beam + column_size/2

for i in range(num_cross_beams):
    x = -length/2 + i * beam_spacing + beam_spacing/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, z_rafter))
    rafter = bpy.context.active_object
    rafter.scale = (column_size * 0.7, width + column_size, column_size * 0.8)
    rafter.name = f"Cross_Beam_{i+1}"

# Decorative vines (twisted cylinders along columns)
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x_col = x_side * (length/2 - column_size/2)
        y_col = y_side * (width/2 - column_size/2)
        
        # Create spiral vine using multiple segments
        num_vine_segments = 15
        for i in range(num_vine_segments):
            t = i / num_vine_segments
            z = floor_height + t * column_height
            
            # Spiral around column
            angle = t * 4 * math.pi
            offset = column_size/2 + 0.05
            x_vine = x_col + math.cos(angle) * offset
            y_vine = y_col + math.sin(angle) * offset
            
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(x_vine, y_vine, z))
            vine_segment = bpy.context.active_object
            vine_segment.scale[2] = 2.0
            vine_segment.name = f"Vine_Segment_{x_side}_{y_side}_{i}"

# Hanging lanterns from corners
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (length/2 - 0.5)
        y = y_side * (width/2 - 0.5)
        z_lantern = z_beam - 0.3
        
        # Lantern chain
        bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.25, location=(x, y, z_beam - 0.125))
        chain = bpy.context.active_object
        chain.name = f"Lantern_Chain_{x_side}_{y_side}"
        
        # Lantern body (hexagonal)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.12, depth=0.2, location=(x, y, z_lantern))
        lantern = bpy.context.active_object
        lantern.name = f"Lantern_{x_side}_{y_side}"
        
        # Lantern top
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.13, depth=0.12, location=(x, y, z_lantern + 0.16))
        lantern_top = bpy.context.active_object
        lantern_top.name = f"Lantern_Top_{x_side}_{y_side}"

# Decorative pottery at base
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x_pot = x_side * (length/2 + 0.3)
        y_pot = y_side * (width/2 + 0.3)
        
        # Terra cotta pot
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.35, location=(x_pot, y_pot, floor_height + 0.175))
        pot = bpy.context.active_object
        pot.scale[0] = 1.1
        pot.scale[1] = 1.1
        pot.name = f"Pot_{x_side}_{y_side}"
        
        # Plant/bush in pot
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(x_pot, y_pot, floor_height + 0.45))
        plant = bpy.context.active_object
        plant.scale[2] = 0.8
        plant.name = f"Plant_{x_side}_{y_side}"

# Materials
mat_stucco = bpy.data.materials.new(name="White_Stucco")
mat_stucco.use_nodes = True
nodes = mat_stucco.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.95, 0.93, 0.88, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

mat_terracotta = bpy.data.materials.new(name="Terracotta")
mat_terracotta.use_nodes = True
nodes = mat_terracotta.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.75, 0.4, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

mat_wood = bpy.data.materials.new(name="Weathered_Wood")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.5, 0.4, 0.3, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9

mat_vine = bpy.data.materials.new(name="Green_Vine")
mat_vine.use_nodes = True
nodes = mat_vine.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.2, 0.5, 0.2, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

mat_lantern = bpy.data.materials.new(name="Bronze_Lantern")
mat_lantern.use_nodes = True
nodes = mat_lantern.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.6, 0.45, 0.25, 1.0)
bsdf.inputs['Metallic'].default_value = 0.7
bsdf.inputs['Roughness'].default_value = 0.5

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Column' in obj.name or 'Capital' in obj.name:
            obj.data.materials.append(mat_stucco)
        elif 'Floor' in obj.name or 'Pot' in obj.name:
            obj.data.materials.append(mat_terracotta)
        elif 'Beam' in obj.name or 'Cross' in obj.name:
            obj.data.materials.append(mat_wood)
        elif 'Vine' in obj.name or 'Plant' in obj.name:
            obj.data.materials.append(mat_vine)
        elif 'Lantern' in obj.name or 'Chain' in obj.name:
            obj.data.materials.append(mat_lantern)
        else:
            obj.data.materials.append(mat_stucco)

print("Mediterranean pergola gazebo created!")
