import bpy
import bmesh
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for twin peaks
bpy.ops.mesh.primitive_plane_add(size=22, location=(0, 0, 0))
twin_peaks = bpy.context.active_object
twin_peaks.name = "TwinPeaks"

# Enter edit mode and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=10)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = twin_peaks.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Define two peak centers
peak1 = (-3, 0, 7.5)
peak2 = (3, 0, 6.8)

# Create twin peaks
for vert in bm.verts:
    x, y = vert.co.x, vert.co.y
    
    # Distance to each peak
    dist1 = math.sqrt((x - peak1[0])**2 + (y - peak1[1])**2)
    dist2 = math.sqrt((x - peak2[0])**2 + (y - peak2[1])**2)
    
    # Height from peak 1
    height1 = 0
    if dist1 < 6:
        height1 = (6 - dist1) * (peak1[2] / 6)
    
    # Height from peak 2
    height2 = 0
    if dist2 < 5.5:
        height2 = (5.5 - dist2) * (peak2[2] / 5.5)
    
    # Take maximum height (creates two distinct peaks)
    height = max(height1, height2)
    height += random.uniform(-0.25, 0.25)
    
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = twin_peaks.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add displacement
displace = twin_peaks.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 1.1
displace.mid_level = 0.5

tex = bpy.data.textures.new("TwinPeaksTexture", type='CLOUDS')
tex.noise_scale = 0.85
tex.noise_depth = 7
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create granite-like material
mat = bpy.data.materials.new(name="TwinPeaksMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
voronoi = nodes.new('ShaderNodeTexVoronoi')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')
mix = nodes.new('ShaderNodeMix')
mix.data_type = 'RGBA'

# Voronoi for granite pattern
voronoi.inputs['Scale'].default_value = 8.0

# Noise for variation
noise.inputs['Scale'].default_value = 5.0

links.new(voronoi.outputs['Distance'], mix.inputs['A'])
links.new(noise.outputs['Fac'], mix.inputs['B'])
links.new(mix.outputs['Result'], color_ramp.inputs['Fac'])

# Granite colors
color_ramp.color_ramp.elements[0].color = (0.38, 0.36, 0.34, 1)  # Medium gray
color_ramp.color_ramp.elements[1].color = (0.55, 0.52, 0.48, 1)  # Light gray

bsdf.inputs['Roughness'].default_value = 0.88

links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

twin_peaks.data.materials.append(mat)

# Add camera positioned to see both peaks
bpy.ops.object.camera_add(location=(0, -22, 10))
camera = bpy.context.active_object
camera.rotation_euler = (1.2, 0, 1.5708)  # Facing the twin peaks
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(10, -12, 16))
sun = bpy.context.active_object
sun.data.energy = 3.6
sun.rotation_euler = (0.85, 0.4, 0.5)

print("Twin Peaks created successfully!")