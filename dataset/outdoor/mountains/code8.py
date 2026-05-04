import bpy
import bmesh
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for alpine ridges
bpy.ops.mesh.primitive_plane_add(size=26, location=(0, 0, 0))
alpine = bpy.context.active_object
alpine.name = "AlpineRidges"

# Enter edit mode and subdivide heavily for sharp detail
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=14)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = alpine.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create dramatic jagged alpine ridges
for vert in bm.verts:
    x, y = vert.co.x, vert.co.y
    
    # Main ridge system - sharp peaks
    ridge1 = abs(math.sin(y * 0.4)) ** 0.6 * 7
    ridge2 = abs(math.sin(y * 0.25 + 1.5)) ** 0.5 * 6
    ridge3 = abs(math.sin(y * 0.6 + 3)) ** 0.7 * 5
    
    # Cross ridges for more complexity
    cross_ridge = abs(math.sin(x * 0.3)) * 2
    
    # Combine ridges with varying weights
    height = ridge1 + ridge2 * 0.6 + ridge3 * 0.4 + cross_ridge * 0.3
    
    # Make peaks more dramatic and sharp
    height = height ** 1.5
    
    # Add jagged variation - more pronounced at peaks
    jagged_factor = (height / 10) * random.uniform(-0.6, 0.4)
    height += jagged_factor
    
    # Add small-scale rocky detail
    rocky_noise = random.uniform(-0.2, 0.2)
    height += rocky_noise
    
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface - lower level to preserve sharpness
subsurf = alpine.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 1
subsurf.render_levels = 2

# Add strong displacement for jagged peaks
displace = alpine.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 1.8
displace.mid_level = 0.5

tex = bpy.data.textures.new("AlpineTexture", type='VORONOI')
tex.noise_scale = 2.5
tex.distance_metric = 'DISTANCE'
displace.texture = tex

# Add second displacement for fine detail
displace2 = alpine.modifiers.new(name="Displace2", type='DISPLACE')
displace2.strength = 0.6
displace2.mid_level = 0.5

tex2 = bpy.data.textures.new("AlpineDetail", type='CLOUDS')
tex2.noise_scale = 3.0
tex2.noise_depth = 10
displace2.texture = tex2

bpy.ops.object.shade_smooth()

# Create alpine material with snow and rock
mat = bpy.data.materials.new(name="AlpineMaterial")
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
mix = nodes.new('ShaderNodeMix')
mix.data_type = 'RGBA'

noise.inputs['Scale'].default_value = 8.0
noise.inputs['Detail'].default_value = 10.0

# Height-based snow coverage
links.new(coord.outputs['Object'], separate_xyz.inputs['Vector'])

# More realistic gradient - snow starts higher, rock at bottom
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[0].color = (0.28, 0.26, 0.24, 1)  # Dark rock
color_ramp.color_ramp.elements.new(0.35)
color_ramp.color_ramp.elements[1].color = (0.42, 0.38, 0.35, 1)  # Mid rock
color_ramp.color_ramp.elements[2].position = 0.65
color_ramp.color_ramp.elements[2].color = (0.95, 0.95, 0.98, 1)  # Snow

links.new(separate_xyz.outputs['Z'], color_ramp.inputs['Fac'])
links.new(noise.outputs['Fac'], mix.inputs['Factor'])
mix.inputs['A'].default_value = (1, 1, 1, 1)
links.new(color_ramp.outputs['Color'], mix.inputs['B'])
links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])

bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Specular'].default_value = 0.3

links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

alpine.data.materials.append(mat)

# Add camera positioned to show dramatic ridges
bpy.ops.object.camera_add(location=(22, -18, 13))
camera = bpy.context.active_object
camera.rotation_euler = (1.05, 0, 0.85)
bpy.context.scene.camera = camera

# Add sun light with dramatic angle
bpy.ops.object.light_add(type='SUN', location=(15, -12, 20))
sun = bpy.context.active_object
sun.data.energy = 4.8
sun.data.color = (1.0, 0.98, 0.95)
sun.rotation_euler = (0.65, 0.4, 0.6)

print("Alpine Ridges created successfully!")