import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Chinese pavilion parameters
base_size = 4.0
floor_height = 0.4
column_height = 3.0
column_radius = 0.18
roof_tiers = 2

# Stone platform with steps
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, floor_height/2))
platform = bpy.context.active_object
platform.scale = (base_size, base_size, floor_height)
platform.name = "Stone_Platform"

# Three-tier steps
for i in range(3):
    step_size = base_size + (3-i) * 0.35
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -i * 0.1 ))
    step = bpy.context.active_object
    step.scale = (step_size, step_size, 0.18)
    step.name = f"Step_{i+1}"

# Four red lacquered columns
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (base_size/2 - 0.4)
        y = y_side * (base_size/2 - 0.4)
        
        # Stone base
        bpy.ops.mesh.primitive_cylinder_add(radius=column_radius * 1.4, depth=0.3, location=(x, y, floor_height +0.15))
        base = bpy.context.active_object
        base.name = f"Column_Base_{x_side}_{y_side}"
        
        # Main column (slightly tapered)
        bpy.ops.mesh.primitive_cylinder_add(radius=column_radius, depth=column_height, location=(x, y, floor_height + 0.3 + column_height/1.8))
        column = bpy.context.active_object
        column.name = f"Red_Column_{x_side}_{y_side}"
        
        # Ornate bracket (dougong)
        num_brackets = 4
        for b in range(num_brackets):
            z_bracket = floor_height + 0.3 + column_height - 0.1 * b
            bracket_size = column_radius * (1.8 + b * 0.3)
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z_bracket))
            bracket = bpy.context.active_object
            bracket.scale = (bracket_size, bracket_size, 0.08)
            bracket.name = f"Bracket_{x_side}_{y_side}_{b}"

# Decorative railings with lattice pattern
z_rail_bottom = floor_height + 0.5
z_rail_top = floor_height + 1.2

for side in ['north', 'east', 'south', 'west']:
    if side == 'north':
        x1, y1 = -(base_size/2 - 0.4), (base_size/2 - 0.4)
        x2, y2 = (base_size/2 - 0.4), (base_size/2 - 0.4)
    elif side == 'east':
        x1, y1 = (base_size/2 - 0.4), (base_size/2 - 0.4)
        x2, y2 = (base_size/2 - 0.4), -(base_size/2 - 0.4)
    elif side == 'south':
        x1, y1 = (base_size/2 - 0.4), -(base_size/2 - 0.4)
        x2, y2 = -(base_size/2 - 0.4), -(base_size/2 - 0.4)
    else:  # west
        x1, y1 = -(base_size/2 - 0.4), -(base_size/2 - 0.4)
        x2, y2 = -(base_size/2 - 0.4), (base_size/2 - 0.4)
    
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2
    length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    rotation = math.atan2(y2 - y1, x2 - x1)
    
    # Top and bottom rails
    for z_rail in [z_rail_bottom, z_rail_top]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_mid, y_mid, z_rail))
        rail = bpy.context.active_object
        rail.scale = (length, 0.06, 0.06)
        rail.rotation_euler[2] = rotation
        rail.name = f"Rail_{side}_{z_rail}"
    
    # Lattice pattern (diagonal crosses)
    num_sections = 4
    for i in range(num_sections):
        t = (i + 0.5) / num_sections
        x_lattice = x1 + t * (x2 - x1)
        y_lattice = y1 + t * (y2 - y1)
        z_lattice = (z_rail_bottom + z_rail_top) / 2
        
        # Diagonal 1
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_lattice, y_lattice, z_lattice))
        diag1 = bpy.context.active_object
        diag1.scale = (0.04, 0.04, z_rail_top - z_rail_bottom)
        diag1.rotation_euler[2] = rotation + math.pi/4
        diag1.name = f"Lattice_Diag1_{side}_{i}"
        
        # Diagonal 2
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_lattice, y_lattice, z_lattice))
        diag2 = bpy.context.active_object
        diag2.scale = (0.04, 0.04, z_rail_top - z_rail_bottom)
        diag2.rotation_euler[2] = rotation - math.pi/4
        diag2.name = f"Lattice_Diag2_{side}_{i}"

# Double-tiered curved roof (flying eaves)
z_first_roof = floor_height + 0.2 + column_height

for tier in range(roof_tiers):
    tier_size = base_size * (1.3 - tier * 0.2)
    tier_height = 1.2 - tier * 0.4
    z_tier = z_first_roof + tier * 0.4
    
    # Main roof surface (curved upward edges)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_tier + tier_height/3))
    roof_base = bpy.context.active_object
    roof_base.scale = (tier_size, tier_size, tier_height/3)
    roof_base.name = f"Roof_Base_T{tier+1}"
    
   
# Decorative ridge ornaments
z_ridge = z_first_roof + roof_tiers * 0.5

# Central finial (baozhu - precious pearl)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0, z_ridge))
pearl = bpy.context.active_object
pearl.name = "Precious_Pearl"



# Hanging wind chimes
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x_chime = x_side * (base_size/2)
        y_chime = y_side * (base_size/2)
        z_chime = z_first_roof - 0.3
        
        # Chime string
        bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.25, location=(x_chime, y_chime, z_first_roof - 0.125))
        string = bpy.context.active_object
        string.name = f"Chime_String_{x_side}_{y_side}"
        
        # Chime bells (3 per string)
        for b in range(3):
            z_bell = z_chime - b * 0.08
            bpy.ops.mesh.primitive_cone_add(radius1=0.04, depth=0.06, location=(x_chime, y_chime, z_bell))
            bell = bpy.context.active_object
            bell.name = f"Wind_Bell_{x_side}_{y_side}_{b}"





# Materials
mat_red_lacquer = bpy.data.materials.new(name="Red_Lacquer")
mat_red_lacquer.use_nodes = True
nodes = mat_red_lacquer.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.7, 0.1, 0.1, 1.0)
bsdf.inputs['Roughness'].default_value = 0.2
bsdf.inputs['Specular IOR Level'].default_value = 0.8

mat_gold = bpy.data.materials.new(name="Gold_Ornament")
mat_gold.use_nodes = True
nodes = mat_gold.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.9, 0.75, 0.2, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.2

mat_stone = bpy.data.materials.new(name="Gray_Stone")
mat_stone.use_nodes = True
nodes = mat_stone.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.55, 0.55, 0.53, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

mat_roof_tile = bpy.data.materials.new(name="Glazed_Tiles")
mat_roof_tile.use_nodes = True
nodes = mat_roof_tile.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.15, 0.35, 0.15, 1.0)
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['Specular IOR Level'].default_value = 0.7

mat_wood_dark = bpy.data.materials.new(name="Dark_Wood_Chinese")
mat_wood_dark.use_nodes = True
nodes = mat_wood_dark.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.25, 0.15, 0.1, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Column' in obj.name and 'Base' not in obj.name:
            obj.data.materials.append(mat_red_lacquer)
        elif 'Roof' in obj.name or 'Eave' in obj.name:
            obj.data.materials.append(mat_roof_tile)
        elif 'Pearl' in obj.name or 'Dragon' in obj.name or 'Bracket' in obj.name:
            obj.data.materials.append(mat_gold)
        elif 'Platform' in obj.name or 'Step' in obj.name or 'Base' in obj.name or 'Moon_Gate' in obj.name:
            obj.data.materials.append(mat_stone)
        else:
            obj.data.materials.append(mat_wood_dark)

print("Chinese pavilion gazebo created!")

