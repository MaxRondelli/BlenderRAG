import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sporty main car body - lower, wider profile
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.5))
car_body = bpy.context.active_object
car_body.name = "CarBody"
car_body.scale = (2.8, 1.2, 0.25)

# Create sporty cabin - lower and more angular
bpy.ops.mesh.primitive_cube_add(size=2, location=(-0.2, 0, 0.95))
car_cabin = bpy.context.active_object
car_cabin.name = "CarCabin"
car_cabin.scale = (1.4, 1.0, 0.32)

# Function to create sporty wheel with silver accents
def create_wheel(x, y, name):
    z = 0.35  # Lower ride height for sporty look
    
    # Main tire (torus for realistic profile) - slightly wider
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.42,
        minor_radius=0.12,
        location=(x, y, z),
        rotation=(math.radians(90), 0, 0),
        major_segments=48,
        minor_segments=16
    )
    tire = bpy.context.active_object
    tire.name = name + "_Tire"
    
    # Rim (disc) - larger for sporty look
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.35,
        depth=0.1,
        location=(x, y, z),
        rotation=(math.radians(90), 0, 0),
        vertices=32
    )
    rim = bpy.context.active_object
    rim.name = name + "_Rim"
    
    # Hub cap - more prominent
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.18,
        depth=0.06,
        location=(x, y, z),
        rotation=(math.radians(90), 0, 0),
        vertices=16
    )
    hub = bpy.context.active_object
    hub.name = name + "_Hub"
    
    # Apply smooth shading
    for obj in [tire, rim, hub]:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
    
    return tire, rim, hub

# Create wheels - wider stance for sporty look
front_x = 1.6
rear_x = -1.6
wheel_y = 1.3  # Wider stance

wheels_data = [
    create_wheel(front_x, wheel_y, "FrontRight"),
    create_wheel(front_x, -wheel_y, "FrontLeft"),
    create_wheel(rear_x, wheel_y, "RearRight"),
    create_wheel(rear_x, -wheel_y, "RearLeft")
]

tires = [w[0] for w in wheels_data]
rims = [w[1] for w in wheels_data]
hubs = [w[2] for w in wheels_data]

# Function to create lights
def create_light(x, y, z, name):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y, z), segments=16, ring_count=8)
    light = bpy.context.active_object
    light.name = name
    light.scale = (0.8, 1, 1)
    bpy.ops.object.shade_smooth()
    return light

# Create sporty headlights - lower position
headlights = [
    create_light(2.85, 0.7, 0.55, "HeadlightRight"),
    create_light(2.85, -0.7, 0.55, "HeadlightLeft")
]

# Create sporty taillights - lower position
taillights = [
    create_light(-2.85, 0.7, 0.6, "TaillightRight"),
    create_light(-2.85, -0.7, 0.6, "TaillightLeft")
]

# Create materials with sporty color scheme
def create_material(name, color, metallic=0.0, roughness=0.5, emission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if emission > 0:
            bsdf.inputs['Emission Strength'].default_value = emission
    return mat

# Create and assign materials - dark metallic blue with silver accents
body_mat = create_material("SportyBodyMat", (0.05, 0.1, 0.3, 1.0), metallic=0.95, roughness=0.08)  # Dark metallic blue
tire_mat = create_material("SportyTireMat", (0.02, 0.02, 0.02, 1.0), metallic=0.0, roughness=0.95)  # Sport tire rubber
rim_mat = create_material("SportyRimMat", (0.95, 0.95, 0.98, 1.0), metallic=0.98, roughness=0.02)  # Bright silver chrome
hub_mat = create_material("SportyHubMat", (0.9, 0.92, 0.95, 1.0), metallic=0.9, roughness=0.15)  # Silver accents
light_mat = create_material("SportyLightMat", (1.0, 1.0, 1.0, 1.0), metallic=0.0, roughness=0.05)  # Bright white
tail_mat = create_material("SportyTailMat", (0.95, 0.02, 0.02, 1.0), metallic=0.3, roughness=0.15, emission=2.5)  # Bright red

# Apply materials to body parts
for obj in [car_body, car_cabin]:
    obj.data.materials.append(body_mat)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

for tire in tires:
    tire.data.materials.append(tire_mat)
for rim in rims:
    rim.data.materials.append(rim_mat)
for hub in hubs:
    hub.data.materials.append(hub_mat)

for headlight in headlights:
    headlight.data.materials.append(light_mat)
for taillight in taillights:
    taillight.data.materials.append(tail_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = [car_body, car_cabin] + \
            tires + rims + hubs + headlights + taillights

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = car_body
bpy.ops.object.join()

bpy.context.active_object.name = "SportyCar"

print("Sporty car with dark metallic blue paint and silver accents created successfully!")