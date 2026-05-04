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

# Base palo (più alta, più cilindrica, brushed metal)
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.2, location=(0, 0, 0.1))
base = bpy.context.active_object
mat_brushed = bpy.data.materials.new("BrushedMetal")
mat_brushed.use_nodes = True
bsdf_brushed = mat_brushed.node_tree.nodes["Principled BSDF"]
bsdf_brushed.inputs["Base Color"].default_value = (0.5, 0.5, 0.55, 1)
bsdf_brushed.inputs["Metallic"].default_value = 0.9
bsdf_brushed.inputs["Roughness"].default_value = 0.25
base.data.materials.append(mat_brushed)

# Palo principale (dark charcoal gray, high metallic)
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.3, location=(0, 0.035, 1.25))
palo = bpy.context.active_object
palo.scale[0] = 0.9
palo.scale[1] = 0.9
mat_charcoal = bpy.data.materials.new("CharcoalMetal")
mat_charcoal.use_nodes = True
bsdf_charcoal = mat_charcoal.node_tree.nodes["Principled BSDF"]
bsdf_charcoal.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1)
bsdf_charcoal.inputs["Metallic"].default_value = 0.95
bsdf_charcoal.inputs["Roughness"].default_value = 0.2
palo.data.materials.append(mat_charcoal)

# Supporti orizzontali (2 staffe)
for i, z_pos in enumerate([2.3, 2.5]):
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0, 0.035, z_pos))
    staffa = bpy.context.active_object
    staffa.scale = (0.6, 1.2, 0.3)
    staffa.data.materials.append(mat_brushed)

# Bordo bianco retro (hexagonal)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.48, depth=0.02, location=(0, 0.015, 2.6))
bordo = bpy.context.active_object
bordo.rotation_euler = (math.radians(90), 0, 0)
mat_bianco = bpy.data.materials.new("Bianco")
mat_bianco.use_nodes = True
bsdf_bianco = mat_bianco.node_tree.nodes["Principled BSDF"]
bsdf_bianco.inputs["Base Color"].default_value = (1, 1, 1, 1)
bordo.data.materials.append(mat_bianco)

# Segnale STOP (hexagonal, darker crimson, matte)
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.45, depth=0.03, location=(0, 0, 2.6))
stop_sign = bpy.context.active_object
stop_sign.rotation_euler = (math.radians(90), 0, 0)
mat_crimson = bpy.data.materials.new("CrimsonMatte")
mat_crimson.use_nodes = True
bsdf_crimson = mat_crimson.node_tree.nodes["Principled BSDF"]
bsdf_crimson.inputs["Base Color"].default_value = (0.6, 0.02, 0.08, 1)
bsdf_crimson.inputs["Metallic"].default_value = 0.0
bsdf_crimson.inputs["Roughness"].default_value = 0.9
stop_sign.data.materials.append(mat_crimson)

# Testo STOP
bpy.ops.object.text_add(location=(0, -0.035, 2.6))
text_obj = bpy.context.active_object
text_obj.data.body = "STOP"
text_obj.data.size = 0.35
text_obj.data.extrude = 0.015
text_obj.rotation_euler = (math.radians(90), 0, 0)
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'
text_obj.data.materials.append(mat_bianco)

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


