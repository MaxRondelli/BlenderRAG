import bpy
from math import radians

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create humanoid using UV spheres and cylinders
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

# Head
head = add_sphere("Head", (0, 0, 1.65), 0.15)

# Neck
neck = add_cylinder("Neck", (0, 0, 1.45), 0.07, 0.15)

# Torso (single elongated form)
torso = add_cylinder("Torso", (0, 0, 1.175), 0.22, 0.55)
torso.scale = (1, 0.7, 1)

# Shoulders
l_shoulder = add_sphere("L_Shoulder", (-0.25, 0, 1.3), 0.1)
r_shoulder = add_sphere("R_Shoulder", (0.25, 0, 1.3), 0.1)

# Upper arms (thicker)
l_upper_arm = add_cylinder("L_UpperArm", (-0.32, 0, 1.1), 0.07, 0.35, (0, radians(10), 0))
r_upper_arm = add_cylinder("R_UpperArm", (0.32, 0, 1.1), 0.07, 0.35, (0, radians(-10), 0))

# Forearms (thicker)
l_forearm = add_cylinder("L_Forearm", (-0.37, 0, 0.85), 0.06, 0.3, (0, radians(5), 0))
r_forearm = add_cylinder("R_Forearm", (0.37, 0, 0.85), 0.06, 0.3, (0, radians(-5), 0))

# Hands (larger)
l_hand = add_sphere("L_Hand", (-0.4, 0, 0.68), 0.07)
r_hand = add_sphere("R_Hand", (0.4, 0, 0.68), 0.07)

# Hips
hips = add_sphere("Hips", (0, 0, 0.9), 0.19)
hips.scale = (1.1, 0.7, 0.8)

# Upper legs (thicker)
l_upper_leg = add_cylinder("L_UpperLeg", (-0.11, 0, 0.65), 0.09, 0.4)
r_upper_leg = add_cylinder("R_UpperLeg", (0.11, 0, 0.65), 0.09, 0.4)

# Lower legs (thicker)
l_lower_leg = add_cylinder("L_LowerLeg", (-0.11, 0, 0.3), 0.075, 0.35)
r_lower_leg = add_cylinder("R_LowerLeg", (0.11, 0, 0.3), 0.075, 0.35)

# Feet (larger)
l_foot = add_sphere("L_Foot", (-0.11, 0.05, 0.08), 0.09)
l_foot.scale = (1, 1.5, 0.8)
r_foot = add_sphere("R_Foot", (0.11, 0.05, 0.08), 0.09)
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

# Add Subdivision Surface for smoother transitions
subsurf = statue.modifiers.new(name="Subsurf", type="SUBSURF")
subsurf.levels = 3
subsurf.render_levels = 4

# Create bronze metallic material
mat = bpy.data.materials.new(name="Bronze")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (400, 0)

principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.location = (0, 0)

noise = nodes.new(type='ShaderNodeTexNoise')
noise.location = (-600, 200)
noise.inputs['Scale'].default_value = 8.0
noise.inputs['Detail'].default_value = 15.0

color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (-300, 200)
color_ramp.color_ramp.elements[0].color = (0.52, 0.32, 0.12, 1)  # Dark bronze
color_ramp.color_ramp.elements[1].color = (0.72, 0.45, 0.18, 1)  # Amber bronze

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-800, 200)

# Additional noise for surface detail
detail_noise = nodes.new(type='ShaderNodeTexNoise')
detail_noise.location = (-600, -200)
detail_noise.inputs['Scale'].default_value = 25.0
detail_noise.inputs['Detail'].default_value = 8.0

mix_node = nodes.new(type='ShaderNodeMixRGB')
mix_node.location = (-150, 0)

# Principled settings for bronze metallic look
principled.inputs['Base Color'].default_value = (0.62, 0.38, 0.15, 1)
principled.inputs['Metallic'].default_value = 0.95
principled.inputs['Roughness'].default_value = 0.15
principled.inputs['IOR'].default_value = 2.9

# Connect nodes
links = mat.node_tree.links
links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
links.new(tex_coord.outputs['Generated'], detail_noise.inputs['Vector'])
links.new(mix_node.outputs['Color'], principled.inputs['Base Color'])
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
sun.data.energy = 3.0
sun.rotation_euler = (radians(45), 0, radians(45))

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 2))
area = bpy.context.active_object
area.data.energy = 200
area.data.size = 2

# Additional rim light for metallic highlights
bpy.ops.object.light_add(type='SPOT', location=(1, 2, 3))
spot = bpy.context.active_object
spot.data.energy = 100
spot.rotation_euler = (radians(-30), 0, radians(-45))

# Select statue to view
statue.select_set(True)
bpy.context.view_layer.objects.active = statue

print("✓ Bronze metallic humanoid statue created!")


