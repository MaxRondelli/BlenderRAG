import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere base
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Futuristic"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 2

# Create metallic silver material
silver_mat = bpy.data.materials.new(name="Metallic_Silver")
silver_mat.use_nodes = True
bsdf = silver_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.7, 0.7, 0.8, 1)  # Base Color
bsdf.inputs[4].default_value = 0.9  # Metallic
bsdf.inputs[7].default_value = 0.2  # Roughness

# Create neon blue material
neon_mat = bpy.data.materials.new(name="Neon_Blue")
neon_mat.use_nodes = True
bsdf_neon = neon_mat.node_tree.nodes["Principled BSDF"]
bsdf_neon.inputs[0].default_value = (0.0, 0.5, 1.0, 1)
bsdf_neon.inputs[4].default_value = 0.7  # Metallic
bsdf_neon.inputs[18].default_value = 0.5  # Emission Strength

# Assign materials
ball.data.materials.append(silver_mat)
ball.data.materials.append(neon_mat)

# Create hexagonal pattern
bpy.ops.object.mode_set(mode='OBJECT')
for i, face in enumerate(ball.data.polygons):
    # Create panel effect
    if i % 6 == 0:
        face.material_index = 1  # Neon
    else:
        face.material_index = 0  # Silver

# Add edge bevel for panel effect
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.bevel(offset=0.02, segments=2)
bpy.ops.object.mode_set(mode='OBJECT')

print("Futuristic soccer ball created!")
