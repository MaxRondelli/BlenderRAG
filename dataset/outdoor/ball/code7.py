import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Stars"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2

# Create gold material for stars
gold_mat = bpy.data.materials.new(name="Gold_Star")
gold_mat.use_nodes = True
bsdf = gold_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (1.0, 0.8, 0.0, 1)
bsdf.inputs[4].default_value = 0.8  # Metallic
bsdf.inputs[7].default_value = 0.2  # Roughness

# Create dark blue material
blue_mat = bpy.data.materials.new(name="Dark_Blue")
blue_mat.use_nodes = True
bsdf_blue = blue_mat.node_tree.nodes["Principled BSDF"]
bsdf_blue.inputs[0].default_value = (0.05, 0.05, 0.3, 1)
bsdf_blue.inputs[7].default_value = 0.4

# Create white material
white_mat = bpy.data.materials.new(name="White_Panel")
white_mat.use_nodes = True
bsdf_white = white_mat.node_tree.nodes["Principled BSDF"]
bsdf_white.inputs[0].default_value = (0.95, 0.95, 0.95, 1)

# Assign materials
ball.data.materials.append(gold_mat)
ball.data.materials.append(blue_mat)
ball.data.materials.append(white_mat)

# Create star pattern
bpy.ops.object.mode_set(mode='OBJECT')
for i, face in enumerate(ball.data.polygons):
    # Every 5th face is a gold star
    if i % 5 == 0:
        face.material_index = 0  # Gold
    elif i % 3 == 0:
        face.material_index = 1  # Blue
    else:
        face.material_index = 2  # White

bpy.ops.object.shade_smooth()

print("Star pattern soccer ball created!")
