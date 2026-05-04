import bpy
import bmesh
import math
import random

# Clean the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
lunghezza = 3.0  # meters
larghezza = 2.0  # meters
numero_strisce = 8  # Reduced for more luxurious look
spessore = 0.035  # Increased thickness for plush feel

# Create base rug mesh
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
tappeto = bpy.context.active_object
tappeto.name = "Persian_Luxury_Rug"

# Scale the rug
tappeto.scale = (larghezza, lunghezza, 1)
bpy.ops.object.transform_apply(scale=True)

# Add subdivisions for realism
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=120)
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier for thickness
solidify = tappeto.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = spessore
solidify.offset = 0

# Add Displacement modifier for pile texture
disp = tappeto.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.012  # Increased for more pronounced texture

# Create texture for displacement
texture_fibre = bpy.data.textures.new('Texture_Fibre', type='VORONOI')
texture_fibre.noise_scale = 1.5
texture_fibre.distance_metric = 'DISTANCE'
disp.texture = texture_fibre

# Create materials for luxury stripes
def crea_materiale_lusso(nome, colore_base, roughness=0.6):
    mat = bpy.data.materials.new(name=nome)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Base Color'].default_value = colore_base
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = 0.02  # Slight metallic sheen
    
    # Texture Coordinate
    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-600, 0)
    
    # Noise texture for color variation
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 180.0
    noise.inputs['Detail'].default_value = 12.0
    noise.inputs['Roughness'].default_value = 0.6
    
    # ColorRamp for controlling variation
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 100)
    color_ramp.color_ramp.elements[0].position = 0.35
    color_ramp.color_ramp.elements[1].position = 0.65
    
    # Mix node for color blending
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (0, 0)
    mix.blend_type = 'MIX'
    mix.inputs['Color1'].default_value = colore_base
    colore_highlight = (colore_base[0] * 1.2, colore_base[1] * 1.1, colore_base[2] * 0.9, 1.0)
    mix.inputs['Color2'].default_value = colore_highlight
    
    # Voronoi for fiber texture
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.location = (-400, -200)
    voronoi.inputs['Scale'].default_value = 250.0
    
    # Bump for surface detail
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.5  # Enhanced bump
    
    # Wave texture for Persian pattern
    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-400, -400)
    wave.inputs['Scale'].default_value = 25.0
    wave.inputs['Distortion'].default_value = 2.0
    wave.wave_profile = 'TRI'
    
    # Links
    links = mat.node_tree.links
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(coord.outputs['Object'], wave.inputs['Vector'])
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix.inputs['Fac'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    
    if 'Distance' in voronoi.outputs:
        links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    elif 'Fac' in voronoi.outputs:
        links.new(voronoi.outputs['Fac'], bump.inputs['Height'])
    
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create gold and burgundy materials
mat_oro = crea_materiale_lusso("Striscia_Oro", (0.8, 0.6, 0.2, 1.0), 0.5)
mat_bordeaux = crea_materiale_lusso("Striscia_Bordeaux", (0.5, 0.1, 0.15, 1.0), 0.7)

# Assign materials to rug
if len(tappeto.data.materials) == 0:
    tappeto.data.materials.append(mat_oro)
    tappeto.data.materials.append(mat_bordeaux)
else:
    tappeto.data.materials[0] = mat_oro
    if len(tappeto.data.materials) < 2:
        tappeto.data.materials.append(mat_bordeaux)
    else:
        tappeto.data.materials[1] = mat_bordeaux

# Create stripes using face material assignment
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Calculate stripe assignment
larghezza_striscia = lunghezza / numero_strisce

for face in tappeto.data.polygons:
    # Calculate face center
    centro_y = sum([tappeto.data.vertices[v].co.y for v in face.vertices]) / len(face.vertices)
    
    # Determine stripe membership
    posizione_normalizzata = (centro_y + lunghezza/2)
    indice_striscia = int(posizione_normalizzata / larghezza_striscia)
    
    # Alternate between gold (0) and burgundy (1)
    if indice_striscia % 2 == 0:
        face.material_index = 0  # Gold
    else:
        face.material_index = 1  # Burgundy

# Add Subdivision Surface modifier for luxury smoothness
subsurf = tappeto.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 3  # Higher subdivision for luxury feel
subsurf.render_levels = 4

# Add slight bevel for soft edges
bevel = tappeto.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.008
bevel.segments = 2

# Setup lighting and camera
bpy.ops.object.light_add(type='SUN', location=(4, 4, 8))
luce = bpy.context.active_object
luce.data.energy = 2.5

bpy.ops.object.camera_add(location=(2.5, -3.5, 2.8))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(68), 0, math.radians(35))
bpy.context.scene.camera = camera

# Set rendering engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 150

print("=" * 50)
print("Luxury Persian-style rug created successfully!")
print("=" * 50)
print("Dimensions: {} x {} meters".format(larghezza, lunghezza))
print("Stripes: {} (alternating gold and burgundy)".format(numero_strisce))
print("")
print("FEATURES:")
print("- Enhanced pile height and texture")
print("- Warm earth tone colors (gold/burgundy)")
print("- Luxury material properties with metallic sheen")
print("- Soft beveled edges")
print("=" * 50)