import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sleek sports car body - lower and more angular
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.45))
car_body = bpy.context.active_object
car_body.name = "CarBody"
car_body.scale = (2.8, 1.1, 0.25)

# Create low-profile cabin - more angular and lower
bpy.ops.mesh.primitive_cube_add(size=2, location=(-0.2, 0, 0.95))
car_cabin = bpy.context.active_object
car_cabin.name = "CarCabin"
car_cabin.scale = (1.2, 0.85, 0.3)

# Create yellow racing stripes
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.7))
stripe_center = bpy.context.active_object
stripe_center.name = "StripeCenter"
stripe_center.scale = (2.9, 0.15, 0.01)

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0.4, 0.7))
stripe_left = bpy.context.active_object
stripe_left.name = "StripeLeft"
stripe_left.scale = (2.9, 0.05, 0.01)

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, -0.4, 0.7))
stripe_right = bpy.context.active_object
stripe_right.name = "StripeRight"
stripe_right.scale = (2.9, 0.05, 0.01)

# Function to create low-profile racing wheels
def create_wheel(x, y, name):
    z = 0.35  # Lower wheel height for sports car
    
    # Low-profile tire
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
    
    # Large racing rim
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.38,
        depth=0.1,
        location=(x, y, z),
        rotation=(math.radians(90), 0, 0),
        vertices=32
    )
    rim = bpy.context.active_object
    rim.name = name + "_Rim"
    
    # Sports hub with spokes
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

# Create wheels - wider stance for sports car
front_x = 1.6
rear_x = -1.6
wheel_y = 1.25

wheels_data = [
    create_wheel(front_x, wheel_y, "FrontRight"),
    create_wheel(front_x, -wheel_y, "FrontLeft"),
    create_wheel(rear_x, wheel_y, "RearRight"),
    create_wheel(rear_x, -wheel_y, "RearLeft")
]

tires = [w[0] for w in wheels_data]
rims = [w[1] for w in wheels_data]
hubs = [w[2] for w in wheels_data]

# Function to create aggressive lights
def create_light(x, y, z, name):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y, z), segments=16, ring_count=8)
    light = bpy.context.active_object
    light.name = name
    light.scale = (0.8, 1.2, 0.6)
    bpy.ops.object.shade_smooth()
    return light

# Create sleek headlights
headlights = [
    create_light(2.9, 0.7, 0.45, "HeadlightRight"),
    create_light(2.9, -0.7, 0.45, "HeadlightLeft")
]

# Create aggressive taillights
taillights = [
    create_light(-2.9, 0.7, 0.5, "TaillightRight"),
    create_light(-2.9, -0.7, 0.5, "TaillightLeft")
]

# Create materials for sports car
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

# Create racing materials
matte_black_mat = create_material("MatteBlackMat", (0.05, 0.05, 0.05, 1.0), metallic=0.1, roughness=0.8)
yellow_stripe_mat = create_material("YellowStripeMat", (1.0, 0.9, 0.0, 1.0), metallic=0.3, roughness=0.2)
racing_tire_mat = create_material("RacingTireMat", (0.02, 0.02, 0.02, 1.0), metallic=0.0, roughness=0.95)
silver_rim_mat = create_material("SilverRimMat", (0.9, 0.9, 0.95, 1.0), metallic=0.98, roughness=0.02)
carbon_hub_mat = create_material("CarbonHubMat", (0.08, 0.08, 0.08, 1.0), metallic=0.9, roughness=0.1)
xenon_light_mat = create_material("XenonLightMat", (0.9, 0.95, 1.0, 1.0), metallic=0.0, roughness=0.0, emission=3.0)
led_tail_mat = create_material("LEDTailMat", (1.0, 0.0, 0.0, 1.0), metallic=0.1, roughness=0.1, emission=4.0)

# Apply materials to body parts
for obj in [car_body, car_cabin]:
    obj.data.materials.append(matte_black_mat)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

for obj in [stripe_center, stripe_left, stripe_right]:
    obj.data.materials.append(yellow_stripe_mat)

for tire in tires:
    tire.data.materials.append(racing_tire_mat)
for rim in rims:
    rim.data.materials.append(silver_rim_mat)
for hub in hubs:
    hub.data.materials.append(carbon_hub_mat)

for headlight in headlights:
    headlight.data.materials.append(xenon_light_mat)
for taillight in taillights:
    taillight.data.materials.append(led_tail_mat)

# Join all parts
bpy.ops.object.select_all(action='DESELECT')
all_parts = [car_body, car_cabin, stripe_center, stripe_left, stripe_right] + \
            tires + rims + hubs + headlights + taillights

for obj in all_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = car_body
bpy.ops.object.join()

bpy.context.active_object.name = "SportsRacingCar"

print("Sleek sports racing car created successfully!")
