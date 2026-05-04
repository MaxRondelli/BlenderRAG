import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Cyberpunk"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2

# Create black base material
black_mat = bpy.data.materials.new(name="Black_Base")
black_mat.use_nodes = True
bsdf_black = black_mat.node_tree.nodes["Principled BSDF"]
bsdf_black.inputs[0].default_value = (0.02, 0.02, 0.02, 1)
bsdf_black.inputs[4].default_value = 0.3  # Metallic
bsdf_black.inputs[7].default_value = 0.1  # Roughness

# Create cyan glow material
cyan_mat = bpy.data.materials.new(name="Cyan_Glow")
cyan_mat.use_nodes = True
bsdf_cyan = cyan_mat.node_tree.nodes["Principled BSDF"]
bsdf_cyan.inputs[0].default_value = (0.0, 0.8, 1.0, 1)
bsdf_cyan.inputs[17].default_value = (0.0, 1.0, 1.0)  # Emission color (RGB only)
bsdf_cyan.inputs[18].default_value = 2.0  # Emission strength

# Create magenta glow material
magenta_mat = bpy.data.materials.new(name="Magenta_Glow")
magenta_mat.use_nodes = True
bsdf_magenta = magenta_mat.node_tree.nodes["Principled BSDF"]
bsdf_magenta.inputs[0].default_value = (1.0, 0.0, 0.8, 1)
bsdf_magenta.inputs[17].default_value = (1.0, 0.0, 1.0)  # Emission color (RGB only)
bsdf_magenta.inputs[18].default_value = 2.0  # Emission strength

# Create purple glow material
purple_mat = bpy.data.materials.new(name="Purple_Glow")
purple_mat.use_nodes = True
bsdf_purple = purple_mat.node_tree.nodes["Principled BSDF"]
bsdf_purple.inputs[0].default_value = (0.5, 0.0, 1.0, 1)
bsdf_purple.inputs[17].default_value = (0.7, 0.0, 1.0)  # Emission color (RGB only)
bsdf_purple.inputs[18].default_value = 2.0  # Emission strength

# Assign materials
ball.data.materials.append(black_mat)
ball.data.materials.append(cyan_mat)
ball.data.materials.append(magenta_mat)
ball.data.materials.append(purple_mat)

# Create cyberpunk pattern with glowing lines
bpy.ops.object.mode_set(mode='OBJECT')
for i, face in enumerate(ball.data.polygons):
    # Create circuit-board-like pattern
    if i % 7 == 0:
        face.material_index = 1  # Cyan
    elif i % 7 == 2:
        face.material_index = 2  # Magenta
    elif i % 7 == 4:
        face.material_index = 3  # Purple
    else:
        face.material_index = 0  # Black

bpy.ops.object.shade_smooth()
print("Cyberpunk soccer ball created!")
