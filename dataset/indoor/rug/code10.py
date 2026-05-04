import bpy
import bmesh
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
length = 3.0  # meters
width = 2.0   # meters
thickness = 0.025
pattern_circles = 8

# Create base rug mesh
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
rug = bpy.context.active_object
rug.name = "Persian_Rug"

# Scale the rug
rug.scale = (width, length, 1)
bpy.ops.object.transform_apply(scale=True)

# Add subdivisions for realism - RIDOTTO per evitare crash
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=5)  # RIDOTTO da 150 a 5
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier for thickness
solidify = rug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = thickness
solidify.offset = 0

# Add Displacement modifier for fiber texture
disp = rug.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.008

# Create fiber texture
texture_fibers = bpy.data.textures.new('Texture_Fibers', type='VORONOI')
texture_fibers.noise_scale = 3.0
texture_fibers.distance_metric = 'DISTANCE'
disp.texture = texture_fibers

# Create Persian pattern materials
def create_persian_material(name, base_color, roughness=0.8):
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
    
    # Texture Coordinate
    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-800, 0)
    
    # Wave texture for circular patterns
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-600, 200)
    wave.wave_profile = 'TRI'
    wave.inputs['Scale'].default_value = 8.0
    wave.inputs['Distortion'].default_value = 2.0
    wave.inputs['Detail'].default_value = 3.0
    
    # Noise texture for variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-600, -100)
    noise.inputs['Scale'].default_value = 80.0
    noise.inputs['Detail'].default_value = 10.0
    noise.inputs['Roughness'].default_value = 0.7
    
    # Color Ramp for pattern control
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-400, 200)
    color_ramp.color_ramp.elements[0].position = 0.3
    color_ramp.color_ramp.elements[1].position = 0.7
    
    # Mix node for color variation - CORRETTO
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (-200, 0)
    mix.blend_type = 'MIX'
    mix.inputs['Color1'].default_value = base_color  # CORRETTO: era inputs[6]
    darker_color = (base_color[0] * 0.6, base_color[1] * 0.6, base_color[2] * 0.6, 1.0)
    mix.inputs['Color2'].default_value = darker_color  # CORRETTO: era inputs[7]
    
    # Voronoi for fiber texture
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.location = (-400, -300)
    voronoi.inputs['Scale'].default_value = 250.0
    
    # Bump for surface detail
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (200, -200)
    bump.inputs['Strength'].default_value = 0.4
    
    # Math node for combining textures
    math_multiply = nodes.new(type='ShaderNodeMath')
    math_multiply.location = (-200, 200)
    math_multiply.operation = 'MULTIPLY'
    
    # Connections - CORRETTI
    links = mat.node_tree.links
    links.new(coord.outputs['Object'], wave.inputs['Vector'])
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(wave.outputs['Color'], color_ramp.inputs['Fac'])  # CORRETTO
    links.new(color_ramp.outputs['Color'], math_multiply.inputs[0])
    links.new(noise.outputs['Fac'], math_multiply.inputs[1])  # CORRETTO
    links.new(math_multiply.outputs['Value'], mix.inputs['Fac'])  # CORRETTO
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])  # CORRETTO
    
    if 'Distance' in voronoi.outputs:
        links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    else:
        links.new(voronoi.outputs['Fac'], bump.inputs['Height'])
    
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create three Persian-style materials
mat_burgundy = create_persian_material("Persian_Burgundy", (0.6, 0.15, 0.15, 1.0), 0.85)
mat_gold = create_persian_material("Persian_Gold", (0.8, 0.6, 0.2, 1.0), 0.75)
mat_cream = create_persian_material("Persian_Cream", (0.9, 0.85, 0.7, 1.0), 0.8)

# Assign materials to rug
rug.data.materials.append(mat_burgundy)
rug.data.materials.append(mat_gold)
rug.data.materials.append(mat_cream)

# Create circular pattern by assigning materials based on distance from centers
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Define circle centers for pattern
circle_centers = [
    (-0.5, -0.8, 0), (0.5, -0.8, 0),
    (-0.8, 0, 0), (0, 0, 0), (0.8, 0, 0),
    (-0.5, 0.8, 0), (0.5, 0.8, 0)
]

for face in rug.data.polygons:
    # Calculate face center
    center_x = sum([rug.data.vertices[v].co.x for v in face.vertices]) / len(face.vertices)
    center_y = sum([rug.data.vertices[v].co.y for v in face.vertices]) / len(face.vertices)
    
    # Find nearest circle center
    min_dist = float('inf')
    nearest_circle = 0
    
    for i, circle_center in enumerate(circle_centers):
        dist = math.sqrt(
            (center_x - circle_center[0])**2 + 
            (center_y - circle_center[1])**2
        )
        if dist < min_dist:
            min_dist = dist
            nearest_circle = i
    
    # Assign material based on distance and circle
    if min_dist < 0.3:
        face.material_index = 1  # Gold for circle centers
    elif min_dist < 0.6:
        face.material_index = 0  # Burgundy for middle rings
    else:
        face.material_index = 2  # Cream for background

# Add Subdivision Surface modifier for smoother appearance
subsurf = rug.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Add lighting and camera
bpy.ops.object.light_add(type='SUN', location=(4, -3, 8))
sun_light = bpy.context.active_object
sun_light.data.energy = 4.0
sun_light.rotation_euler = (math.radians(45), math.radians(30), 0)

bpy.ops.object.camera_add(location=(2.5, -3.5, 2.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(35))
bpy.context.scene.camera = camera

# Set render engine to Cycles
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256

print("=" * 50)
print("Persian-style rug created successfully!")
print("=" * 50)
print("Dimensions: {} x {} meters".format(width, length))
print("Pattern: Circular geometric design")
print("Colors: Burgundy, Gold, and Cream")
print("")
print("INSTRUCTIONS:")
print("1. Press Z and select 'Material Preview' or 'Rendered'")
print("2. Press F12 to render the final image")
print("3. Modify parameters at the script beginning")
print("=" * 50)