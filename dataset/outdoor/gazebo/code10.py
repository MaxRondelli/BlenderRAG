import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Gothic Revival gazebo parameters
base_size = 3.5
num_sides = 6
floor_height = 0.3
column_height = 3.2
spire_height = 2.5

# Stone hexagonal platform
bpy.ops.mesh.primitive_cylinder_add(vertices=num_sides, radius=base_size/1.5, depth=floor_height, location=(0, 0, floor_height/2))
floor = bpy.context.active_object
floor.name = "Stone_Floor"

# Six slender Gothic columns with clustered shafts
for i in range(num_sides):
    angle = (2 * math.pi / num_sides) * i
    x = math.cos(angle) * (base_size/2 - 0.2)
    y = math.sin(angle) * (base_size/2 - 0.2)
    
    # Main column
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=column_height, location=(x, y, floor_height + column_height/2))
    column = bpy.context.active_object
    column.name = f"Gothic_Column_{i+1}"
    
    # Clustered shafts (three smaller columns around main)
    for cluster_angle in [0, 2*math.pi/3, 4*math.pi/3]:
        x_cluster = x + math.cos(angle + cluster_angle) * 0.06
        y_cluster = y + math.sin(angle + cluster_angle) * 0.06
        
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=column_height, location=(x_cluster, y_cluster, floor_height + column_height/2))
        cluster_shaft = bpy.context.active_object
        cluster_shaft.name = f"Cluster_Shaft_{i+1}_{cluster_angle}"
    
    # Ornate capital with crockets
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.15, depth=0.25, location=(x, y, floor_height + column_height - 0.125))
    capital = bpy.context.active_object
    capital.name = f"Gothic_Capital_{i+1}"
    
    # Crockets on capital
    num_crockets = 4
    for c in range(num_crockets):
        crocket_angle = angle + (2 * math.pi / num_crockets) * c
        x_c = x + math.cos(crocket_angle) * 0.15
        y_c = y + math.sin(crocket_angle) * 0.15
        z_c = floor_height + column_height - 0.1
        
        bpy.ops.mesh.primitive_cone_add(radius1=0.03, depth=0.12, location=(x_c, y_c, z_c))
        crocket = bpy.context.active_object
        crocket.rotation_euler[1] = math.pi/4
        crocket.rotation_euler[2] = crocket_angle
        crocket.name = f"Crocket_{i+1}_{c}"

# Pointed Gothic arches between columns
z_arch = floor_height + column_height/2




# Hexagonal spire roof
z_spire_base = floor_height + column_height + 0.2

# Base of spire (hexagonal drum)
bpy.ops.mesh.primitive_cylinder_add(vertices=num_sides, radius=base_size/2., depth=0.4, location=(0, 0, z_spire_base + 0.2))
drum = bpy.context.active_object
drum.name = "Spire_Drum"

# Main spire (tall pointed cone)
bpy.ops.mesh.primitive_cone_add(vertices=num_sides, radius1=base_size/2.5, depth=spire_height, location=(0, 0, z_spire_base + 0.4 + spire_height/2))
spire = bpy.context.active_object
spire.name = "Gothic_Spire"



# Crockets along spire edges
num_crocket_levels = 6
for level in range(num_crocket_levels):
    t = level / num_crocket_levels
    z_level = z_spire_base + 0.4 + t * spire_height
    radius_level = (base_size/2.5) * (1 - t)
    
    for i in range(num_sides):
        angle = (2 * math.pi / num_sides) * i
        x_cr = math.cos(angle) * radius_level
        y_cr = math.sin(angle) * radius_level
        
        bpy.ops.mesh.primitive_cone_add(radius1=0.04, depth=0.15, location=(x_cr, y_cr, z_level))
        spire_crocket = bpy.context.active_object
        spire_crocket.rotation_euler[1] = math.pi/5
        spire_crocket.rotation_euler[2] = angle
        spire_crocket.name = f"Spire_Crocket_{level}_{i}"

# Finial cross at peak
z_finial = z_spire_base + 0.4 + spire_height

# Vertical cross beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_finial + 0.35))
cross_v = bpy.context.active_object
cross_v.scale = (0.04, 0.04, 0.7)
cross_v.name = "Cross_Vertical"

# Horizontal cross beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_finial + 0.5))
cross_h = bpy.context.active_object
cross_h.scale = (0.4, 0.04, 0.04)
cross_h.name = "Cross_Horizontal"

# Ornate cross ends
for x_offset in [-0.2, 0.2]:
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.05, depth=0.08, location=(x_offset, 0, z_finial + 0.5))
    cross_end = bpy.context.active_object
    cross_end.rotation_euler[0] = -math.pi/2 if x_offset < 0 else math.pi/2
    cross_end.name = f"Cross_End_{x_offset}"

# Pinnacles at each column top
for i in range(num_sides):
    angle = (2 * math.pi / num_sides) * i
    x_pin = math.cos(angle) * (base_size/2 - 0.2)
    y_pin = math.sin(angle) * (base_size/2 - 0.2)
    z_pin = floor_height + column_height
    
    # Pinnacle base
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=0.2, location=(x_pin, y_pin, z_pin + 0.1))
    pin_base = bpy.context.active_object
    pin_base.name = f"Pinnacle_Base_{i+1}"
    
    # Pinnacle spire
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.1, depth=0.6, location=(x_pin, y_pin, z_pin + 0.5))
    pinnacle = bpy.context.active_object
    pinnacle.name = f"Pinnacle_{i+1}"
    
    # Pinnacle finial
    bpy.ops.mesh.primitive_cone_add(radius1=0.03, depth=0.12, location=(x_pin, y_pin, z_pin + 0.86))
    pin_finial = bpy.context.active_object
    pin_finial.name = f"Pinnacle_Finial_{i+1}"

# Gothic bench with pointed arch backrest
bench_segments = 3
for seg in range(bench_segments):
    angle = (2 * math.pi / bench_segments) * seg + math.pi
    x_bench = math.cos(angle) * (base_size/2 - 0.8)
    y_bench = math.sin(angle) * (base_size/2 - 0.8)
    
    # Bench seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_bench, y_bench, floor_height + 0.25))
    bench_seat = bpy.context.active_object
    bench_seat.scale = (0.5, 0.4, 0.5)
    bench_seat.rotation_euler[2] = angle
    bench_seat.name = f"Bench_Seat_{seg}"
    
    # Pointed arch backrest
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.25, depth=0.5, location=(x_bench * 0.85, y_bench * 0.85, floor_height + 0.7))
    backrest = bpy.context.active_object
    backrest.rotation_euler[2] = angle + math.pi
    backrest.name = f"Bench_Backrest_{seg}"

# Materials
mat_stone_gray = bpy.data.materials.new(name="Gray_Stone")
mat_stone_gray.use_nodes = True
nodes = mat_stone_gray.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.52, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9

mat_dark_wood = bpy.data.materials.new(name="Dark_Oak")
mat_dark_wood.use_nodes = True
nodes = mat_dark_wood.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.25, 0.18, 0.12, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

mat_metal = bpy.data.materials.new(name="Wrought_Iron_Gothic")
mat_metal.use_nodes = True
nodes = mat_metal.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.15, 0.15, 0.15, 1.0)
bsdf.inputs['Metallic'].default_value = 0.85
bsdf.inputs['Roughness'].default_value = 0.5

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Bench' in obj.name:
            obj.data.materials.append(mat_dark_wood)
        elif 'Cross' in obj.name or 'Tracery' in obj.name or 'Quatrefoil' in obj.name:
            obj.data.materials.append(mat_metal)
        else:
            obj.data.materials.append(mat_stone_gray)

print("Gothic Revival gazebo created!")
