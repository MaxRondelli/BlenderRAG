import bpy
import bmesh
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for badlands
bpy.ops.mesh.primitive_plane_add(size=26, location=(0, 0, 0))
badlands = bpy.context.active_object
badlands.name = "ErodedBadlands"

# Enter edit mode and subdivide heavily for detail
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=13)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = badlands.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create eroded badlands terrain with multiple small peaks
for vert in bm.verts:
    x, y = vert.co.x, vert.co.y
    
    # Multiple overlapping noise functions for complexity
    height = 0
    height += abs(math.sin(x * 0.4) * math.cos(y * 0.3)) * 3
    height += abs(math.sin(x * 0.6 + 1) * math.sin(y * 0.5)) * 2
    height += abs(math.cos(x * 0.3) * math.sin(y * 0.4 + 2)) * 2.5
    
    # Add sharp erosion features
    height += random.uniform(-0.5, 0.5)
    
    # Create some flat areas (erosion plateaus)
    if height > 4:
        height = 4 + (height - 4) * 0.3
    
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = badlands.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 1

# Add strong displacement for erosion patterns
displace = badlands.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 2.0
displace.mid_level = 0.5

tex = bpy.data.textures.new("BadlandsTexture", type='VORONOI')
tex.noise_scale = 2.0
tex.distance_metric = 'DISTANCE'
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create layered sediment material
mat = bpy.data.materials.new(name="BadlandsMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
coord = nodes.new('ShaderNodeTexCoord')
separate_xyz = nodes.new('ShaderNodeSeparateXYZ')
color_ramp = nodes.new('ShaderNodeValToRGB')
noise = nodes.new('ShaderNodeTexNoise')
wave = nodes.new('ShaderNodeTexWave')

# Wave texture for sediment layers
wave.wave_type = 'BANDS'
wave.inputs['Scale'].default_value = 15.0
wave.inputs['Distortion'].default_value = 3.0

# Noise for variation
noise.inputs['Scale'].default_value = 7.0

# Use Z coordinate for layering effect
links.new(coord.outputs['Object'], separate_xyz.inputs['Vector'])
links.new(separate_xyz.outputs['Z'], wave.inputs['Vector'])
links.new(wave.outputs['Fac'], color_ramp.inputs['Fac'])

# Sediment layer colors (red/orange badlands)
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[0].color = (0.6, 0.3, 0.2, 1)  # Red layer
color_ramp.color_ramp.elements.new(0.5)
color_ramp.color_ramp.elements[1].color = (0.7, 0.5, 0.35, 1)  # Orange layer
color_ramp.color_ramp.elements[2].position = 1.0
color_ramp.color_ramp.elements[2].color = (0.55, 0.45, 0.38, 1)  # Tan layer

bsdf.inputs['Roughness'].default_value = 0.9

links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

badlands.data.materials.append(mat)

# Add camera
bpy.ops.object.camera_add(location=(22, -22, 9))
camera = bpy.context.active_object
camera.rotation_euler = (1.2, 0, 0.785)
bpy.context.scene.camera = camera

# Add sun light with warm color
bpy.ops.object.light_add(type='SUN', location=(15, -15, 20))
sun = bpy.context.active_object
sun.data.energy = 4.5
sun.data.color = (1.0, 0.92, 0.8)  # Warm sunlight
sun.rotation_euler = (0.7, 0.35, 0.65)

print("Eroded Badlands created successfully!")