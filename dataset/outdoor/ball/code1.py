import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Classic"

# Add subdivision surface for smoothness
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Create black pentagon material
black_mat = bpy.data.materials.new(name="Black_Pentagon")
black_mat.use_nodes = True
black_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.05, 0.05, 1)

# Create white hexagon material
white_mat = bpy.data.materials.new(name="White_Hexagon")
white_mat.use_nodes = True
white_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.95, 0.95, 0.95, 1)

# Assign materials
if len(ball.data.materials) == 0:
    ball.data.materials.append(black_mat)
    ball.data.materials.append(white_mat)

# Enter edit mode and assign materials to faces
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Assign materials to faces in a pattern
for i, face in enumerate(ball.data.polygons):
    if i % 2 == 0:
        face.material_index = 0  # Black
    else:
        face.material_index = 1  # White

bpy.ops.object.mode_set(mode='OBJECT')
print("Classic soccer ball created!")
