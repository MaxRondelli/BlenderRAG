import bpy
import math

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Camera
cam = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam)
bpy.context.scene.collection.objects.link(cam_obj)
cam_obj.location = (0, -3, 2.6)
cam_obj.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = cam_obj

# Luce
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 2
sun_obj = bpy.data.objects.new("Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.location = (3, -3, 5)
sun_obj.rotation_euler = (math.radians(45), 0, math.radians(30))

# Base palo (sleek black metal)
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.1, location=(0, 0, 0.05))
base = bpy.context.active_object
mat_nero = bpy.data.materials.new("NeroMetallo")
mat_nero.use_nodes = True
bsdf_nero = mat_nero.node_tree.nodes["Principled BSDF"]
bsdf_nero.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)
bsdf_nero.inputs["Metallic"].default_value = 0.9
bsdf_nero.inputs["Roughness"].default_value = 0.2
base.data.materials.append(mat_nero)

# Palo principale (sleek black metal, più sottile e moderno)
bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=2.3, location=(0, 0.035, 1.25))
palo = bpy.context.active_object
palo.scale[0] = 0.95
palo.scale[1] = 0.95
mat_palo = bpy.data.materials.new("PaloNero")
mat_palo.use_nodes = True
bsdf_palo = mat_palo.node_tree.nodes["Principled BSDF"]
bsdf_palo.inputs["Base Color"].default_value = (0.08, 0.08, 0.08, 1)
bsdf_palo.inputs["Metallic"].default_value = 0.9
bsdf_palo.inputs["Roughness"].default_value = 0.15
palo.data.materials.append(mat_palo)

# Supporti orizzontali moderni (staffe nere più sleek)
for i, z_pos in enumerate([2.3, 2.5]):
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0, 0.035, z_pos))
    staffa = bpy.context.active_object
    staffa.scale = (0.7, 1.1, 0.25)
    staffa.data.materials.append(mat_nero)

# Bordo grigio scuro retro
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.48, depth=0.02, location=(0, 0.015, 2.6))
bordo = bpy.context.active_object
bordo.rotation_euler = (math.radians(90), 0, 0)
mat_grigio_scuro = bpy.data.materials.new("GrigioScuro")
mat_grigio_scuro.use_nodes = True
bsdf_grigio_scuro = mat_grigio_scuro.node_tree.nodes["Principled BSDF"]
bsdf_grigio_scuro.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1)
bsdf_grigio_scuro.inputs["Metallic"].default_value = 0.3
bsdf_grigio_scuro.inputs["Roughness"].default_value = 0.4
bordo.data.materials.append(mat_grigio_scuro)

# Segnale STOP (deep navy blue)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.45, depth=0.03, location=(0, 0, 2.6))
stop_sign = bpy.context.active_object
stop_sign.rotation_euler = (math.radians(90), 0, 0)
mat_blu_navy = bpy.data.materials.new("BluNavy")
mat_blu_navy.use_nodes = True
bsdf_blu = mat_blu_navy.node_tree.nodes["Principled BSDF"]
bsdf_blu.inputs["Base Color"].default_value = (0.05, 0.15, 0.35, 1)
bsdf_blu.inputs["Roughness"].default_value = 0.25
bsdf_blu.inputs["Metallic"].default_value = 0.1
stop_sign.data.materials.append(mat_blu_navy)

# Testo STOP (bright yellow)
bpy.ops.object.text_add(location=(0, -0.035, 2.6))
text_obj = bpy.context.active_object
text_obj.data.body = "STOP"
text_obj.data.size = 0.35
text_obj.data.extrude = 0.015
text_obj.rotation_euler = (math.radians(90), 0, 0)
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'
mat_giallo = bpy.data.materials.new("GialloVivace")
mat_giallo.use_nodes = True
bsdf_giallo = mat_giallo.node_tree.nodes["Principled BSDF"]
bsdf_giallo.inputs["Base Color"].default_value = (1.0, 0.9, 0.1, 1)
bsdf_giallo.inputs["Roughness"].default_value = 0.3
text_obj.data.materials.append(mat_giallo)

# Sfondo
bpy.context.scene.world.use_nodes = True
bg = bpy.context.scene.world.node_tree.nodes['Background']
bg.inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
bg.inputs["Strength"].default_value = 1

# Render
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = True
