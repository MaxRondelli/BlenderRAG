import bpy
import math

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# MATERIALE PIETRA SCURA
mat_dark_stone = bpy.data.materials.new(name="DarkStone")
mat_dark_stone.use_nodes = True
nodes = mat_dark_stone.node_tree.nodes
links = mat_dark_stone.node_tree.links

# Rimuovi nodo default
nodes.clear()

# Crea nodi per texture pietra scura
texture_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
noise1 = nodes.new(type='ShaderNodeTexNoise')
noise2 = nodes.new(type='ShaderNodeTexNoise')
voronoi = nodes.new(type='ShaderNodeTexVoronoi')
color_ramp = nodes.new(type='ShaderNodeValToRGB')
mix_rgb = nodes.new(type='ShaderNodeMixRGB')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Posiziona nodi
texture_coord.location = (-800, 0)
mapping.location = (-600, 0)
noise1.location = (-400, 200)
noise2.location = (-400, -100)
voronoi.location = (-400, -400)
color_ramp.location = (-200, 0)
mix_rgb.location = (0, 0)
bsdf.location = (300, 0)
output.location = (500, 0)

# Configura noise per venature
noise1.inputs['Scale'].default_value = 4.0
noise1.inputs['Detail'].default_value = 10.0
noise2.inputs['Scale'].default_value = 18.0
voronoi.inputs['Scale'].default_value = 25.0

# Configura color ramp per colori pietra scura (grigio carbone con venature nere)
color_ramp.color_ramp.elements[0].color = (0.15, 0.15, 0.15, 1.0)
color_ramp.color_ramp.elements[1].color = (0.35, 0.35, 0.35, 1.0)

# Collegamenti
links.new(texture_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])

links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Configura BSDF per pietra
bsdf.inputs['Roughness'].default_value = 0.4
bsdf.inputs['Metallic'].default_value = 0.0

# MATERIALE ACQUA BLU-VERDE
mat_water = bpy.data.materials.new(name="Water")
mat_water.use_nodes = True
bsdf_water = mat_water.node_tree.nodes["Principled BSDF"]
bsdf_water.inputs['Base Color'].default_value = (0.1, 0.4, 0.5, 1.0)
bsdf_water.inputs['Metallic'].default_value = 0.9
bsdf_water.inputs['Roughness'].default_value = 0.05
bsdf_water.inputs['Alpha'].default_value = 0.85
bsdf_water.inputs['IOR'].default_value = 1.33

# BASE INFERIORE
bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=0.25, location=(0, 0, 0.125))
base_bottom = bpy.context.active_object
base_bottom.name = "Base_Bottom"
base_bottom.data.materials.append(mat_dark_stone)

# Aggiungi modificatore Subdivision per forme più organiche
base_mod = base_bottom.modifiers.new(name="Subsurf", type="SUBSURF")
base_mod.levels = 2

# ANELLO INTERMEDIO
bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=0.15, location=(0, 0, 0.325))
mid_ring = bpy.context.active_object
mid_ring.name = "Mid_Ring"
mid_ring.data.materials.append(mat_dark_stone)

# Aggiungi modificatore per forme più arrotondate
mid_mod = mid_ring.modifiers.new(name="Subsurf", type="SUBSURF")
mid_mod.levels = 2

# PIEDISTALLO CENTRALE
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=1.4, location=(0, 0, 1.1))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal"
pedestal.data.materials.append(mat_dark_stone)

# Forma più organica per il piedistallo
ped_mod = pedestal.modifiers.new(name="Subsurf", type="SUBSURF")
ped_mod.levels = 1

# VASCA PRINCIPALE - base
bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.2, location=(0, 0, 1.85))
bowl_base = bpy.context.active_object
bowl_base.name = "Bowl_Base"
bowl_base.data.materials.append(mat_dark_stone)

# Forma più arrotondata per la base della vasca
bowl_base_mod = bowl_base.modifiers.new(name="Subsurf", type="SUBSURF")
bowl_base_mod.levels = 2

# VASCA PRINCIPALE - bordo
bpy.ops.mesh.primitive_torus_add(major_radius=1.8, minor_radius=0.4, location=(0, 0, 2.0))
bowl = bpy.context.active_object
bowl.name = "Bowl"
bowl.scale[2] = 0.7
bowl.data.materials.append(mat_dark_stone)

# Forma più organica per il bordo
bowl_mod = bowl.modifiers.new(name="Subsurf", type="SUBSURF")
bowl_mod.levels = 2

# ACQUA nella vasca
bpy.ops.mesh.primitive_cylinder_add(radius=1.7, depth=0.05, location=(0, 0, 1.95))
water_pool = bpy.context.active_object
water_pool.name = "Water_Pool"
water_pool.data.materials.append(mat_water)

# Forma più naturale per l'acqua
water_mod = water_pool.modifiers.new(name="Subsurf", type="SUBSURF")
water_mod.levels = 1

# CAMERA
bpy.ops.object.camera_add(location=(5, -5, 3))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = camera

print("Fontana con pietra scura e forme organiche creata!")

