import bpy
from math import radians

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create heroic humanoid using UV spheres and cylinders
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

# Head - slightly larger for heroic proportions
head = add_sphere("Head", (0, 0, 1.65), 0.15)

# Neck - thicker
neck = add_cylinder("Neck", (0, 0, 1.45), 0.07, 0.15)

# Torso (upper and lower) - broader and more muscular
chest = add_sphere("Chest", (0, 0, 1.3), 0.22)
chest.scale = (1.3, 0.8, 1.3)

belly = add_sphere("Belly", (0, 0, 1.05), 0.18)
belly.scale = (1.1, 0.75, 1.1)

# Shoulders - much broader for heroic look
l_shoulder = add_sphere("L_Shoulder", (-0.28, 0, 1.3), 0.1)
r_shoulder = add_sphere("R_Shoulder", (0.28, 0, 1.3), 0.1)

# Upper arms - thicker and more muscular
l_upper_arm = add_cylinder("L_UpperArm", (-0.37, 0, 1.1), 0.07, 0.35, (0, radians(10), 0))
r_upper_arm = add_cylinder("R_UpperArm", (0.37, 0, 1.1), 0.07, 0.35, (0, radians(-10), 0))

# Forearms - thicker
l_forearm = add_cylinder("L_Forearm", (-0.42, 0, 0.85), 0.06, 0.3, (0, radians(5), 0))
r_forearm = add_cylinder("R_Forearm", (0.42, 0, 0.85), 0.06, 0.3, (0, radians(-5), 0))

# Hands - larger
l_hand = add_sphere("L_Hand", (-0.45, 0, 0.68), 0.07)
r_hand = add_sphere("R_Hand", (0.45, 0, 0.68), 0.07)

# Hips - broader
hips = add_sphere("Hips", (0, 0, 0.9), 0.19)
hips.scale = (1.2, 0.75, 0.9)

# Upper legs - thicker
l_upper_leg = add_cylinder("L_UpperLeg", (-0.13, 0, 0.65), 0.09, 0.4)
r_upper_leg = add_cylinder("R_UpperLeg", (0.13, 0, 0.65), 0.09, 0.4)

# Lower legs - thicker
l_lower_leg = add_cylinder("L_LowerLeg", (-0.13, 0, 0.3), 0.075, 0.35)
r_lower_leg = add_cylinder("R_LowerLeg", (0.13, 0, 0.3), 0.075, 0.35)

# Feet
l_foot = add_sphere("L_Foot", (-0.13, 0.05, 0.08), 0.08)
l_foot.scale = (1, 1.5, 0.8)
r_foot = add_sphere("R_Foot", (0.13, 0.05, 0.08), 0.08)
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
statue.name = "Heroic_Statue"

# Smooth shading
bpy.ops.object.shade_smooth()

# Add Subdivision Surface
subsurf = statue.modifiers.new(name="Subsurf", type="SUBSURF")
subsurf.levels = 2
subsurf.render_levels = 3

# Create dark charcoal marble material with high contrast veining
mat = bpy.data.materials.new(name="CharcoalMarble")
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
noise.inputs['Scale'].default_value = 6.0
noise.inputs['Detail'].default_value = 12.0
noise.inputs['Roughness'].default_value = 0.4

color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (-300, 0)
color_ramp.color_ramp.elements[0].color = (0.15, 0.15, 0.18, 1)
color_ramp.color_ramp.elements[1].color = (0.35, 0.35, 0.38, 1)

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-800, 0)

# Principled settings for marble
principled.inputs['Roughness'].default_value = 0.2
principled.inputs['Metallic'].default_value = 0.0

# Connect nodes
links = mat.node_tree.links
links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material
statue.data.materials.append(mat)

# Pedestal
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.3, location=(0, 0, 0.15))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal"
pedestal.data.materials.append(mat)
bpy.ops.object.shade_smooth()

# Camera
bpy.ops.object.camera_add(location=(2.8, -2.8, 1.8), rotation=(radians(70), 0, radians(45)))
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
area.data.size = 2.5

# Select statue to view
statue.select_set(True)
bpy.context.view_layer.objects.active = statue

print("✓ Heroic muscular statue created!")
