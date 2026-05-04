import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere base
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Vintage"

# Add subdivision surface for smoother look
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 1

# Create brown leather material
leather_mat = bpy.data.materials.new(name="Brown_Leather")
leather_mat.use_nodes = True
nodes = leather_mat.node_tree.nodes
links = leather_mat.node_tree.links

bsdf = nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.4, 0.25, 0.15, 1)  # Brown color
bsdf.inputs[7].default_value = 0.6  # Roughness
bsdf.inputs[12].default_value = 0.3  # Specular

# Add noise texture for leather variation
noise_tex = nodes.new(type='ShaderNodeTexNoise')
noise_tex.inputs[2].default_value = 15.0  # Scale
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.color_ramp.elements[0].color = (0.3, 0.2, 0.1, 1)
color_ramp.color_ramp.elements[1].color = (0.5, 0.3, 0.2, 1)

links.new(noise_tex.outputs[0], color_ramp.inputs[0])
links.new(color_ramp.outputs[0], bsdf.inputs[0])

ball.data.materials.append(leather_mat)

# Add displacement for stitching effect
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Add array of small indentations to simulate stitching
for i in range(0, len(ball.data.vertices), 8):
    ball.data.vertices[i].co *= 0.98

bpy.ops.object.shade_smooth()

print("Vintage leather soccer ball created!")
