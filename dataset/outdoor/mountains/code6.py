import bpy
import bmesh
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for mesa
bpy.ops.mesh.primitive_plane_add(size=22, location=(0, 0, 0))
mesa = bpy.context.active_object
mesa.name = "DesertMesa"

# Enter edit mode and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=12)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = mesa.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create flat-topped mesa with more natural top surface
for vert in bm.verts:
    x, y = vert.co.x, vert.co.y
    dist = (vert.co.xy).length
    
    if dist < 5:
        # Flat top with organic variation and subtle erosion patterns
        base_height = 4.5
        # Add subtle undulations to the top surface
        variation = math.sin(x * 0.8) * 0.15 + math.cos(y * 0.9) * 0.12
        # Add small-scale noise
        noise = random.uniform(-0.08, 0.08)
        height = base_height + variation + noise
    elif dist < 6:
        # Steep sides with erosion channels
        slope_factor = (6 - dist)
        base_slope = slope_factor * 4.5
        # Add vertical erosion grooves
        erosion = abs(math.sin(math.atan2(y, x) * 8)) * 0.3 * slope_factor
        height = base_slope - erosion + random.uniform(-0.25, 0.15)
    else:
        # Desert floor with small dunes
        dune_pattern = abs(math.sin(x * 0.3) * math.cos(y * 0.4)) * 0.3
        height = dune_pattern + random.uniform(0, 0.12)
    
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = mesa.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add displacement for erosion patterns
displace = mesa.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 0.5
displace.mid_level = 0.5

tex = bpy.data.textures.new("MesaTexture", type='CLOUDS')
tex.noise_scale = 1.8
tex.noise_depth = 6
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create sandstone/desert material
mat = bpy.data.materials.new(name="MesaMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')
coord = nodes.new('ShaderNodeTexCoord')

noise.inputs['Scale'].default_value = 3.0
noise.inputs['Detail'].default_value = 6.0

# Sandstone color layers
color_ramp.color_ramp.elements[0].color = (0.65, 0.45, 0.3, 1)  # Orange sandstone
color_ramp.color_ramp.elements[1].color = (0.75, 0.6, 0.45, 1)  # Light tan

bsdf.inputs['Roughness'].default_value = 0.85

links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

mesa.data.materials.append(mat)

# Add camera
bpy.ops.object.camera_add(location=(16, -16, 7))
camera = bpy.context.active_object
camera.rotation_euler = (1.25, 0, 0.785)
bpy.context.scene.camera = camera

# Add strong sun for desert lighting
bpy.ops.object.light_add(type='SUN', location=(12, -12, 20))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.data.color = (1.0, 0.95, 0.85)  # Warm desert sun
sun.rotation_euler = (0.6, 0.3, 0.7)

print("Desert Mesa created successfully!")