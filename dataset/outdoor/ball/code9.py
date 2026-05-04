import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Tribal"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2

# Create materials
black_mat = bpy.data.materials.new(name="Black_Tribal")
black_mat.use_nodes = True
black_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.05, 0.05, 0.05, 1)

orange_mat = bpy.data.materials.new(name="Orange_Tribal")
orange_mat.use_nodes = True
orange_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.4, 0.0, 1)

yellow_mat = bpy.data.materials.new(name="Yellow_Tribal")
yellow_mat.use_nodes = True
yellow_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.8, 0.0, 1)

# Assign materials
ball.data.materials.append(black_mat)
ball.data.materials.append(orange_mat)
ball.data.materials.append(yellow_mat)

# Create geometric tribal pattern
bpy.ops.object.mode_set(mode='OBJECT')
for i, face in enumerate(ball.data.polygons):
    # Calculate position-based pattern
    center = face.center
    z_pos = center.z
    
    if abs(z_pos) > 0.7:
        face.material_index = 0  # Black at poles
    elif i % 3 == 0:
        face.material_index = 1  # Orange
    elif i % 3 == 1:
        face.material_index = 2  # Yellow
    else:
        face.material_index = 0  # Black

# Add edge split for sharper geometric look
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.edge_split(type='EDGE')
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.shade_smooth()

print("Tribal pattern soccer ball created!")
