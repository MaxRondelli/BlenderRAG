import bpy
import random
from mathutils import Vector

# Pulisci scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Crea icosphere
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1, location=(0, 0, 0))
rock = bpy.context.active_object
rock.name = "Rock"

# Deforma per forma irregolare PRIMA dei modifiers
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(1.3, 1.0, 0.8))
bpy.ops.mesh.select_random(ratio=0.6, seed=random.randint(0, 100))
bpy.ops.transform.translate(value=(
    random.uniform(-0.2, 0.2),
    random.uniform(-0.2, 0.2),
    random.uniform(-0.1, 0.1)
))
bpy.ops.object.mode_set(mode='OBJECT')

# Aggiungi subdivision surface (aumentato per curve più organiche)
subsurf = rock.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Edge split per spigoli vivi
edge_split = rock.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
edge_split.split_angle = 0.523599  # ~30 gradi

# Smooth by Angle per Blender 4.x (sostituisce auto_smooth)
smooth = rock.modifiers.new(name="SmoothByAngle", type='SMOOTH')

smooth.iterations = 2

# Displacement primario per forma grezza - ridotto del 40%
displace1 = rock.modifiers.new(name="Displace1", type='DISPLACE')
displace1.strength = 0.36
displace1.mid_level = 0.5
tex1 = bpy.data.textures.new('RockDisplace1', type='VORONOI')
tex1.noise_scale = 1.5
tex1.distance_metric = 'DISTANCE'
displace1.texture = tex1

# Displacement secondario per parti taglienti - ridotto del 40%
displace2 = rock.modifiers.new(name="Displace2", type='DISPLACE')
displace2.strength = 0.21
displace2.mid_level = 0.5
tex2 = bpy.data.textures.new('RockDisplace2', type='VORONOI')
tex2.noise_scale = 3.0
tex2.distance_metric = 'MINKOVSKY'
displace2.texture = tex2

# Displacement terzo per micro-dettagli - ridotto del 40%
displace3 = rock.modifiers.new(name="Displace3", type='DISPLACE')
displace3.strength = 0.06
displace3.mid_level = 0.5
tex3 = bpy.data.textures.new('RockDisplace3', type='STUCCI')
tex3.noise_scale = 12.0
displace3.texture = tex3

# Materiale PBR con variazioni di colore carbone-ambra-rame
mat = bpy.data.materials.new(name="RockMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Shader principale
output = nodes.new(type='ShaderNodeOutputMaterial')
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Roughness'].default_value = 0.85
bsdf.inputs['Metallic'].default_value = 0.1

# Coordinate
coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Scale'].default_value = (3, 3, 3)

# Colore base carbone scuro
noise_base = nodes.new(type='ShaderNodeTexNoise')
noise_base.inputs['Scale'].default_value = 4.0
noise_base.inputs['Detail'].default_value = 8.0

ramp_base = nodes.new(type='ShaderNodeValToRGB')
ramp_base.color_ramp.elements[0].color = (0.15, 0.15, 0.18, 1)  # Carbone scuro
ramp_base.color_ramp.elements[1].color = (0.25, 0.25, 0.28, 1)  # Carbone grigio

# Layer ambra calda
noise_amber = nodes.new(type='ShaderNodeTexNoise')
noise_amber.inputs['Scale'].default_value = 2.5
noise_amber.inputs['Detail'].default_value = 6.0

ramp_amber = nodes.new(type='ShaderNodeValToRGB')
ramp_amber.color_ramp.elements[0].position = 0.4
ramp_amber.color_ramp.elements[0].color = (0.45, 0.28, 0.12, 1)  # Ambra scura
ramp_amber.color_ramp.elements[1].position = 0.7
ramp_amber.color_ramp.elements[1].color = (0.65, 0.42, 0.18, 1)  # Ambra chiara

# Layer rame ossidato
voronoi = nodes.new(type='ShaderNodeTexVoronoi')
voronoi.inputs['Scale'].default_value = 6.0
voronoi.feature = 'DISTANCE_TO_EDGE'

ramp_copper = nodes.new(type='ShaderNodeValToRGB')
ramp_copper.color_ramp.elements[0].position = 0.3
ramp_copper.color_ramp.elements[0].color = (0.32, 0.18, 0.08, 1)  # Rame scuro
ramp_copper.color_ramp.elements[1].position = 0.5
ramp_copper.color_ramp.elements[1].color = (0.58, 0.32, 0.15, 1)  # Rame ossidato

# Mix colori: base + ambra
mix1 = nodes.new(type='ShaderNodeMix')
mix1.data_type = 'RGBA'


# Mix: precedente + rame
mix2 = nodes.new(type='ShaderNodeMix')
mix2.data_type = 'RGBA'


# Noise per bump più morbido
noise_bump1 = nodes.new(type='ShaderNodeTexNoise')
noise_bump1.inputs['Scale'].default_value = 8.0
noise_bump1.inputs['Detail'].default_value = 10.0

noise_bump = nodes.new(type='ShaderNodeTexNoise')
noise_bump.inputs['Scale'].default_value = 12.0
noise_bump.inputs['Detail'].default_value = 8.0

# Mix bump
mix_bump = nodes.new(type='ShaderNodeMix')
mix_bump.data_type = 'FLOAT'

bump = nodes.new(type='ShaderNodeBump')
bump.inputs['Strength'].default_value = 1.5
bump.inputs['Distance'].default_value = 0.04

# Collegamenti
links.new(coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_base.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_amber.inputs['Vector'])
links.new(mapping.outputs['Vector'], voronoi.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_bump1.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_bump.inputs['Vector'])



links.new(ramp_base.outputs['Color'], mix1.inputs['A'])
links.new(ramp_amber.outputs['Color'], mix1.inputs['B'])
links.new(mix1.outputs['Result'], mix2.inputs['A'])
links.new(ramp_copper.outputs['Color'], mix2.inputs['B'])
links.new(mix2.outputs['Result'], bsdf.inputs['Base Color'])


links.new(mix_bump.outputs['Result'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

rock.data.materials.append(mat)

# Posiziona nodi
output.location = (600, 0)
bsdf.location = (350, 0)
bump.location = (100, -300)
mix_bump.location = (-150, -300)
noise_bump1.location = (-400, -250)
noise_bump.location = (-400, -400)
mix2.location = (100, 200)
mix1.location = (-150, 250)
ramp_base.location = (-400, 300)
ramp_amber.location = (-400, 150)
ramp_copper.location = (-400, 0)
noise_base.location = (-650, 300)
noise_amber.location = (-650, 150)
voronoi.location = (-650, 0)
mapping.location = (-900, 200)
coord.location = (-1100, 200)

# Setup lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
sun = bpy.context.active_object
sun.data.energy = 3

# Camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.active_object
camera.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = camera

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("Rock weathered con colori carbone-ambra-rame generato!")
