import bpy
import math
import bmesh

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

# Base palo (più larga, grigio carbone scuro)
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.1, location=(0, 0, 0.05))
base = bpy.context.active_object
mat_grigio_scuro = bpy.data.materials.new("GrigioCarbone")
mat_grigio_scuro.use_nodes = True
bsdf_grigio_scuro = mat_grigio_scuro.node_tree.nodes["Principled BSDF"]
bsdf_grigio_scuro.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1)
bsdf_grigio_scuro.inputs["Metallic"].default_value = 0.85
bsdf_grigio_scuro.inputs["Roughness"].default_value = 0.35
base.data.materials.append(mat_grigio_scuro)

# Palo principale (grigio carbone metallico, leggermente conico)
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.3, location=(0, 0.035, 1.25))
palo = bpy.context.active_object
palo.scale[0] = 0.9
palo.scale[1] = 0.9
mat_palo_scuro = bpy.data.materials.new("PaloCarbone")
mat_palo_scuro.use_nodes = True
bsdf_palo_scuro = mat_palo_scuro.node_tree.nodes["Principled BSDF"]
bsdf_palo_scuro.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1)
bsdf_palo_scuro.inputs["Metallic"].default_value = 0.8
bsdf_palo_scuro.inputs["Roughness"].default_value = 0.3
palo.data.materials.append(mat_palo_scuro)

# Supporti orizzontali più robusti con bordi arrotondati
for i, z_pos in enumerate([2.3, 2.5]):
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0.035, z_pos))
    staffa = bpy.context.active_object
    staffa.scale = (0.7, 1.4, 0.4)
    
    # Aggiungi modificatore Bevel per arrotondare i bordi
    bevel_mod = staffa.modifiers.new(name="Bevel", type="BEVEL")
    bevel_mod.width = 0.005
    bevel_mod.segments = 3
    
    # Aggiungi Subdivision per smoothness
    subsurf_mod = staffa.modifiers.new(name="Subsurf", type="SUBSURF")
    subsurf_mod.levels = 1
    
    staffa.data.materials.append(mat_grigio_scuro)

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
bsdf_burgundy.inputs["Base Color"].default_value = (0.5, 0.1, 0.15, 1)
bsdf_burgundy.inputs["Roughness"].default_value = 0.25
stop_sign.data.materials.append(mat_burgundy)

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

