import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create simple main car body - just one elongated box (lower and wider for sports car)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.55))
car_body = bpy.context.active_object
car_body.name = "CarBody"
car_body.scale = (2.5, 1.2, 0.3)

# Create simple cabin - smaller box on top
bpy.ops.mesh.primitive_cube_add(size=2, location=(-0.2, 0, 1.1))
car_cabin = bpy.context.active_object
car_cabin.name = "CarCabin"
car_cabin.scale = (1.3, 0.95, 0.3)

# Function to create realistic wheel
def create_wheel(x, y, name):
    z = 0.45  # Wheel height from ground
    
    # Main tire (torus for realistic profile)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.4,
        minor_radius=0.15,
        location=(x, y, z),
        rotation=(math.radians(90), 0, 0),
        major_segments=48,
        minor_segments=16
    )
    tire = bpy.context.active_object
    tire.name = name + "_Tire"
    
    # Rim (disc)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.32,
        depth=0.12,
        location=(x, y, z),
        rotation=(math.radians(90), 0, 0),
        vertices=32
    )
    rim = bpy.context.active_object
    rim.name = name + "_Rim"
    
    # Hub cap
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.15,
        depth=0.08,
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

# Create wheels - perfectly symmetric positioning (adjusted for wider body)
front_x = 1.5
rear_x = -1.5
wheel_y = 1.25  # Distance from center (adjusted for wider body)

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
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(x, y, z), segments=16, ring_count=8)
    light = bpy.context.active_object
    light.name = name
    light.scale = (0.7, 1, 1)
    bpy.ops.object.shade_smooth()
    return light

# Create simple headlights (adjusted for wider body)
headlights = [
    create_light(2.6, 0.75, 0.55, "HeadlightRight"),
    create_light(2.6, -0.75, 0.55, "HeadlightLeft")
]

# Create simple taillights (adjusted for wider body)
taillights = [
    create_light(-2.6, 0.75, 0.6, "TaillightRight"),
    create_light(-2.6, -0.75, 0.6, "TaillightLeft")
]

# Create materials
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

# Create and assign materials (vibrant red metallic for sports car)
body_mat = create_material("BodyMat", (0.85, 0.08, 0.05, 1.0), metallic=0.95, roughness=0.1)  # Vibrant red metallic
tire_mat = create_material("TireMat", (0.03, 0.03, 0.03, 1.0), metallic=0.0, roughness=0.9)  # Rubber
rim_mat = create_material("RimMat", (0.85, 0.85, 0.85, 1.0), metallic=0.95, roughness=0.05)  # Chrome
hub_mat = create_material("HubMat", (0.1, 0.1, 0.1, 1.0), metallic=0.8, roughness=0.2)  # Dark metal
light_mat = create_material("LightMat", (1.0, 0.95, 0.85, 1.0), metallic=0.0, roughness=0.1)  # White light
tail_mat = create_material("TailMat", (0.9, 0.05, 0.05, 1.0), metallic=0.2, roughness=0.2, emission=2.0)  # Red light

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

bpy.context.active_object.name = "RedSportsCar"

print("Red sports car created successfully!")
