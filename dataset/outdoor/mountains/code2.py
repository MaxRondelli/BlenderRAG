import bpy
import bmesh
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for rolling hills
bpy.ops.mesh.primitive_plane_add(size=25, location=(0, 0, 0))
hills = bpy.context.active_object
hills.name = "RollingHills"

# Enter edit mode and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=12)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = hills.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create rolling hills with multiple peaks
for vert in bm.verts:
    x, y = vert.co.x, vert.co.y
    
    # Multiple sine waves for rolling effect
    height = 0
    height += math.sin(x * 0.3) * 1.5
    height += math.sin(y * 0.4) * 1.2
    height += math.sin(x * 0.15 + y * 0.2) * 2.0
    height += random.uniform(-0.2, 0.2)
    
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = hills.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 3

# Add gentle displacement
displace = hills.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 0.5
displace.mid_level = 0.5

tex = bpy.data.textures.new("HillsTexture", type='CLOUDS')
tex.noise_scale = 0.5
tex.noise_depth = 4
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create green grassy material
mat = bpy.data.materials.new(name="GrassyHillsMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')

noise.inputs['Scale'].default_value = 4.0
noise.inputs['Detail'].default_value = 6.0

color_ramp.color_ramp.elements[0].color = (0.2, 0.4, 0.15, 1)  # Dark green
color_ramp.color_ramp.elements[1].color = (0.35, 0.6, 0.25, 1)  # Light green

bsdf.inputs['Roughness'].default_value = 0.85

links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

hills.data.materials.append(mat)

# Add camera
bpy.ops.object.camera_add(location=(20, -20, 8))
camera = bpy.context.active_object
camera.rotation_euler = (1.2, 0, 0.785)
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(15, -15, 20))
sun = bpy.context.active_object
sun.data.energy = 4.0
sun.rotation_euler = (0.7, 0.2, 0.6)

print("Rolling Hills created successfully!")