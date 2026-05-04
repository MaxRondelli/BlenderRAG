import bpy
import bmesh
import random
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for the mountain
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
mountain = bpy.context.active_object
mountain.name = "SharpPeakMountain"

# Enter edit mode and subdivide for detail
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=10)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = mountain.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create sharp peak mountain shape
for vert in bm.verts:
    dist = (vert.co.xy).length
    
    if dist < 6:
        # Very sharp peak formula
        height = (6 - dist) ** 1.5 * 1.2 + random.uniform(-0.1, 0.1)
        vert.co.z = max(0, height)
    else:
        vert.co.z = random.uniform(0, 0.05)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = mountain.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add displacement for rocky details
displace = mountain.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 0.8
displace.mid_level = 0.5

tex = bpy.data.textures.new("SharpPeakTexture", type='CLOUDS')
tex.noise_scale = 1.2
tex.noise_depth = 8
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create gray rocky material
mat = bpy.data.materials.new(name="SharpPeakMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')

noise.inputs['Scale'].default_value = 6.0
noise.inputs['Detail'].default_value = 10.0

color_ramp.color_ramp.elements[0].color = (0.3, 0.3, 0.32, 1)  # Dark gray
color_ramp.color_ramp.elements[1].color = (0.5, 0.5, 0.52, 1)  # Light gray

bsdf.inputs['Roughness'].default_value = 0.95

links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

mountain.data.materials.append(mat)

# Add camera
bpy.ops.object.camera_add(location=(18, -18, 10))
camera = bpy.context.active_object
camera.rotation_euler = (1.15, 0, 0.785)
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
sun = bpy.context.active_object
sun.data.energy = 3.5
sun.rotation_euler = (0.9, 0.3, 0.5)

print("Sharp Peak Mountain created successfully!")