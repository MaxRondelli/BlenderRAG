import bpy
import bmesh
import math
import random

# Pulisci la scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri del tappeto circolare
raggio = 1.5  # metri
numero_strisce = 12
spessore = 0.03

# Crea il mesh base del tappeto circolare
bpy.ops.mesh.primitive_circle_add(radius=raggio, vertices=64, location=(0, 0, 0))
tappeto = bpy.context.active_object
tappeto.name = "Tappeto_Circolare_Intrecciato"

# Riempi il cerchio - RIDOTTO per evitare crash
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.fill()
bpy.ops.mesh.subdivide(number_cuts=5)  # RIDOTTO da 80 a 5
bpy.ops.object.mode_set(mode='OBJECT')

# Aggiungi un modificatore Solidify per dare spessore
solidify = tappeto.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = spessore
solidify.offset = 0

# Aggiungi un modificatore Displacement per l'intreccio
disp = tappeto.modifiers.new(name="Displacement", type='DISPLACE')
disp.strength = 0.008

# Crea la texture per il displacement (simula l'intreccio)
texture_intreccio = bpy.data.textures.new('Texture_Intreccio', type='WOOD')
texture_intreccio.noise_scale = 1.5
disp.texture = texture_intreccio

# Crea i materiali per le strisce (versione compatibile)
def crea_materiale_striscia_compatibile(nome, colore_base, roughness=0.8):
    mat = bpy.data.materials.new(name=nome)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Nodo output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    # Nodo Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Base Color'].default_value = colore_base
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = 0.0
    
    # Nodo Coordinate Texture
    coord = nodes.new(type='ShaderNodeTexCoord')
    coord.location = (-600, 0)
    
    # Texture Wave per pattern intrecciato
    wave1 = nodes.new(type='ShaderNodeTexWave')
    wave1.location = (-400, 150)
    wave1.inputs['Scale'].default_value = 25.0
    wave1.inputs['Distortion'].default_value = 2.0
    wave1.wave_profile = 'TRI'
    
    wave2 = nodes.new(type='ShaderNodeTexWave')
    wave2.location = (-400, -50)
    wave2.inputs['Scale'].default_value = 25.0
    wave2.inputs['Distortion'].default_value = 2.0
    wave2.wave_profile = 'SIN'
    
    # Math node per combinare le waves
    math_add = nodes.new(type='ShaderNodeMath')
    math_add.location = (-200, 50)
    math_add.operation = 'ADD'
    
    # Color Ramp per controllare la variazione
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-50, 50)
    color_ramp.color_ramp.elements[0].position = 0.4
    color_ramp.color_ramp.elements[1].position = 0.6
    
    # MixRGB per variare il colore - CORRETTO
    mix = nodes.new(type='ShaderNodeMixRGB')
    mix.location = (0, 0)
    mix.blend_type = 'MIX'
    mix.inputs['Color1'].default_value = colore_base  # CORRETTO: era inputs[6]
    colore_scuro = (colore_base[0] * 0.7, colore_base[1] * 0.7, colore_base[2] * 0.7, 1.0)
    mix.inputs['Color2'].default_value = colore_scuro  # CORRETTO: era inputs[7]
    
    # Texture Noise per micro-dettagli
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-400, -250)
    noise.inputs['Scale'].default_value = 180.0
    noise.inputs['Detail'].default_value = 12.0
    
    # Bump per texture intrecciata
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (100, -200)
    bump.inputs['Strength'].default_value = 0.4
    
    # Collegamenti
    links = mat.node_tree.links
    links.new(coord.outputs['Object'], wave1.inputs['Vector'])
    links.new(coord.outputs['Object'], wave2.inputs['Vector'])
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(wave1.outputs['Fac'], math_add.inputs[0])
    links.new(wave2.outputs['Fac'], math_add.inputs[1])
    links.new(math_add.outputs['Value'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], mix.inputs['Fac'])
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Crea i materiali marrone e beige
mat_marrone = crea_materiale_striscia_compatibile("Striscia_Marrone", (0.4, 0.25, 0.15, 1.0), 0.85)
mat_beige = crea_materiale_striscia_compatibile("Striscia_Beige", (0.7, 0.55, 0.4, 1.0), 0.8)

# Assegna i materiali al tappeto
if len(tappeto.data.materials) == 0:
    tappeto.data.materials.append(mat_marrone)
    tappeto.data.materials.append(mat_beige)
else:
    tappeto.data.materials[0] = mat_marrone
    if len(tappeto.data.materials) < 2:
        tappeto.data.materials.append(mat_beige)
    else:
        tappeto.data.materials[1] = mat_beige

# Crea le strisce concentriche
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Calcola quali facce appartengono a quale striscia concentrica
raggio_striscia = raggio / numero_strisce

for face in tappeto.data.polygons:
    # Calcola il centro della faccia
    centro_x = sum([tappeto.data.vertices[v].co.x for v in face.vertices]) / len(face.vertices)
    centro_y = sum([tappeto.data.vertices[v].co.y for v in face.vertices]) / len(face.vertices)
    
    # Calcola la distanza dal centro
    distanza = math.sqrt(centro_x**2 + centro_y**2)
    
    # Determina a quale anello concentrico appartiene
    indice_anello = int(distanza / raggio_striscia)
    
    # Alterna tra marrone (0) e beige (1)
    if indice_anello % 2 == 0:
        face.material_index = 0  # Marrone
    else:
        face.material_index = 1  # Beige

# Aggiungi un modificatore Subdivision Surface per maggiore realismo
subsurf = tappeto.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Posiziona una luce e una camera per visualizzare meglio
bpy.ops.object.light_add(type='SUN', location=(4, 4, 8))
luce = bpy.context.active_object
luce.data.energy = 3.5

bpy.ops.object.camera_add(location=(2.5, -3.5, 3.2))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(62), 0, math.radians(35))
bpy.context.scene.camera = camera

# Imposta il motore di rendering su Cycles per migliore qualità
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("=" * 50)
print("Tappeto circolare intrecciato creato con successo!")
print("=" * 50)
print("Raggio: {} metri".format(raggio))
print("Anelli concentrici: {} (alternati marrone e beige)".format(numero_strisce))
print("")
print("ISTRUZIONI:")
print("1. Premi Z nel viewport e seleziona 'Material Preview' o 'Rendered'")
print("2. Per renderizzare l'immagine finale: premi F12")
print("3. Puoi modificare i parametri all'inizio dello script")
print("=" * 50)