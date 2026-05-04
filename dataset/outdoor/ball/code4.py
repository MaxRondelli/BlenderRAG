import bpy
import bmesh
import math
import colorsys

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Rainbow"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2

# Create rainbow materials
num_colors = 8
materials = []
for i in range(num_colors):
    hue = i / num_colors
    rgb = colorsys.hsv_to_rgb(hue, 0.9, 0.95)
    
    mat = bpy.data.materials.new(name=f"Rainbow_{i}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (*rgb, 1)
    bsdf.inputs[7].default_value = 0.3  # Roughness
    
    ball.data.materials.append(mat)
    materials.append(mat)

# Assign materials in rainbow pattern
bpy.ops.object.mode_set(mode='OBJECT')
for i, face in enumerate(ball.data.polygons):
    face.material_index = i % num_colors

# Smooth shading
bpy.ops.object.shade_smooth()

print("Rainbow soccer ball created!")
