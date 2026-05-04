import bpy
import bmesh
import random
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base plane for volcano
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
volcano = bpy.context.active_object
volcano.name = "VolcanicMountain"

# Enter edit mode and subdivide
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.subdivide(number_cuts=10)
bpy.ops.object.mode_set(mode='OBJECT')

# Get mesh data
mesh = volcano.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Create volcano shape with crater
for vert in bm.verts:
    dist = (vert.co.xy).length
    
    if dist < 1.5:
        # Crater depression at top
        height = 5.5 - (1.5 - dist) * 1.2 + random.uniform(-0.1, 0.1)
    elif dist < 7:
        # Cone shape
        height = (7 - dist) * 0.9 + random.uniform(-0.2, 0.2)
    else:
        # Base
        height = random.uniform(0, 0.05)
    
    vert.co.z = max(0, height)

bm.to_mesh(mesh)
bm.free()

# Add subdivision surface
subsurf = volcano.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2

# Add displacement
displace = volcano.modifiers.new(name="Displace", type='DISPLACE')
displace.strength = 0.9
displace.mid_level = 0.5

tex = bpy.data.textures.new("VolcanoTexture", type='CLOUDS')
tex.noise_scale = 1.0
tex.noise_depth = 6
displace.texture = tex

bpy.ops.object.shade_smooth()

# Create dark volcanic rock material
mat = bpy.data.materials.new(name="VolcanicMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
noise = nodes.new('ShaderNodeTexNoise')
color_ramp = nodes.new('ShaderNodeValToRGB')
coord = nodes.new('ShaderNodeTexCoord')

noise.inputs['Scale'].default_value = 7.0
noise.inputs['Detail'].default_value = 10.0

# Dark volcanic colors
color_ramp.color_ramp.elements[0].color = (0.12, 0.1, 0.1, 1)  # Very dark gray
color_ramp.color_ramp.elements[1].color = (0.25, 0.2, 0.18, 1)  # Dark brown

bsdf.inputs['Roughness'].default_value = 0.95

links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

volcano.data.materials.append(mat)

# Add glowing crater effect
bpy.ops.mesh.primitive_plane_add(size=2.5, location=(0, 0, 5.6))
crater_glow = bpy.context.active_object
crater_glow.name = "CraterGlow"

# Create emission material for crater
glow_mat = bpy.data.materials.new(name="CraterGlowMaterial")
glow_mat.use_nodes = True
glow_nodes = glow_mat.node_tree.nodes
glow_links = glow_mat.node_tree.links
glow_nodes.clear()

glow_output = glow_nodes.new('ShaderNodeOutputMaterial')
glow_emission = glow_nodes.new('ShaderNodeEmission')

glow_emission.inputs['Color'].default_value = (1.0, 0.3, 0.05, 1)  # Orange glow
glow_emission.inputs['Strength'].default_value = 5.0

glow_links.new(glow_emission.outputs['Emission'], glow_output.inputs['Surface'])

crater_glow.data.materials.append(glow_mat)

# Add camera
bpy.ops.object.camera_add(location=(18, -18, 10))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = camera

# Add sun light
bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
sun = bpy.context.active_object
sun.data.energy = 2.5
sun.rotation_euler = (1.0, 0.4, 0.5)

print("Volcanic Mountain created successfully!")