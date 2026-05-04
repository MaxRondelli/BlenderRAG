import bpy
import bmesh
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
diameter = 2.5  # meters
number_stripes = 12
thickness = 0.04

# Create base mesh - circular rug (SIMPLER APPROACH)
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=diameter/2, location=(0, 0, 0))
rug = bpy.context.active_object
rug.name = "Circular_Braided_Rug"

# Fill and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.fill()
bpy.ops.mesh.subdivide(number_cuts=10)
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier for thickness
solidify = rug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = thickness
solidify.offset = 0

# Add Displacement modifier for braided texture
disp = rug.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.008

# Create texture for displacement (simulates braided fibers)
texture_braided = bpy.data.textures.new('Texture_Braided', type='VORONOI')
texture_braided.noise_scale = 3.0
texture_braided.distance_metric = 'DISTANCE'
disp.texture = texture_braided

# Create materials for stripes (compatible version)
def create_stripe_material_compatible(name, base_color, roughness=0.8):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF node
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    
    # Texture Coordinate node
    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-600, 0)
    
    # Noise texture for color variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 200.0
    noise.inputs['Detail'].default_value = 12.0
    
    # Color Ramp for controlling variation
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 100)
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].position = 0.6
    
    # MixRGB for color variation
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (0, 0)
    mix.blend_type = 'MIX'
    mix.inputs['Color1'].default_value = base_color
    darker_color = (base_color[0] * 0.7, base_color[1] * 0.7, base_color[2] * 0.7, 1.0)
    mix.inputs['Color2'].default_value = darker_color
    
    # Wave texture for braided pattern
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-400, -200)
    wave.inputs['Scale'].default_value = 180.0
    wave.wave_profile = 'SAW'
    
    # Bump for micro-details
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.4
    
    # Links
    links = mat.node_tree.links
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(coord.outputs['Object'], wave.inputs['Vector'])
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix.inputs['Fac'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(wave.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create brown and beige materials
mat_brown = create_stripe_material_compatible("Stripe_Brown", (0.4, 0.25, 0.1, 1.0), 0.85)
mat_beige = create_stripe_material_compatible("Stripe_Beige", (0.7, 0.6, 0.45, 1.0), 0.8)

# Assign materials to the rug
if len(rug.data.materials) == 0:
    rug.data.materials.append(mat_brown)
    rug.data.materials.append(mat_beige)
else:
    rug.data.materials[0] = mat_brown
    if len(rug.data.materials) < 2:
        rug.data.materials.append(mat_beige)
    else:
        rug.data.materials[1] = mat_beige

# Create circular stripes using material assignment
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Calculate which faces belong to which stripe based on distance from center
max_radius = diameter / 2
stripe_width = max_radius / number_stripes

for face in rug.data.polygons:
    # Calculate face center
    center_x = sum([rug.data.vertices[v].co.x for v in face.vertices]) / len(face.vertices)
    center_y = sum([rug.data.vertices[v].co.y for v in face.vertices]) / len(face.vertices)
    
    # Calculate distance from center
    distance = math.sqrt(center_x**2 + center_y**2)
    
    # Determine which stripe this face belongs to
    stripe_index = int(distance / stripe_width)
    
    # Alternate between brown (0) and beige (1)
    if stripe_index % 2 == 0:
        face.material_index = 0  # Brown
    else:
        face.material_index = 1  # Beige

# Add Subdivision Surface modifier for smoother appearance
subsurf = rug.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 1
subsurf.render_levels = 2

# Position light and camera for better visualization
bpy.ops.object.light_add(type='SUN', location=(4, -3, 8))
light = bpy.context.active_object
light.data.energy = 4.0

bpy.ops.object.camera_add(location=(2, -3, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(30))
bpy.context.scene.camera = camera

# Set render engine to Cycles for better quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("Circular braided rug created successfully!")
print("=" * 50)
print("Diameter: {} meters".format(diameter))
print("Stripes: {} (alternating brown and beige)".format(number_stripes))
print("")
print("INSTRUCTIONS:")
print("1. Press Z in viewport and select 'Material Preview' or 'Rendered'")
print("2. To render final image: press F12")
print("3. You can modify parameters at the beginning of the script")
print("=" * 50)