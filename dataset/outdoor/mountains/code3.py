import bpy
import bmesh
import random

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane
bpy.ops.mesh.primitive_plane_add(size=22, location=(0, 0, 0))
mountain = bpy.context.active_object
mountain.name = "SnowCappedMountain"

# Enter edit mode and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=10)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = mountain.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create tall mountain shape
for vert in bm.verts:
    dist = (vert.co.xy).length
    
    if dist < 7:
        height = (7 - dist) * 1.4 + random.uniform(-0.2, 0.2)
        vert.co.z = max(0, height)
    else:
        vert.co.z = random.uniform(0, 0.08)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = mountain.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add displacement
displace = mountain.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 1.0
displace.mid_level = 0.5

tex = bpy.data.textures.new("SnowMountainTexture", type='CLOUDS')
tex.noise_scale = 0.9
tex.noise_depth = 7
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create snow-capped material with gradient
mat = bpy.data.materials.new(name="SnowCappedMaterial")
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
mix_color = nodes.new('ShaderNodeMix')
mix_color.data_type = 'RGBA'

# Noise for variation
noise.inputs['Scale'].default_value = 5.0

# Use Z coordinate for height-based coloring
links.new(coord.outputs['Object'], separate_xyz.inputs['Vector'])

# Color ramp for snow line (white at top, rock at bottom)
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[0].color = (0.35, 0.3, 0.28, 1)  # Rock
color_ramp.color_ramp.elements[1].position = 0.6
color_ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.98, 1)  # Snow

links.new(separate_xyz.outputs['Z'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

bsdf.inputs['Roughness'].default_value = 0.7

links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

mountain.data.materials.append(mat)

# Add camera
bpy.ops.object.camera_add(location=(16, -16, 9))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(12, -12, 18))
sun = bpy.context.active_object
sun.data.energy = 4.5
sun.rotation_euler = (0.8, 0.4, 0.5)

print("Snow-Capped Mountain created successfully!")