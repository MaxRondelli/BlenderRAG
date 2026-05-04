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

# Head
head = add_sphere("Head", (0, 0, 1.65), 0.13)

# Neck (slightly thicker)
neck = add_cylinder("Neck", (0, 0, 1.45), 0.06, 0.15)

# Torso (broader chest and shoulders)
chest = add_sphere("Chest", (0, 0, 1.3), 0.22)
chest.scale = (1.2, 0.75, 1.3)

belly = add_sphere("Belly", (0, 0, 1.05), 0.18)
belly.scale = (1.1, 0.75, 1.05)

# Broader shoulders
l_shoulder = add_sphere("L_Shoulder", (-0.28, 0, 1.32), 0.1)
r_shoulder = add_sphere("R_Shoulder", (0.28, 0, 1.32), 0.1)

# Thicker upper arms
l_upper_arm = add_cylinder("L_UpperArm", (-0.36, 0, 1.1), 0.065, 0.37, (0, radians(10), 0))
r_upper_arm = add_cylinder("R_UpperArm", (0.36, 0, 1.1), 0.065, 0.37, (0, radians(-10), 0))

# More muscular forearms
l_forearm = add_cylinder("L_Forearm", (-0.42, 0, 0.84), 0.055, 0.32, (0, radians(5), 0))
r_forearm = add_cylinder("R_Forearm", (0.42, 0, 0.84), 0.055, 0.32, (0, radians(-5), 0))

# Larger hands
l_hand = add_sphere("L_Hand", (-0.45, 0, 0.66), 0.065)
r_hand = add_sphere("R_Hand", (0.45, 0, 0.66), 0.065)

# More defined hips
hips = add_sphere("Hips", (0, 0, 0.9), 0.19)
hips.scale = (1.15, 0.75, 0.85)

# Thicker upper legs
l_upper_leg = add_cylinder("L_UpperLeg", (-0.12, 0, 0.65), 0.085, 0.42)
r_upper_leg = add_cylinder("R_UpperLeg", (0.12, 0, 0.65), 0.085, 0.42)

# More robust lower legs
l_lower_leg = add_cylinder("L_LowerLeg", (-0.12, 0, 0.3), 0.07, 0.37)
r_lower_leg = add_cylinder("R_LowerLeg", (0.12, 0, 0.3), 0.07, 0.37)

# Slightly larger feet
l_foot = add_sphere("L_Foot", (-0.12, 0.06, 0.08), 0.08)
l_foot.scale = (1.1, 1.6, 0.85)
r_foot = add_sphere("R_Foot", (0.12, 0.06, 0.08), 0.08)
r_foot.scale = (1.1, 1.6, 0.85)

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

# Create bronze patina material
mat = bpy.data.materials.new(name="Bronze_Patina")
mat.use_nodes = True
nodes = mat.node_tree.nodes
nodes.clear()

# Output node
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (600, 0)

# Main principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.location = (300, 0)

# Noise texture for patina variation
noise1 = nodes.new(type='ShaderNodeTexNoise')
noise1.location = (-800, 200)
noise1.inputs['Scale'].default_value = 8.0
noise1.inputs['Detail'].default_value = 15.0
noise1.inputs['Roughness'].default_value = 0.6

# Second noise for base bronze texture
noise2 = nodes.new(type='ShaderNodeTexNoise')
noise2.location = (-800, -200)
noise2.inputs['Scale'].default_value = 25.0
noise2.inputs['Detail'].default_value = 8.0
noise2.inputs['Roughness'].default_value = 0.4

# ColorRamp for patina (greenish accents)
color_ramp1 = nodes.new(type='ShaderNodeValToRGB')
color_ramp1.location = (-500, 200)
color_ramp1.color_ramp.elements[0].color = (0.15, 0.08, 0.05, 1)  # Dark bronze
color_ramp1.color_ramp.elements[1].color = (0.2, 0.35, 0.25, 1)   # Green patina

# ColorRamp for base bronze color
color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
color_ramp2.location = (-500, -200)
color_ramp2.color_ramp.elements[0].color = (0.25, 0.15, 0.08, 1)  # Medium bronze
color_ramp2.color_ramp.elements[1].color = (0.35, 0.22, 0.12, 1)  # Lighter bronze

# Mix node to combine patina and bronze
mix_color = nodes.new(type='ShaderNodeMix')
mix_color.location = (-200, 0)
mix_color.data_type = 'RGBA'
mix_color.blend_type = 'MIX'

# Texture coordinates
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-1000, 0)

# Principled BSDF settings for bronze
principled.inputs['Base Color'].default_value = (0.3, 0.18, 0.1, 1)
principled.inputs['Metallic'].default_value = 0.9
principled.inputs['Roughness'].default_value = 0.4

# Connect nodes
links = mat.node_tree.links
links.new(tex_coord.outputs['Generated'], noise1.inputs['Vector'])
links.new(tex_coord.outputs['Generated'], noise2.inputs['Vector'])
links.new(color_ramp2.outputs['Color'], mix_color.inputs['A'])
links.new(color_ramp1.outputs['Color'], mix_color.inputs['B'])
links.new(mix_color.outputs['Result'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material
statue.data.materials.append(mat)

# Pedestal
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.28, location=(0, 0, 0.14))
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
bpy.ops.object.light_add(type='SUN', location=(6, 6, 12))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (radians(40), 0, radians(50))

bpy.ops.object.light_add(type='AREA', location=(-3, -3, 3))
area = bpy.context.active_object
area.data.energy = 200
area.data.size = 2.5

# Select statue to view
statue.select_set(True)
bpy.context.view_layer.objects.active = statue

print("✓ Heroic bronze statue created!")


