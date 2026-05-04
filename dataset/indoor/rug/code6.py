import bpy
import bmesh
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
radius = 1.5  # meters
num_rings = 8
thickness = 0.025

# Create the base mesh for the rug
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=radius, location=(0, 0, 0))
rug = bpy.context.active_object
rug.name = "Braided_Rug"

# Fill the circle - REDUCED SUBDIVISION
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.fill()
bpy.ops.mesh.subdivide(number_cuts=5)  # REDUCED from 50 to 5
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier for thickness
solidify = rug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = thickness
solidify.offset = 0

# Add Displacement modifier for braided texture
disp = rug.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.008

# Create texture for displacement (braided pattern)
texture_braid = bpy.data.textures.new('Texture_Braid', type='VORONOI')
texture_braid.noise_scale = 3.5
texture_braid.distance_metric = 'DISTANCE'
disp.texture = texture_braid

# Create materials for the braided rings
def create_braided_material(name, base_color, roughness=0.8):
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
    
    # Wave texture for braided pattern
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-400, 100)
    wave.inputs['Scale'].default_value = 25.0
    wave.inputs['Distortion'].default_value = 2.0
    wave.wave_profile = 'TRI'
    
    # Color Ramp for pattern control
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 100)
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].position = 0.6
    
    # Mix node for color variation - FIXED
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (0, 0)
    mix.blend_type = 'MIX'
    mix.inputs['Color1'].default_value = base_color  # FIXED: was inputs[6]
    darker_color = (base_color[0] * 0.7, base_color[1] * 0.7, base_color[2] * 0.7, 1.0)
    mix.inputs['Color2'].default_value = darker_color  # FIXED: was inputs[7]
    
    # Noise texture for fiber variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, -200)
    noise.inputs['Scale'].default_value = 180.0
    
    # Bump for surface detail
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.4
    
    # Connections
    links = mat.node_tree.links
    links.new(coord.outputs['Generated'], wave.inputs['Vector'])
    links.new(coord.outputs['Generated'], noise.inputs['Vector'])
    links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix.inputs['Fac'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create earth tone materials
mat_brown = create_braided_material("Ring_Brown", (0.4, 0.25, 0.15, 1.0), 0.85)
mat_tan = create_braided_material("Ring_Tan", (0.6, 0.45, 0.3, 1.0), 0.8)
mat_orange = create_braided_material("Ring_Orange", (0.7, 0.4, 0.2, 1.0), 0.8)

# Assign materials to the rug
materials = [mat_brown, mat_tan, mat_orange]
for mat in materials:
    rug.data.materials.append(mat)

# Create concentric rings using material assignment
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Calculate ring widths and assign materials
ring_width = radius / num_rings

for face in rug.data.polygons:
    # Calculate distance from center for each face
    center_x = sum([rug.data.vertices[v].co.x for v in face.vertices]) / len(face.vertices)
    center_y = sum([rug.data.vertices[v].co.y for v in face.vertices]) / len(face.vertices)
    distance_from_center = math.sqrt(center_x**2 + center_y**2)
    
    # Determine which ring this face belongs to
    ring_index = int(distance_from_center / ring_width)
    ring_index = min(ring_index, num_rings - 1)
    
    # Assign material based on ring (cycle through the 3 materials)
    face.material_index = ring_index % len(materials)

# Add Subdivision Surface modifier for smoother appearance
subsurf = rug.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Add lighting and camera
bpy.ops.object.light_add(type='SUN', location=(4, 4, 8))
light = bpy.context.active_object
light.data.energy = 3.5

bpy.ops.object.camera_add(location=(2.5, -3, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(35))
bpy.context.scene.camera = camera

# Set rendering engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("Circular braided rug created successfully!")
print("=" * 50)
print("Radius: {} meters".format(radius))
print("Rings: {} (earth tone colors)".format(num_rings))
print("")
print("INSTRUCTIONS:")
print("1. Press Z in viewport and select 'Material Preview' or 'Rendered'")
print("2. To render final image: press F12")
print("3. You can modify parameters at the beginning of the script")
print("=" * 50)