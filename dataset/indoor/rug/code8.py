import bpy
import bmesh
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
diameter = 2.5  # meters
thickness = 0.03
pattern_rings = 6

# Create base circular rug mesh
bpy.ops.mesh.primitive_circle_add(vertices=64, radius=diameter/2, location=(0, 0, 0))
rug = bpy.context.active_object
rug.name = "Persian_Rug"

# Fill the circle - RIDOTTO per evitare crash
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.fill()
bpy.ops.mesh.subdivide(number_cuts=5)  # RIDOTTO da 8+8 a 5
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier for thickness
solidify = rug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = thickness
solidify.offset = 0

# Add Displacement for texture
disp = rug.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.008

# Create displacement texture
texture_pattern = bpy.data.textures.new('Texture_Pattern', type='VORONOI')
texture_pattern.noise_scale = 3.0
texture_pattern.distance_metric = 'DISTANCE'
disp.texture = texture_pattern

# Create Persian rug material
def create_persian_material(name, base_color, accent_color, roughness=0.8):
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
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['IOR'].default_value = 1.2
    
    # Texture Coordinate
    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-800, 0)
    
    # Mapping for scaling
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (3.0, 3.0, 3.0)
    
    # Voronoi texture for main pattern
    voronoi1 = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi1.location = (-400, 200)
    voronoi1.inputs['Scale'].default_value = 8.0
    
    # Second Voronoi for complexity
    voronoi2 = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi2.location = (-400, -100)
    voronoi2.inputs['Scale'].default_value = 20.0
    
    # Wave texture for radial pattern
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-400, 0)
    wave.wave_type = 'RINGS'
    wave.inputs['Scale'].default_value = 15.0
    wave.inputs['Distortion'].default_value = 2.0
    
    # Color ramp for pattern control
    color_ramp1 = nodes.new(type='ShaderNodeValToRGB')
    color_ramp1.location = (-200, 200)
    color_ramp1.color_ramp.elements[0].position = 0.3
    color_ramp1.color_ramp.elements[1].position = 0.7
    color_ramp1.color_ramp.elements[0].color = base_color
    color_ramp1.color_ramp.elements[1].color = accent_color
    
    # Color ramp for wave
    color_ramp2 = nodes.new(type='ShaderNodeValToRGB')
    color_ramp2.location = (-200, 0)
    color_ramp2.color_ramp.elements[0].position = 0.4
    color_ramp2.color_ramp.elements[1].position = 0.6
    
    # Mix nodes for combining patterns - CORRETTI
    mix1 = nodes.new(type='ShaderNodeMixRGB')
    mix1.location = (0, 100)
    mix1.blend_type = 'MULTIPLY'
    mix1.inputs['Fac'].default_value = 0.7  # CORRETTO
    
    mix2 = nodes.new(type='ShaderNodeMixRGB')
    mix2.location = (200, 0)
    mix2.blend_type = 'OVERLAY'
    mix2.inputs['Fac'].default_value = 0.5  # CORRETTO
    
    # Noise for micro details
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, -300)
    noise.inputs['Scale'].default_value = 80.0
    noise.inputs['Detail'].default_value = 8.0
    
    # Bump for surface detail
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (200, -200)
    bump.inputs['Strength'].default_value = 0.5
    
    # Connect nodes - CORRETTI
    links = mat.node_tree.links
    links.new(coord.outputs['UV'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], voronoi1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], voronoi2.inputs['Vector'])
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    links.new(voronoi1.outputs['Distance'], color_ramp1.inputs['Fac'])
    links.new(wave.outputs['Fac'], color_ramp2.inputs['Fac'])
    
    # CORRETTO: usa 'Color1' e 'Color2' invece di 6 e 7
    links.new(color_ramp1.outputs['Color'], mix1.inputs['Color1'])
    links.new(voronoi2.outputs['Distance'], mix1.inputs['Color2'])
    
    links.new(mix1.outputs['Color'], mix2.inputs['Color1'])
    links.new(color_ramp2.outputs['Color'], mix2.inputs['Color2'])
    
    links.new(mix2.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create Persian-style material with earth tones
mat_persian = create_persian_material("Persian_Pattern", 
                                     (0.6, 0.3, 0.15, 1.0),  # Deep brown base
                                     (0.8, 0.6, 0.2, 1.0))   # Golden accent

# Assign material to rug
if len(rug.data.materials) == 0:
    rug.data.materials.append(mat_persian)
else:
    rug.data.materials[0] = mat_persian

# Add Subdivision Surface for smoothness
subsurf = rug.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Add slight random deformation for realism
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.vertex_random(offset=0.01)
bpy.ops.object.mode_set(mode='OBJECT')

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(4, 4, 8))
sun = bpy.context.active_object
sun.data.energy = 2.5
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add area light for softer shadows
bpy.ops.object.light_add(type='AREA', location=(-2, -2, 5))
area_light = bpy.context.active_object
area_light.data.energy = 80
area_light.data.size = 3.0

# Position camera
bpy.ops.object.camera_add(location=(2.5, -3.5, 3.0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(55), 0, math.radians(35))
bpy.context.scene.camera = camera

# Set render engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256

print("=" * 50)
print("Persian-style circular rug created successfully!")
print("=" * 50)
print("Diameter: {} meters".format(diameter))
print("Pattern: Ornate floral with earth tones")
print("")
print("INSTRUCTIONS:")
print("1. Switch to Material Preview or Rendered view")
print("2. Press F12 to render")
print("3. Modify parameters at the top of the script")
print("=" * 50)