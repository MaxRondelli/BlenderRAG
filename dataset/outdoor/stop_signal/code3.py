import bpy
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Camera
cam = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam)
bpy.context.scene.collection.objects.link(cam_obj)
cam_obj.location = (0, -3, 2.6)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = cam_obj

# Light
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 2
sun_obj = bpy.data.objects.new("Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.location = (3, -3, 5)
sun_obj.rotation_euler = (math.radians(45), 0, math.radians(30))

# Base pole (wider, dark charcoal)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.08, depth=0.1, location=(0, 0, 0.05))
base = bpy.context.active_object
mat_charcoal = bpy.data.materials.new("CharcoalMatte")
mat_charcoal.use_nodes = True
bsdf_charcoal = mat_charcoal.node_tree.nodes["Principled BSDF"]
bsdf_charcoal.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1)
bsdf_charcoal.inputs["Metallic"].default_value = 0.6
bsdf_charcoal.inputs["Roughness"].default_value = 0.8
base.data.materials.append(mat_charcoal)

# Main pole (dark charcoal metallic, hexagonal cross-section, thinner)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=2.3, location=(0, 0.035, 1.25))
palo = bpy.context.active_object
palo.scale[0] = 0.9
palo.scale[1] = 0.9
mat_pole = bpy.data.materials.new("DarkCharcoalPole")
mat_pole.use_nodes = True
bsdf_pole = mat_pole.node_tree.nodes["Principled BSDF"]
bsdf_pole.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1)
bsdf_pole.inputs["Metallic"].default_value = 0.5
bsdf_pole.inputs["Roughness"].default_value = 0.85
palo.data.materials.append(mat_pole)

# Triangular gussets instead of rectangular brackets
for i, z_pos in enumerate([2.3, 2.5]):
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.06, depth=0.05, location=(0, 0.035, z_pos))
    gusset = bpy.context.active_object
    gusset.rotation_euler = (math.radians(90), 0, 0)
    gusset.scale = (1.2, 0.8, 1.5)
    gusset.data.materials.append(mat_charcoal)

# Black octagonal border
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.48, depth=0.02, location=(0, 0.015, 2.6))
bordo = bpy.context.active_object
bordo.rotation_euler = (math.radians(90), 0, 0)
mat_black = bpy.data.materials.new("MatteBlack")
mat_black.use_nodes = True
bsdf_black = mat_black.node_tree.nodes["Principled BSDF"]
bsdf_black.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)
bsdf_black.inputs["Roughness"].default_value = 0.9
bordo.data.materials.append(mat_black)

# Black octagonal STOP sign
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.45, depth=0.03, location=(0, 0, 2.6))
stop_sign = bpy.context.active_object
stop_sign.rotation_euler = (math.radians(90), 0, 0)
mat_sign_black = bpy.data.materials.new("SignBlack")
mat_sign_black.use_nodes = True
bsdf_sign_black = mat_sign_black.node_tree.nodes["Principled BSDF"]
bsdf_sign_black.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
bsdf_sign_black.inputs["Roughness"].default_value = 0.8
stop_sign.data.materials.append(mat_sign_black)

# Bright yellow STOP text
bpy.ops.object.text_add(location=(0, -0.035, 2.6))
text_obj = bpy.context.active_object
text_obj.data.body = "STOP"
text_obj.data.size = 0.35
text_obj.data.extrude = 0.015
text_obj.rotation_euler = (math.radians(90), 0, 0)
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'
mat_yellow = bpy.data.materials.new("BrightYellow")
mat_yellow.use_nodes = True
bsdf_yellow = mat_yellow.node_tree.nodes["Principled BSDF"]
bsdf_yellow.inputs["Base Color"].default_value = (1, 0.9, 0, 1)
bsdf_yellow.inputs["Roughness"].default_value = 0.3
text_obj.data.materials.append(mat_yellow)

# Background
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
bg.inputs["Strength"].default_value = 1

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = True
