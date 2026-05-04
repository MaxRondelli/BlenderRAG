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

# Base palo (più larga, cromo)
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.1, location=(0, 0, 0.05))
base = bpy.context.active_object
mat_cromo = bpy.data.materials.new("CromoBase")
mat_cromo.use_nodes = True
bsdf_cromo = mat_cromo.node_tree.nodes["Principled BSDF"]
bsdf_cromo.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
bsdf_cromo.inputs["Metallic"].default_value = 1.0
bsdf_cromo.inputs["Roughness"].default_value = 0.1
base.data.materials.append(mat_cromo)

# Palo principale (nero metallico, leggermente conico)
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.3, location=(0, 0.035, 1.25))
palo = bpy.context.active_object
palo.scale[0] = 0.9  # Cono leggero
palo.scale[1] = 0.9
mat_nero_cromo = bpy.data.materials.new("NeroMetallicoChrome")
mat_nero_cromo.use_nodes = True
bsdf_nero = mat_nero_cromo.node_tree.nodes["Principled BSDF"]
bsdf_nero.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)
bsdf_nero.inputs["Metallic"].default_value = 0.9
bsdf_nero.inputs["Roughness"].default_value = 0.15
palo.data.materials.append(mat_nero_cromo)

# Supporti orizzontali (2 staffe modernizzate con bordi arrotondati)
for i, z_pos in enumerate([2.3, 2.5]):
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0, 0.035, z_pos))
    staffa = bpy.context.active_object
    staffa.scale = (0.7, 1.3, 0.4)
    # Aggiungiamo subdivisions per arrotondare
    modifier = staffa.modifiers.new(name="Subsurf", type="SUBSURF")
    modifier.levels = 2
    modifier.render_levels = 2
    staffa.data.materials.append(mat_cromo)

# Bordo bianco retro
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.48, depth=0.02, location=(0, 0.015, 2.6))
bordo = bpy.context.active_object
bordo.rotation_euler = (math.radians(90), 0, 0)
mat_bianco = bpy.data.materials.new("Bianco")
mat_bianco.use_nodes = True
bsdf_bianco = mat_bianco.node_tree.nodes["Principled BSDF"]
bsdf_bianco.inputs["Base Color"].default_value = (1, 1, 1, 1)
bordo.data.materials.append(mat_bianco)

# Segnale STOP (burgundy profondo)
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.45, depth=0.03, location=(0, 0, 2.6))
stop_sign = bpy.context.active_object
stop_sign.rotation_euler = (math.radians(90), 0, 0)
mat_burgundy = bpy.data.materials.new("BurgundyStop")
mat_burgundy.use_nodes = True
bsdf_burgundy = mat_burgundy.node_tree.nodes["Principled BSDF"]
bsdf_burgundy.inputs["Base Color"].default_value = (0.55, 0.12, 0.2, 1)
bsdf_burgundy.inputs["Roughness"].default_value = 0.25
stop_sign.data.materials.append(mat_burgundy)

# Testo STOP (oro)
bpy.ops.object.text_add(location=(0, -0.035, 2.6))
text_obj = bpy.context.active_object
text_obj.data.body = "STOP"
text_obj.data.size = 0.35
text_obj.data.extrude = 0.015
text_obj.rotation_euler = (math.radians(90), 0, 0)
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'
mat_oro = bpy.data.materials.new("Oro")
mat_oro.use_nodes = True
bsdf_oro = mat_oro.node_tree.nodes["Principled BSDF"]
bsdf_oro.inputs["Base Color"].default_value = (1.0, 0.84, 0.0, 1)
bsdf_oro.inputs["Metallic"].default_value = 0.8
bsdf_oro.inputs["Roughness"].default_value = 0.2
text_obj.data.materials.append(mat_oro)

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
