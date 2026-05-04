import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Crystal"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2

# Create glass/crystal material
glass_mat = bpy.data.materials.new(name="Crystal_Glass")
glass_mat.use_nodes = True
nodes = glass_mat.node_tree.nodes
links = glass_mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add glass BSDF
glass_bsdf = nodes.new(type='ShaderNodeBsdfGlass')
glass_bsdf.inputs[0].default_value = (0.8, 0.9, 1.0, 1)  # Slight blue tint
glass_bsdf.inputs[1].default_value = 0.05  # Roughness
glass_bsdf.inputs[2].default_value = 1.45  # IOR

# Add glossy BSDF for reflections
glossy_bsdf = nodes.new(type='ShaderNodeBsdfGlossy')
glossy_bsdf.inputs[1].default_value = 0.1

# Mix shader
mix_shader = nodes.new(type='ShaderNodeMixShader')
mix_shader.inputs[0].default_value = 0.3

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')

# Connect nodes
links.new(glass_bsdf.outputs[0], mix_shader.inputs[1])
links.new(glossy_bsdf.outputs[0], mix_shader.inputs[2])
links.new(mix_shader.outputs[0], output.inputs[0])

ball.data.materials.append(glass_mat)

# Enable transparency in viewport
ball.show_transparent = True

# Add solidify modifier for thickness
solidify = ball.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 0.02

bpy.ops.object.shade_smooth()

print("Crystal glass soccer ball created!")
