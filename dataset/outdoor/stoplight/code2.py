import bpy
import math

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# BASE
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0.1))
base = bpy.context.active_object
base.scale = (0.5, 0.3, 0.05)

mat_base = bpy.data.materials.new(name="BaseBlack")
mat_base.use_nodes = True
bsdf = mat_base.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs['Roughness'].default_value = 0.4
base.data.materials.append(mat_base)

# PALO
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=2.5, location=(0, 0, 1.35))
palo = bpy.context.active_object

mat_palo = bpy.data.materials.new(name="PaloGrigio")
mat_palo.use_nodes = True
bsdf_palo = mat_palo.node_tree.nodes["Principled BSDF"]
bsdf_palo.inputs['Base Color'].default_value = (0.6, 0.6, 0.65, 1)
bsdf_palo.inputs['Metallic'].default_value = 0.7
bsdf_palo.inputs['Roughness'].default_value = 0.3
palo.data.materials.append(mat_palo)

# CORPO PRINCIPALE - Cilindrico invece di cubo
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.4, location=(0, 0, 2.9))
corpo = bpy.context.active_object

# Materiale argentato metallico per il corpo
mat_corpo = bpy.data.materials.new(name="CorpoArgentato")
mat_corpo.use_nodes = True
bsdf_corpo = mat_corpo.node_tree.nodes["Principled BSDF"]
bsdf_corpo.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1)
bsdf_corpo.inputs['Roughness'].default_value = 0.1
bsdf_corpo.inputs['Metallic'].default_value = 0.9
corpo.data.materials.append(mat_corpo)

# LUCI CON VISIERE - Colore ambra caldo per tutte
luci_data = [
    ("Rosso", (1.0, 0.4, 0.1), 3.15),
    ("Giallo", (1.0, 0.5, 0.2), 2.9),
    ("Verde", (1.0, 0.6, 0.3), 2.65)
]

for nome, colore, z_pos in luci_data:
    # VISIERA sopra la luce - argentata
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.08, location=(0, 0.08, z_pos + 0.08))
    visiera = bpy.context.active_object
    visiera.rotation_euler = (math.radians(90), 0, 0)
    visiera.scale = (1, 0.6, 1)
    visiera.data.materials.append(mat_corpo)
    
    # Luce (sfera)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.075, location=(0, 0.02, z_pos))
    luce = bpy.context.active_object
    
    # Materiale emissivo vetro con colore ambra caldo
    mat_luce = bpy.data.materials.new(name=f"Mat_{nome}")
    mat_luce.use_nodes = True
    nodes = mat_luce.node_tree.nodes
    links = mat_luce.node_tree.links
    nodes.clear()
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mix = nodes.new('ShaderNodeMixShader')
    emission = nodes.new('ShaderNodeEmission')
    glass = nodes.new('ShaderNodeBsdfPrincipled')
    
    emission.inputs['Color'].default_value = (*colore, 1)
    emission.inputs['Strength'].default_value = 15.0
    glass.inputs['Base Color'].default_value = (*colore, 1)
    glass.inputs['IOR'].default_value = 1.45
    glass.inputs['Alpha'].default_value = 0.8
    glass.inputs['Roughness'].default_value = 0.0
    
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(glass.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    mix.inputs['Fac'].default_value = 0.7
    
    luce.data.materials.append(mat_luce)
    
    # Anello argentato
    bpy.ops.mesh.primitive_torus_add(major_radius=0.095, minor_radius=0.012, location=(0, 0.02, z_pos))
    anello = bpy.context.active_object
    anello.rotation_euler = (math.radians(90), 0, 0)
    anello.data.materials.append(mat_corpo)

# CAMERA
bpy.ops.object.camera_add(location=(1.5, -1.8, 2.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(70), 0, math.radians(40))
bpy.context.scene.camera = camera

# LUCI
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0

bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
area = bpy.context.active_object
area.data.energy = 150

# WORLD HDRI (opzionale per realismo)
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Strength'].default_value = 0.3

# RENDER
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.view_transform = 'Filmic'

print("Semaforo moderno argentato creato!")


