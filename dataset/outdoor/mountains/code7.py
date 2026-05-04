import bpy
import bmesh
import random

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for cliff
bpy.ops.mesh.primitive_plane_add(size=18, location=(0, 0, 0))
cliff = bpy.context.active_object
cliff.name = "RockyCliff"

# Enter edit mode and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=10)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = cliff.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create cliff with steep drop
for vert in bm.verts:
    x, y = vert.co.x, vert.co.y
    
    # Create steep cliff face on one side
    if x > 2:
        height = 0.2 + random.uniform(-0.1, 0.1)
    elif x > -2:
        # Steep transition
        height = ((x + 2) / 4) * 7 + random.uniform(-0.3, 0.3)
    else:
        # Top plateau with some variation
        height = 7 + random.uniform(-0.4, 0.4)
    
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = cliff.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add strong displacement for rocky surface
displace = cliff.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 1.8
displace.mid_level = 0.5

tex = bpy.data.textures.new("CliffTexture", type='VORONOI')
tex.noise_scale = 1.5
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create layered rock material
mat = bpy.data.materials.new(name="CliffMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
noise1 = nodes.new('ShaderNodeTexNoise')
noise2 = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')
mix = nodes.new('ShaderNodeMix')
mix.data_type = 'RGBA'

# Two noise layers for complex rock pattern
noise1.inputs['Scale'].default_value = 4.0
noise1.inputs['Detail'].default_value = 8.0

noise2.inputs['Scale'].default_value = 10.0
noise2.inputs['Detail'].default_value = 6.0

links.new(noise1.outputs['Fac'], mix.inputs['A'])
links.new(noise2.outputs['Fac'], mix.inputs['B'])
links.new(mix.outputs['Result'], color_ramp.inputs['Fac'])

# Rock layer colors
color_ramp.color_ramp.elements[0].color = (0.4, 0.35, 0.3, 1)  # Brown layer
color_ramp.color_ramp.elements[1].color = (0.55, 0.5, 0.45, 1)  # Tan layer

bsdf.inputs['Roughness'].default_value = 0.92

links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

cliff.data.materials.append(mat)

# Add camera to show cliff face
bpy.ops.object.camera_add(location=(12, -15, 6))
camera = bpy.context.active_object
camera.rotation_euler = (1.3, 0, 0.65)
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(8, -10, 12))
sun = bpy.context.active_object
sun.data.energy = 3.2
sun.rotation_euler = (0.9, 0.5, 0.4)

print("Rocky Cliff created successfully!")