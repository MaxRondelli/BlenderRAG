import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere base
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=(0, 0, 0))
ball = bpy.context.active_object
ball.name = "SoccerBall_Striped"

# Add subdivision surface
subsurf = ball.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf.levels = 1

# Create materials for stripes
red_mat = bpy.data.materials.new(name="Red_Stripe")
red_mat.use_nodes = True
red_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.1, 0.1, 1)

blue_mat = bpy.data.materials.new(name="Blue_Stripe")
blue_mat.use_nodes = True
blue_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.3, 0.8, 1)

white_mat = bpy.data.materials.new(name="White_Stripe")
white_mat.use_nodes = True
white_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.95, 0.95, 0.95, 1)

# Assign materials
ball.data.materials.append(red_mat)
ball.data.materials.append(blue_mat)
ball.data.materials.append(white_mat)

# Create vertical stripe pattern
bpy.ops.object.mode_set(mode='OBJECT')
for i, face in enumerate(ball.data.polygons):
    # Calculate which stripe this face belongs to
    center = face.center
    angle = math.atan2(center.y, center.x)
    stripe_num = int((angle + math.pi) / (2 * math.pi) * 12) % 3
    face.material_index = stripe_num

print("Striped soccer ball created!")
