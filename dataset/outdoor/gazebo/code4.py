import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Modern minimalist gazebo parameters
platform_size = 4.0
platform_height = 0.1
post_height = 3.0
post_size = 0.1
roof_offset = 0.3

# Concrete platform (square, thin)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, platform_height/2))
platform = bpy.context.active_object
platform.scale = (platform_size, platform_size, platform_height)
platform.name = "Concrete_Platform"

# Four slim steel posts at corners
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x = x_side * (platform_size/2 - post_size)
        y = y_side * (platform_size/2 - post_size)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, platform_height + post_height/2))
        post = bpy.context.active_object
        post.scale = (post_size, post_size, post_height)
        post.name = f"Steel_Post_{x_side}_{y_side}"

# Floating roof (cantilevered, slightly larger than platform)
roof_size = platform_size + 2 * roof_offset
roof_thickness = 0.12
z_roof = platform_height + post_height

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_roof + roof_thickness/2))
roof = bpy.context.active_object
roof.scale = (roof_size, roof_size, roof_thickness)
roof.name = "Floating_Roof"

# Integrated LED strip channels (recessed lighting)
num_led_strips = 4
for i in range(num_led_strips):
    y = -roof_size/2 + (i + 1) * (roof_size / (num_led_strips + 1))
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, z_roof))
    led_channel = bpy.context.active_object
    led_channel.scale = (roof_size - 0.2, 0.04, 0.03)
    led_channel.name = f"LED_Channel_{i+1}"

# Minimalist bench (built-in seating along one side)
bench_height = 0.45
bench_depth = 0.5
bench_y = platform_size/2 - bench_depth/2 - 0.1

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, bench_y, platform_height + bench_height/2))
bench_seat = bpy.context.active_object
bench_seat.scale = (platform_size - 0.4, bench_depth, bench_height)
bench_seat.name = "Built_in_Bench"

# Bench backrest
backrest_height = 0.4
backrest_thickness = 0.08

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, bench_y + bench_depth/2 - backrest_thickness/2, platform_height + bench_height + backrest_height/2))
backrest = bpy.context.active_object
backrest.scale = (platform_size - 0.4, backrest_thickness, backrest_height)
backrest.name = "Bench_Backrest"

# Vertical accent slats (decorative privacy screen on one side)
num_slats = 8
slat_width = 0.08
slat_thickness = 0.04
slat_spacing = (platform_size - 0.8) / num_slats
screen_x = -platform_size/2 + 0.2

for i in range(num_slats):
    y = -platform_size/2 + 0.4 + i * slat_spacing
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(screen_x, y, platform_height + post_height/2))
    slat = bpy.context.active_object
    slat.scale = (slat_thickness, slat_width, post_height - 0.5)
    slat.name = f"Screen_Slat_{i+1}"

# Geometric planter boxes (integrated into design)
planter_size = 0.4
planter_height = 0.35

for position in [(-1, -1), (1, -1)]:
    x = position[0] * (platform_size/2 - planter_size/2 - 0.15)
    y = position[1] * (platform_size/2 - planter_size/2 - 0.15)
    
    # Planter box (cube)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, platform_height + planter_height/2))
    planter = bpy.context.active_object
    planter.scale = (planter_size, planter_size, planter_height)
    planter.name = f"Planter_Box_{position}"
    
    # Simple plant representation (geometric)
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.15, depth=0.4, location=(x, y, platform_height + planter_height + 0.2))
    plant = bpy.context.active_object
    plant.rotation_euler[2] = math.pi/6
    plant.name = f"Geometric_Plant_{position}"

# Cable tension details (thin support cables)
cable_radius = 0.005
for x_side in [-1, 1]:
    for y_side in [-1, 1]:
        x_post = x_side * (platform_size/2 - post_size)
        y_post = y_side * (platform_size/2 - post_size)
        
        # Diagonal cable from top of post to opposite corner of roof
        x_roof = -x_side * roof_size/2
        y_roof = -y_side * roof_size/2
        
        x_mid = (x_post + x_roof) / 2
        y_mid = (y_post + y_roof) / 2
        z_mid = (platform_height + post_height + z_roof) / 2
        
        cable_length = math.sqrt((x_roof - x_post)**2 + (y_roof - y_post)**2 + 0.01**2)
        
        bpy.ops.mesh.primitive_cylinder_add(radius=cable_radius, depth=cable_length, location=(x_mid, y_mid, z_mid))
        cable = bpy.context.active_object
        
        # Rotate cable
        xy_length = math.sqrt((x_roof - x_post)**2 + (y_roof - y_post)**2)
        if xy_length > 0:
            pitch = math.atan2(0.01, xy_length)
            yaw = math.atan2(y_roof - y_post, x_roof - x_post)
            cable.rotation_euler[1] = pitch
            cable.rotation_euler[2] = yaw
        
        cable.name = f"Tension_Cable_{x_side}_{y_side}"

# Materials
mat_concrete = bpy.data.materials.new(name="Polished_Concrete")
mat_concrete.use_nodes = True
nodes = mat_concrete.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.6, 1.0)
bsdf.inputs['Roughness'].default_value = 0.3

mat_steel = bpy.data.materials.new(name="Brushed_Steel")
mat_steel.use_nodes = True
nodes = mat_steel.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.72, 1.0)
bsdf.inputs['Metallic'].default_value = 0.95
bsdf.inputs['Roughness'].default_value = 0.25

mat_wood_dark = bpy.data.materials.new(name="Dark_Wood_Modern")
mat_wood_dark.use_nodes = True
nodes = mat_wood_dark.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.15, 0.12, 0.1, 1.0)
bsdf.inputs['Roughness'].default_value = 0.4

mat_led = bpy.data.materials.new(name="LED_Emission")
mat_led.use_nodes = True
nodes = mat_led.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 0.95, 1.0)
bsdf.inputs['Emission Strength'].default_value = 3.0
bsdf.inputs['Emission Color'].default_value = (1.0, 1.0, 0.95, 1.0)

mat_plant = bpy.data.materials.new(name="Modern_Plant")
mat_plant.use_nodes = True
nodes = mat_plant.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.3, 0.6, 0.3, 1.0)
bsdf.inputs['Roughness'].default_value = 0.6

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Platform' in obj.name or 'Roof' in obj.name:
            obj.data.materials.append(mat_concrete)
        elif 'Post' in obj.name or 'Cable' in obj.name:
            obj.data.materials.append(mat_steel)
        elif 'Bench' in obj.name or 'Slat' in obj.name or 'Planter' in obj.name:
            obj.data.materials.append(mat_wood_dark)
        elif 'LED' in obj.name:
            obj.data.materials.append(mat_led)
        elif 'Plant' in obj.name:
            obj.data.materials.append(mat_plant)

print("Modern minimalist gazebo created!")
