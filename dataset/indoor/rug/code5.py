import bpy
import bmesh
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
length = 3.0  # meters
width = 2.0  # meters
thickness = 0.03

# Create the base mesh of the rug
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
rug = bpy.context.active_object
rug.name = "Persian_Rug"

# Scale the rug
rug.scale = (width, length, 1)
bpy.ops.object.transform_apply(scale=True)

# Add subdivisions for realism
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=120)
bpy.ops.object.mode_set(mode='OBJECT')

# Add a Solidify modifier for thickness
solidify = rug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = thickness
solidify.offset = 0

# Add a Displacement modifier for fiber texture
disp = rug.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.008

# Create texture for displacement (simulates fibers)
texture_fibers = bpy.data.textures.new('Texture_Fibers', type='VORONOI')
texture_fibers.noise_scale = 3.0
texture_fibers.distance_metric = 'DISTANCE'
disp.texture = texture_fibers

# Create Persian rug material
def create_persian_material(name):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (400, 0)
    bsdf.inputs['Roughness'].default_value = 0.85
    
    # Texture Coordinates
    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-800, 0)
    
    # Main pattern using Wave texture
    wave1 = nodes.new(type='ShaderNodeTexWave')
    wave1.location = (-600, 200)
    wave1.wave_type = 'BANDS'
    wave1.wave_profile = 'TRI'
    wave1.inputs['Scale'].default_value = 8.0
    wave1.inputs['Distortion'].default_value = 2.0
    
    # Secondary pattern using another Wave texture
    wave2 = nodes.new(type='ShaderNodeTexWave')
    wave2.location = (-600, -200)
    wave2.wave_type = 'BANDS'
    wave2.wave_profile = 'SAW'
    wave2.inputs['Scale'].default_value = 12.0
    wave2.inputs['Distortion'].default_value = 1.5
    
    # Combine patterns with Math node
    math_mult = nodes.new(type='ShaderNodeMath')
    math_mult.location = (-400, 0)
    math_mult.operation = 'MULTIPLY'
    
    # Color Ramp for pattern colors
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 0)
    
    # Set up color stops for Persian colors
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = (0.5, 0.1, 0.1, 1.0)  # Burgundy
    color_ramp.color_ramp.elements[1].position = 0.5
    color_ramp.color_ramp.elements[1].color = (0.8, 0.6, 0.2, 1.0)  # Gold
    
    # Add third color stop
    color_ramp.color_ramp.elements.new(0.8)
    color_ramp.color_ramp.elements[2].color = (0.9, 0.85, 0.7, 1.0)  # Cream
    
    # Noise for subtle variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-600, 0)
    noise.inputs['Scale'].default_value = 80.0
    noise.inputs['Detail'].default_value = 8.0
    
    # Mix noise with pattern
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (0, 0)
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.3
    
    # Voronoi for fiber texture
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.location = (-400, -400)
    voronoi.inputs['Scale'].default_value = 250.0
    
    # Bump for surface detail
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (200, -200)
    bump.inputs['Strength'].default_value = 0.5
    
    # Links
    links = mat.node_tree.links
    links.new(coord.outputs['Generated'], wave1.inputs['Vector'])
    links.new(coord.outputs['Generated'], wave2.inputs['Vector'])
    links.new(coord.outputs['Generated'], noise.inputs['Vector'])
    links.new(coord.outputs['Generated'], voronoi.inputs['Vector'])
    
    links.new(wave1.outputs['Color'], math_mult.inputs[0])
    links.new(wave2.outputs['Color'], math_mult.inputs[1])
    links.new(math_mult.outputs['Value'], color_ramp.inputs['Fac'])
    
    links.new(color_ramp.outputs['Color'], mix.inputs['Color1'])
    links.new(noise.outputs['Color'], mix.inputs['Color2'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    
    if 'Distance' in voronoi.outputs:
        links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    else:
        links.new(voronoi.outputs['Color'], bump.inputs['Height'])
    
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create and assign the Persian material
persian_mat = create_persian_material("Persian_Pattern")
if len(rug.data.materials) == 0:
    rug.data.materials.append(persian_mat)
else:
    rug.data.materials[0] = persian_mat

# Add Subdivision Surface modifier for smoothness
subsurf = rug.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Position light and camera
bpy.ops.object.light_add(type='SUN', location=(4, 4, 8))
light = bpy.context.active_object
light.data.energy = 4.0

bpy.ops.object.camera_add(location=(2.5, -3.5, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(35))
bpy.context.scene.camera = camera

# Set render engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("Persian rug created successfully!")
print("=" * 50)
print("Dimensions: {} x {} meters".format(width, length))
print("Pattern: Ornate geometric design")
print("Colors: Burgundy, Gold, and Cream")
print("")
print("INSTRUCTIONS:")
print("1. Press Z in viewport and select 'Material Preview' or 'Rendered'")
print("2. To render final image: press F12")
print("3. You can modify parameters at the beginning of the script")
print("=" * 50)