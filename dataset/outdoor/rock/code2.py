import bpy
import random
from mathutils import Vector

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Crea icosphere
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1, location=(0, 0, 0))
rock = bpy.context.active_object
rock.name = "WeatheredRock"

# Deforma per forma irregolare PRIMA dei modifiers - più aggressiva
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(1.5, 1.2, 0.7))
bpy.ops.mesh.select_random(ratio=0.8, seed=random.randint(0, 100))
bpy.ops.transform.translate(value=(
    random.uniform(-0.4, 0.4),
    random.uniform(-0.4, 0.4),
    random.uniform(-0.3, 0.3)
))
bpy.ops.object.mode_set(mode='OBJECT')

# Aggiungi subdivision surface (ridotto per mantenere spigoli)
subsurf = rock.modifiers.new(name="Subdivision", type="SUBSURF")
subsurf.levels = 1
subsurf.render_levels = 2

# Edge split per spigoli più taglienti
edge_split = rock.modifiers.new(name="EdgeSplit", type="EDGE_SPLIT")
edge_split.split_angle = 0.349066  # ~20 gradi per spigoli più definiti

# Smooth by Angle per Blender 4.x
smooth = rock.modifiers.new(name="SmoothByAngle", type="SMOOTH")
smooth.iterations = 1

# Displacement primario più aggressivo per fratture profonde
displace1 = rock.modifiers.new(name="Displace1", type="DISPLACE")
displace1.strength = 1.2
displace1.mid_level = 0.4
tex1 = bpy.data.textures.new('WeatheredDisplace1', type='VORONOI')
tex1.noise_scale = 2.2
tex1.distance_metric = 'DISTANCE'
displace1.texture = tex1

# Displacement secondario per erosione angolare
displace2 = rock.modifiers.new(name="Displace2", type="DISPLACE")
displace2.strength = 0.8
displace2.mid_level = 0.3
tex2 = bpy.data.textures.new('WeatheredDisplace2', type='VORONOI')
tex2.noise_scale = 4.5
tex2.distance_metric = 'MINKOVSKY'
displace2.texture = tex2

# Displacement terzo per crepe profonde
displace3 = rock.modifiers.new(name="Displace3", type="DISPLACE")
displace3.strength = 0.4
displace3.mid_level = 0.2
tex3 = bpy.data.textures.new('WeatheredDisplace3', type='STUCCI')
tex3.noise_scale = 8.0
displace3.texture = tex3

# Displacement aggiuntivo per erosione fine
displace4 = rock.modifiers.new(name="Displace4", type="DISPLACE")
displace4.strength = 0.15
displace4.mid_level = 0.5
tex4 = bpy.data.textures.new('WeatheredDisplace4', type='STUCCI')
tex4.noise_scale = 20.0
displace4.texture = tex4

# Materiale PBR con toni più scuri e terrosi
mat = bpy.data.materials.new(name="WeatheredRockMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Shader principale
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Roughness'].default_value = 0.98
bsdf.inputs['Metallic'].default_value = 0.1

# Coordinate
coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Scale'].default_value = (4, 4, 4)

# Colore base grigio carbone scuro
noise_base = nodes.new(type='ShaderNodeTexNoise')
noise_base.inputs['Scale'].default_value = 5.0
noise_base.inputs['Detail'].default_value = 10.0

ramp_base = nodes.new(type='ShaderNodeValToRGB')
ramp_base.color_ramp.elements[0].color = (0.15, 0.15, 0.12, 1)  # Carbone molto scuro
ramp_base.color_ramp.elements[1].color = (0.35, 0.32, 0.28, 1)  # Grigio scuro terroso

# Layer ossido di ferro rossastro-marrone
noise_rust = nodes.new(type='ShaderNodeTexNoise')
noise_rust.inputs['Scale'].default_value = 3.2
noise_rust.inputs['Detail'].default_value = 8.0

ramp_rust = nodes.new(type='ShaderNodeValToRGB')
ramp_rust.color_ramp.elements[0].position = 0.3
ramp_rust.color_ramp.elements[0].color = (0.42, 0.18, 0.08, 1)  # Rosso-marrone ossido
ramp_rust.color_ramp.elements[1].position = 0.8
ramp_rust.color_ramp.elements[1].color = (0.65, 0.28, 0.15, 1)  # Ruggine rossastra

# Layer macchie carbone profondo
voronoi = nodes.new(type='ShaderNodeTexVoronoi')
voronoi.inputs['Scale'].default_value = 8.0
voronoi.feature = 'DISTANCE_TO_EDGE'

ramp_dark = nodes.new(type='ShaderNodeValToRGB')
ramp_dark.color_ramp.elements[0].position = 0.2
ramp_dark.color_ramp.elements[0].color = (0.08, 0.08, 0.06, 1)  # Quasi nero carbone
ramp_dark.color_ramp.elements[1].position = 0.6
ramp_dark.color_ramp.elements[1].color = (0.22, 0.20, 0.16, 1)  # Grigio carbone

# Layer erosione terrosa
noise_earth = nodes.new(type='ShaderNodeTexNoise')
noise_earth.inputs['Scale'].default_value = 6.5
noise_earth.inputs['Detail'].default_value = 12.0

ramp_earth = nodes.new(type='ShaderNodeValToRGB')
ramp_earth.color_ramp.elements[0].color = (0.25, 0.18, 0.12, 1)  # Marrone terra scuro
ramp_earth.color_ramp.elements[1].color = (0.38, 0.25, 0.18, 1)  # Terra rossastra

# Mix colori: base + ossido ferro
mix1 = nodes.new(type='ShaderNodeMix')
mix1.data_type = 'RGBA'


# Mix: precedente + macchie carbone
mix2 = nodes.new(type='ShaderNodeMix')
mix2.data_type = 'RGBA'


# Mix: precedente + erosione terrosa
mix3 = nodes.new(type='ShaderNodeMix')
mix3.data_type = 'RGBA'


# Noise per bump intenso
noise_bump1 = nodes.new(type='ShaderNodeTexNoise')
noise_bump1.inputs['Scale'].default_value = 15.0
noise_bump1.inputs['Detail'].default_value = 15.0

noise_bump2 = nodes.new(type='ShaderNodeTexNoise')
noise_bump2.inputs['Scale'].default_value = 25.0
noise_bump2.inputs['Detail'].default_value = 12.0

# Mix bump per dettagli profondi
mix_bump = nodes.new(type='ShaderNodeMix')
mix_bump.data_type = 'FLOAT'


bump = nodes.new(type='ShaderNodeBump')
bump.inputs['Strength'].default_value = 3.5
bump.inputs['Distance'].default_value = 0.08

# Collegamenti
links.new(coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_base.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_rust.inputs['Vector'])
links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_earth.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_bump1.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_bump2.inputs['Vector'])


links.new(ramp_base.outputs['Color'], mix1.inputs['A'])
links.new(ramp_rust.outputs['Color'], mix1.inputs['B'])
links.new(mix1.outputs['Result'], mix2.inputs['A'])
links.new(ramp_dark.outputs['Color'], mix2.inputs['B'])
links.new(mix2.outputs['Result'], mix3.inputs['A'])
links.new(ramp_earth.outputs['Color'], mix3.inputs['B'])
links.new(mix3.outputs['Result'], bsdf.inputs['Base Color'])


links.new(mix_bump.outputs['Result'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

rock.data.materials.append(mat)

# Posiziona nodi
output.location = (800, 0)
bsdf.location = (550, 0)
bump.location = (300, -400)
mix_bump.location = (50, -400)
noise_bump1.location = (-200, -350)
noise_bump2.location = (-200, -500)
mix3.location = (300, 200)
mix2.location = (50, 250)
mix1.location = (-200, 300)
ramp_base.location = (-450, 350)
ramp_rust.location = (-450, 200)
ramp_dark.location = (-450, 50)
ramp_earth.location = (-450, -100)
noise_base.location = (-700, 350)
noise_rust.location = (-700, 200)
voronoi.location = (-700, 50)
noise_earth.location = (-700, -100)
mapping.location = (-950, 150)
coord.location = (-1150, 150)

# Setup lighting per enfatizzare le fratture
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
sun = bpy.context.active_object
sun.data.energy = 4
sun.rotation_euler = (0.3, 0.5, 0)

# Luce di riempimento per dettagli nelle ombre
bpy.ops.object.light_add(type='AREA', location=(-3, -2, 3))
fill_light = bpy.context.active_object
fill_light.data.energy = 1.5
fill_light.data.size = 2

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = camera

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("Roccia erosa e frammentata generata!")

