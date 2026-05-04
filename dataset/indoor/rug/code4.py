import bpy
import bmesh
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rug parameters
radius = 1.5  # meters
thickness = 0.02
num_rings = 8

# Create the base mesh of the rug - OPTIMIZED
bpy.ops.mesh.primitive_circle_add(vertices=32, radius=radius, location=(0, 0, 0))
rug = bpy.context.active_object
rug.name = "Mandala_Rug"

# Fill and subdivide - REDUCED subdivision
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.fill()
bpy.ops.mesh.subdivide(number_cuts=5)  # REDUCED from 10 to 5
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier for thickness
solidify = rug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = thickness
solidify.offset = 0

# Add Displacement modifier for fiber texture
disp = rug.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.008

# Create texture for displacement (simulate fibers)
texture_fibers = bpy.data.textures.new('Texture_Fibers', type='VORONOI')
texture_fibers.noise_scale = 1.5
texture_fibers.distance_metric = 'DISTANCE'
disp.texture = texture_fibers

# Create materials for the rings (compatible version)
def create_ring_material_compatible(name, base_color, roughness=0.8):
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
    noise.inputs['Scale'].default_value = 120.0
    noise.inputs['Detail'].default_value = 12.0
    
    # Color Ramp to control variation
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 100)
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].position = 0.6
    
    # MixRGB to vary color
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (0, 0)
    mix.blend_type = 'MIX'
    mix.inputs['Color1'].default_value = base_color
    dark_color = (base_color[0] * 0.7, base_color[1] * 0.7, base_color[2] * 0.7, 1.0)
    mix.inputs['Color2'].default_value = dark_color
    
    # Voronoi texture for fibers
    voronoi = nodes.new(type='ShaderNodeTexVoronoi')
    voronoi.location = (-400, -200)
    voronoi.inputs['Scale'].default_value = 180.0
    
    # Bump for micro-details
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.4
    
    # Connections
    links = mat.node_tree.links
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(coord.outputs['Object'], voronoi.inputs['Vector'])
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix.inputs['Fac'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Connect Voronoi to Bump
    if 'Distance' in voronoi.outputs:
        links.new(voronoi.outputs['Distance'], bump.inputs['Height'])
    elif 'Fac' in voronoi.outputs:
        links.new(voronoi.outputs['Fac'], bump.inputs['Height'])
    
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create materials in earth tones
mat_terracotta = create_ring_material_compatible("Ring_Terracotta", (0.7, 0.3, 0.2, 1.0), 0.85)
mat_cream = create_ring_material_compatible("Ring_Cream", (0.9, 0.85, 0.7, 1.0), 0.75)
mat_brown = create_ring_material_compatible("Ring_Brown", (0.4, 0.25, 0.15, 1.0), 0.9)

# Assign materials to the rug
materials = [mat_terracotta, mat_cream, mat_brown]
for mat in materials:
    rug.data.materials.append(mat)

# Create concentric rings using material assignment
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Calculate which faces belong to which ring
ring_width = radius / num_rings

for face in rug.data.polygons:
    # Calculate face center
    center_x = sum([rug.data.vertices[v].co.x for v in face.vertices]) / len(face.vertices)
    center_y = sum([rug.data.vertices[v].co.y for v in face.vertices]) / len(face.vertices)
    
    # Calculate distance from center
    distance_from_center = math.sqrt(center_x**2 + center_y**2)
    
    # Determine which ring this face belongs to
    ring_index = int(distance_from_center / ring_width)
    
    # Cycle through the three materials
    material_index = ring_index % 3
    face.material_index = material_index

# Add Subdivision Surface modifier for realism
subsurf = rug.modifiers.new(name="Subdivision", type="SUBSURF")
subsurf.levels = 1
subsurf.render_levels = 2

# Position light and camera for better visualization
bpy.ops.object.light_add(type='SUN', location=(4, 4, 8))
light = bpy.context.active_object
light.data.energy = 4.0

bpy.ops.object.camera_add(location=(2.5, -3.5, 3.0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(35))
bpy.context.scene.camera = camera

# Set rendering engine to Cycles for better quality
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("Mandala rug created successfully!")
print("=" * 50)
print("Radius: {} meters".format(radius))
print("Rings: {} (in earth tones)".format(num_rings))
print("")
print("INSTRUCTIONS:")
print("1. Press Z in viewport and select 'Material Preview' or 'Rendered'")
print("2. To render final image: press F12")
print("3. You can modify parameters at the beginning of the script")
print("=" * 50)