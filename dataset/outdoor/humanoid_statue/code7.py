import bpy
from math import radians

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create humanoid using UV spheres, cylinders, and cubes
def add_sphere(name, location, radius):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=32, ring_count=16)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_cylinder(name, location, radius, depth, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def add_cube(name, location, size):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj

# Head
head = add_sphere("Head", (0, 0, 1.65), 0.13)

# Neck
neck = add_cylinder("Neck", (0, 0, 1.45), 0.05, 0.15)

# Torso (upper and lower) - using cubes for angular appearance
chest = add_cube("Chest", (0, 0, 1.3), 0.36)
chest.scale = (1, 0.7, 1.2)

belly = add_cube("Belly", (0, 0, 1.05), 0.32)
belly.scale = (1, 0.7, 1)

# Shoulders
l_shoulder = add_sphere("L_Shoulder", (-0.22, 0, 1.3), 0.08)
r_shoulder = add_sphere("R_Shoulder", (0.22, 0, 1.3), 0.08)

# Upper arms (20% thicker)
l_upper_arm = add_cylinder("L_UpperArm", (-0.3, 0, 1.1), 0.06, 0.35, (0, radians(10), 0))
r_upper_arm = add_cylinder("R_UpperArm", (0.3, 0, 1.1), 0.06, 0.35, (0, radians(-10), 0))

# Forearms (20% thicker)
l_forearm = add_cylinder("L_Forearm", (-0.35, 0, 0.85), 0.048, 0.3, (0, radians(5), 0))
r_forearm = add_cylinder("R_Forearm", (0.35, 0, 0.85), 0.048, 0.3, (0, radians(-5), 0))

# Hands
l_hand = add_sphere("L_Hand", (-0.37, 0, 0.68), 0.05)
r_hand = add_sphere("R_Hand", (0.37, 0, 0.68), 0.05)

# Hips - using cube for angular appearance
hips = add_cube("Hips", (0, 0, 0.9), 0.34)
hips.scale = (1.1, 0.7, 0.8)

# Upper legs (20% thicker)
l_upper_leg = add_cylinder("L_UpperLeg", (-0.11, 0, 0.65), 0.084, 0.4)
r_upper_leg = add_cylinder("R_UpperLeg", (0.11, 0, 0.65), 0.084, 0.4)

# Lower legs (20% thicker)
l_lower_leg = add_cylinder("L_LowerLeg", (-0.11, 0, 0.3), 0.066, 0.35)
r_lower_leg = add_cylinder("R_LowerLeg", (0.11, 0, 0.3), 0.066, 0.35)

# Feet
l_foot = add_sphere("L_Foot", (-0.11, 0.05, 0.08), 0.07)
l_foot.scale = (1, 1.5, 0.8)
r_foot = add_sphere("R_Foot", (0.11, 0.05, 0.08), 0.07)
r_foot.scale = (1, 1.5, 0.8)

# Select all body parts and join
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.select_all(action='DESELECT')

body_parts = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name != 'Pedestal']
for obj in body_parts:
    obj.select_set(True)

bpy.context.view_layer.objects.active = body_parts[0]
bpy.ops.object.join()

statue = bpy.context.active_object
statue.name = "Humanoid_Statue"

# Smooth shading
bpy.ops.object.shade_smooth()

# Add Subdivision Surface
subsurf = statue.modifiers.new(name="Subsurf", type="SUBSURF")
subsurf.levels = 2
subsurf.render_levels = 3

# Create dark bronze material
mat = bpy.data.materials.new(name="Dark_Bronze")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (400, 0)

principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.location = (0, 0)

noise = nodes.new(type='ShaderNodeTexNoise')
noise.location = (-600, 0)
noise.inputs['Scale'].default_value = 8.0
noise.inputs['Detail'].default_value = 6.0

color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (-300, 0)
color_ramp.color_ramp.elements[0].color = (0.25, 0.15, 0.08, 1)
color_ramp.color_ramp.elements[1].color = (0.4, 0.25, 0.12, 1)

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-800, 0)

# Principled settings for polished bronze
principled.inputs['Roughness'].default_value = 0.1
principled.inputs['Metallic'].default_value = 0.95

# Connect nodes
links = mat.node_tree.links
links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material
statue.data.materials.append(mat)

# Pedestal
bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.25, location=(0, 0, 0.125))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal"
pedestal.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Camera
bpy.ops.object.camera_add(location=(2.5, -2.5, 1.5), rotation=(radians(75), 0, radians(45)))
camera = bpy.context.active_object
camera.data.lens = 50
bpy.context.scene.camera = camera

# Lights
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 2.5
sun.rotation_euler = (radians(45), 0, radians(45))

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 2))
area = bpy.context.active_object
area.data.energy = 150
area.data.size = 2

# Select statue to view
statue.select_set(True)
bpy.context.view_layer.objects.active = statue

print("✓ Angular bronze humanoid statue created!")



