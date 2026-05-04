import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Hexagonal pavilion parameters
diameter = 3.8
num_sides = 6
floor_height = 0.25
column_height = 2.6
column_radius = 0.1
roof_height = 1.4

# Hexagonal stone platform
bpy.ops.mesh.primitive_cylinder_add(vertices=num_sides, radius=diameter/2, depth=floor_height, location=(0, 0, floor_height/2))
platform = bpy.context.active_object
platform.name = "Stone_Platform"

# Stone step around platform
bpy.ops.mesh.primitive_cylinder_add(vertices=num_sides, radius=diameter/2 + 0.25, depth=0.15, location=(0, 0, -0.075))
step = bpy.context.active_object
step.name = "Platform_Step"

# Six wooden columns
for i in range(num_sides):
    angle = (2 * math.pi / num_sides) * i
    x = math.cos(angle) * (diameter/2 - 0.25)
    y = math.sin(angle) * (diameter/2 - 0.25)
    
    # Column
    bpy.ops.mesh.primitive_cylinder_add(radius=column_radius, depth=column_height, location=(x, y, floor_height + column_height/2))
    column = bpy.context.active_object
    column.name = f"Wood_Column_{i+1}"
    
    # Simple capital
    bpy.ops.mesh.primitive_cylinder_add(radius=column_radius * 1.3, depth=0.15, location=(x, y, floor_height + column_height - 0.075))
    capital = bpy.context.active_object
    capital.name = f"Column_Capital_{i+1}"

# Simple railings between columns
z_rail = floor_height + 0.9



# Hexagonal pyramid roof
z_roof_base = floor_height + column_height
z_roof_peak = z_roof_base + roof_height

bpy.ops.mesh.primitive_cone_add(vertices=num_sides, radius1=diameter/2 + 0.3, depth=roof_height, location=(0, 0, z_roof_base + roof_height/2))
roof = bpy.context.active_object
roof.name = "Pyramid_Roof"

# Decorative roof trim at base
bpy.ops.mesh.primitive_torus_add(major_radius=diameter/2 + 0.25, minor_radius=0.06, location=(0, 0, z_roof_base))
roof_trim = bpy.context.active_object
roof_trim.name = "Roof_Trim"

# Simple finial at peak
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, z_roof_peak))
finial_base = bpy.context.active_object
finial_base.name = "Finial_Base"

bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.3, location=(0, 0, z_roof_peak + 0.2))
finial_spike = bpy.context.active_object
finial_spike.name = "Finial_Spike"

# Central circular table
table_radius = 0.6
table_height = 0.75

bpy.ops.mesh.primitive_cylinder_add(radius=table_radius, depth=0.05, location=(0, 0, floor_height + table_height))
table_top = bpy.context.active_object
table_top.name = "Table_Top"

# Single central pedestal
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=table_height, location=(0, 0, floor_height + table_height/2))
pedestal = bpy.context.active_object
pedestal.name = "Table_Pedestal"

# Six chairs around table
chair_distance = 1.1
chair_seat_height = 0.45
chair_seat_size = 0.4

for i in range(num_sides):
    angle = (2 * math.pi / num_sides) * i
    x_chair = math.cos(angle) * chair_distance
    y_chair = math.sin(angle) * chair_distance
    
    # Chair seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_chair, y_chair, floor_height + chair_seat_height/2))
    seat = bpy.context.active_object
    seat.scale = (chair_seat_size, chair_seat_size, chair_seat_height)
    seat.name = f"Chair_Seat_{i+1}"
    
    # Chair back
    x_back = x_chair * 1.15
    y_back = y_chair * 1.15
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_back, y_back, floor_height + chair_seat_height + 0.3))
    back = bpy.context.active_object
    back.scale = (chair_seat_size, 0.06, 0.6)
    back.rotation_euler[2] = angle
    back.name = f"Chair_Back_{i+1}"

# Hanging lanterns from roof
lantern_height = z_roof_base - 0.4

for i in range(3):
    angle = (2 * math.pi / 3) * i + math.pi/6
    x_lantern = math.cos(angle) * (diameter/3)
    y_lantern = math.sin(angle) * (diameter/3)
    
    # Chain
    bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.3, location=(x_lantern, y_lantern, z_roof_base - 0.15))
    chain = bpy.context.active_object
    chain.name = f"Lantern_Chain_{i+1}"
    
    # Lantern body
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.1, depth=0.2, location=(x_lantern, y_lantern, lantern_height))
    lantern = bpy.context.active_object
    lantern.name = f"Lantern_{i+1}"
    
    # Lantern top
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.11, depth=0.1, location=(x_lantern, y_lantern, lantern_height + 0.15))
    lantern_top = bpy.context.active_object
    lantern_top.name = f"Lantern_Top_{i+1}"

# Decorative planters at alternating corners
for i in range(0, num_sides, 2):
    angle = (2 * math.pi / num_sides) * i
    x_planter = math.cos(angle) * (diameter/2 + 0.45)
    y_planter = math.sin(angle) * (diameter/2 + 0.45)
    
    # Planter pot
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.35, location=(x_planter, y_planter, floor_height + 0.175))
    planter = bpy.context.active_object
    planter.scale[0] = 1.1
    planter.scale[1] = 1.1
    planter.name = f"Planter_{i+1}"
    
    # Simple plant
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.2, depth=0.5, location=(x_planter, y_planter, floor_height + 0.5))
    plant = bpy.context.active_object
    plant.name = f"Plant_{i+1}"

# Materials
mat_stone = bpy.data.materials.new(name="Gray_Stone")
mat_stone.use_nodes = True
nodes = mat_stone.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.6, 0.58, 0.55, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

mat_wood_light = bpy.data.materials.new(name="Light_Oak")
mat_wood_light.use_nodes = True
nodes = mat_wood_light.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.65, 0.5, 0.35, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

mat_roof = bpy.data.materials.new(name="Dark_Shingles")
mat_roof.use_nodes = True
nodes = mat_roof.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.2, 0.15, 0.12, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9

mat_metal = bpy.data.materials.new(name="Brass")
mat_metal.use_nodes = True
nodes = mat_metal.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.7, 0.55, 0.3, 1.0)
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.3

mat_plant = bpy.data.materials.new(name="Green_Plant")
mat_plant.use_nodes = True
nodes = mat_plant.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.25, 0.5, 0.3, 1.0)
bsdf.inputs['Roughness'].default_value = 0.6

mat_terracotta = bpy.data.materials.new(name="Terracotta")
mat_terracotta.use_nodes = True
nodes = mat_terracotta.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.7, 0.4, 0.3, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Platform' in obj.name or 'Step' in obj.name:
            obj.data.materials.append(mat_stone)
        elif 'Roof' in obj.name:
            obj.data.materials.append(mat_roof)
        elif 'Lantern' in obj.name or 'Chain' in obj.name or 'Finial' in obj.name:
            obj.data.materials.append(mat_metal)
        elif 'Plant' in obj.name:
            obj.data.materials.append(mat_plant)
        elif 'Planter' in obj.name:
            obj.data.materials.append(mat_terracotta)
        else:
            obj.data.materials.append(mat_wood_light)

print("Hexagonal pavilion gazebo created!")
