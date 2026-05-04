import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile nordico (stavkirke)
larghezza_base = 2.5
altezza_primo = 5.0
altezza_secondo = 4.0
altezza_terzo = 3.0

# Primo livello ottagonale
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=larghezza_base/2, depth=altezza_primo, location=(0, 0, altezza_primo/2))
primo_livello = bpy.context.active_object
primo_livello.name = "Primo_Livello_Ottagonale"

# Tetto primo livello con spioventi ripidi
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=larghezza_base/1.5, depth=1.2, location=(0, 0, altezza_primo + 0.6))
tetto_primo = bpy.context.active_object
tetto_primo.name = "Tetto_Primo_Livello"

# Secondo livello più piccolo
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=larghezza_base/2.5, depth=altezza_secondo, location=(0, 0, altezza_primo + 1.2 + altezza_secondo/2))
secondo_livello = bpy.context.active_object
secondo_livello.name = "Secondo_Livello"

# Tetto secondo livello
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=larghezza_base/2.2, depth=1.0, location=(0, 0, altezza_primo + 1.2 + altezza_secondo + 0.5))
tetto_secondo = bpy.context.active_object
tetto_secondo.name = "Tetto_Secondo_Livello"

# Terzo livello (cella campanaria)
z_terzo = altezza_primo + 1.2 + altezza_secondo + 1.0
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=larghezza_base/3.5, depth=altezza_terzo, location=(0, 0, z_terzo + altezza_terzo/2))
terzo_livello = bpy.context.active_object
terzo_livello.name = "Cella_Campanaria"

# Aperture ad arco per le campane
num_aperture = 8
for i in range(num_aperture):
    angolo = (2 * math.pi / num_aperture) * i
    raggio = larghezza_base/3.5
    x = math.cos(angolo) * (raggio + 0.1)
    y = math.sin(angolo) * (raggio + 0.1)
    z = z_terzo + altezza_terzo/2
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.2, location=(x, y, z))
    apertura = bpy.context.active_object
    apertura.rotation_euler[1] = math.pi/2
    apertura.rotation_euler[0] = angolo
    apertura.name = f"Apertura_Campana_{i+1}"

# Tetto finale a guglia ripida
altezza_guglia = 2.5
bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=larghezza_base/3, depth=altezza_guglia, location=(0, 0, z_terzo + altezza_terzo + altezza_guglia/2))
guglia = bpy.context.active_object
guglia.name = "Guglia_Finale"

# Croci decorative sulle estremità dei tetti (tipiche nordiche)
# Croce principale sommitale
z_croce_top = z_terzo + altezza_terzo + altezza_guglia
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_croce_top + 0.35))
croce_v_top = bpy.context.active_object
croce_v_top.scale = (0.04, 0.04, 0.7)
croce_v_top.name = "Croce_Verticale_Top"

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_croce_top + 0.5))
croce_o_top = bpy.context.active_object
croce_o_top.scale = (0.4, 0.04, 0.04)
croce_o_top.name = "Croce_Orizzontale_Top"

# Draghi vichinghi decorativi (teste stilizzate) agli angoli dei tetti
for i_tetto, z_tetto in enumerate([altezza_primo + 1.2, altezza_primo + 1.2 + altezza_secondo + 1.0]):
    for j in range(4):
        angolo = (math.pi/2) * j
        raggio_tetto = larghezza_base/(1.5 if i_tetto == 0 else 2.2)
        x = math.cos(angolo) * raggio_tetto
        y = math.sin(angolo) * raggio_tetto
        
        # Testa di drago stilizzata
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.1, depth=0.3, location=(x, y, z_tetto))
        drago = bpy.context.active_object
        drago.rotation_euler[1] = math.pi/2
        drago.rotation_euler[0] = angolo
        drago.name = f"Drago_Decorativo_T{i_tetto+1}_{j+1}"

# Supporti a X (tipici delle stavkirke)
num_supporti = 8
for i in range(num_supporti):
    angolo = (2 * math.pi / num_supporti) * i
    raggio = larghezza_base/2
    x = math.cos(angolo) * raggio
    y = math.sin(angolo) * raggio
    
    # Supporto diagonale
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x * 0.7, y * 0.7, altezza_primo/2))
    supporto = bpy.context.active_object
    supporto.scale = (0.08, 0.08, altezza_primo * 0.8)
    supporto.rotation_euler[2] = angolo + math.pi/4
    supporto.name = f"Supporto_Angolare_{i+1}"

# Materiale legno scuro (tipico nordico)
mat_legno = bpy.data.materials.new(name="Legno_Nordico")
mat_legno.use_nodes = True
nodes = mat_legno.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.25, 0.2, 0.15, 1.0)
bsdf.inputs['Roughness'].default_value = 0.85

mat_tetto = bpy.data.materials.new(name="Scandole_Legno")
mat_tetto.use_nodes = True
nodes = mat_tetto.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.35, 0.3, 0.25, 1.0)
bsdf.inputs['Roughness'].default_value = 0.9

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Tetto' in obj.name or 'Guglia' in obj.name:
            obj.data.materials.append(mat_tetto)
        else:
            obj.data.materials.append(mat_legno)

print("Campanile nordico stavkirke creato!")
