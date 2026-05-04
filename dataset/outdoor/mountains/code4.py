import bpy
import bmesh
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for mountain range
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
mountain_range = bpy.context.active_object
mountain_range.name = "MountainRange"

# Enter edit mode and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=12)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = mountain_range.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create multiple peaks in a range
peak_positions = [
    (-6, -3, 6.5),
    (-2, 2, 7.2),
    (3, -1, 5.8),
    (7, 3, 6.0),
    (1, -5, 5.5)
]

for vert in bm.verts:
    x, y = vert.co.x, vert.co.y
    height = 0
    
    # Sum influence from all peaks
    for px, py, peak_h in peak_positions:
        dist = math.sqrt((x - px)**2 + (y - py)**2)
        if dist < 8:
            peak_influence = (8 - dist) * (peak_h / 8)
            height += peak_influence
    
    # Add randomness
    height += random.uniform(-0.3, 0.3)
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = mountain_range.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add displacement
displace = mountain_range.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 1.5
displace.mid_level = 0.5

tex = bpy.data.textures.new("RangeTexture", type='CLOUDS')
tex.noise_scale = 0.7
tex.noise_depth = 8
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create brown/gray mountain material
mat = bpy.data.materials.new(name="MountainRangeMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')

noise.inputs['Scale'].default_value = 5.0
noise.inputs['Detail'].default_value = 9.0

color_ramp.color_ramp.elements[0].color = (0.28, 0.22, 0.18, 1)  # Dark brown
color_ramp.color_ramp.elements[1].color = (0.48, 0.42, 0.35, 1)  # Light brown

bsdf.inputs['Roughness'].default_value = 0.9

links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

mountain_range.data.materials.append(mat)

# Add camera
bpy.ops.object.camera_add(location=(25, -25, 12))
camera = bpy.context.active_object
camera.rotation_euler = (1.15, 0, 0.785)
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(15, -15, 20))
sun = bpy.context.active_object
sun.data.energy = 3.8
sun.rotation_euler = (0.85, 0.3, 0.6)

print("Mountain Range created successfully!")