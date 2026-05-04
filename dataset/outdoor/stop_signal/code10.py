import bpy
import bmesh
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
sun.energy = 3
sun_obj = bpy.data.objects.new("Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.location = (3, -3, 5)
sun_obj.rotation_euler = (math.radians(45), 0, math.radians(30))

# Base pole (wider, black metallic)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.15, location=(0, 0, 0.075))
base = bpy.context.active_object
base_modifier = base.modifiers.new(name="Subsurf", type="SUBSURF")
base_modifier.levels = 2
mat_black_metal = bpy.data.materials.new("BlackMetal")
mat_black_metal.use_nodes = True
bsdf_black = mat_black_metal.node_tree.nodes["Principled BSDF"]
bsdf_black.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
bsdf_black.inputs["Metallic"].default_value = 0.9
bsdf_black.inputs["Roughness"].default_value = 0.2
base.data.materials.append(mat_black_metal)

# Main pole (thicker black metallic, smooth)
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.3, location=(0, 0.035, 1.25))
pole = bpy.context.active_object
pole_modifier = pole.modifiers.new(name="Subsurf", type="SUBSURF")
pole_modifier.levels = 3
mat_pole = bpy.data.materials.new("PoleMetal")
mat_pole.use_nodes = True
bsdf_pole = mat_pole.node_tree.nodes["Principled BSDF"]
bsdf_pole.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1)
bsdf_pole.inputs["Metallic"].default_value = 0.85
bsdf_pole.inputs["Roughness"].default_value = 0.15
pole.data.materials.append(mat_pole)

# Modern mounting brackets (sleeker design)
for i, z_pos in enumerate([2.25, 2.55]):
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0.035, z_pos))
    bracket = bpy.context.active_object
    bracket.scale = (0.8, 1.5, 0.25)
    bracket_modifier = bracket.modifiers.new(name="Subsurf", type="SUBSURF")
    bracket_modifier.levels = 2
    bracket.data.materials.append(mat_black_metal)

# White border back
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.48, depth=0.02, location=(0, 0.015, 2.6))
border = bpy.context.active_object
border.rotation_euler = (math.radians(90), 0, 0)
mat_white = bpy.data.materials.new("White")
mat_white.use_nodes = True
bsdf_white = mat_white.node_tree.nodes["Principled BSDF"]
bsdf_white.inputs["Base Color"].default_value = (1, 1, 1, 1)
bsdf_white.inputs["Roughness"].default_value = 0.1
border.data.materials.append(mat_white)

# Yellow STOP sign (octagonal)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.45, depth=0.03, location=(0, 0, 2.6))
stop_sign = bpy.context.active_object
stop_sign.rotation_euler = (math.radians(90), 0, 0)
mat_yellow = bpy.data.materials.new("BrightYellow")
mat_yellow.use_nodes = True
bsdf_yellow = mat_yellow.node_tree.nodes["Principled BSDF"]
bsdf_yellow.inputs["Base Color"].default_value = (1.0, 0.9, 0.0, 1)
bsdf_yellow.inputs["Roughness"].default_value = 0.15
stop_sign.data.materials.append(mat_yellow)

# Black STOP text
bpy.ops.object.text_add(location=(0, -0.035, 2.6))
text_obj = bpy.context.active_object
text_obj.data.body = "STOP"
text_obj.data.size = 0.35
text_obj.data.extrude = 0.02
text_obj.rotation_euler = (math.radians(90), 0, 0)
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'
mat_black_text = bpy.data.materials.new("BlackText")
mat_black_text.use_nodes = True
bsdf_text = mat_black_text.node_tree.nodes["Principled BSDF"]
bsdf_text.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
bsdf_text.inputs["Roughness"].default_value = 0.3
text_obj.data.materials.append(mat_black_text)

# Background
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs["Color"].default_value = (0.85, 0.85, 0.85, 1)
bg.inputs["Strength"].default_value = 1.2

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = True

