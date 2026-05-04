import bpy
import bmesh
import math
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Camo"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 1

# Create camo colors
dark_green = bpy.data.materials.new(name="Dark_Green")
dark_green.use_nodes = True
dark_green.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.15, 0.3, 0.1, 1)

light_green = bpy.data.materials.new(name="Light_Green")
light_green.use_nodes = True
light_green.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.4, 0.5, 0.2, 1)

brown = bpy.data.materials.new(name="Brown_Camo")
brown.use_nodes = True
brown.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.2, 0.1, 1)

tan = bpy.data.materials.new(name="Tan_Camo")
tan.use_nodes = True
tan.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.6, 0.5, 0.3, 1)

# Assign materials
ball.data.materials.append(dark_green)
ball.data.materials.append(light_green)
ball.data.materials.append(brown)
ball.data.materials.append(tan)

# Create random camo pattern
random.seed(42)
bpy.ops.object.mode_set(mode='OBJECT')
for i, face in enumerate(ball.data.polygons):
    # Random camo pattern
    weights = [0.4, 0.3, 0.2, 0.1]
    mat_idx = random.choices([0, 1, 2, 3], weights=weights)[0]
    face.material_index = mat_idx

bpy.ops.object.shade_smooth()

print("Camouflage soccer ball created!")
