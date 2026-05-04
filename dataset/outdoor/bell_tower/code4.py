import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri campanile barocco
larghezza_base = 3.0
altezza_primo_livello = 6.0
altezza_secondo_livello = 4.0
altezza_terzo_livello = 3.0

# Primo livello con base rastremata
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_primo_livello/2))
primo_livello = bpy.context.active_object
primo_livello.scale = (larghezza_base, larghezza_base, altezza_primo_livello)
primo_livello.name = "Primo_Livello"

# Cornicione aggettante
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_primo_livello))
cornice1 = bpy.context.active_object
cornice1.scale = (larghezza_base + 0.4, larghezza_base + 0.4, 0.3)
cornice1.name = "Cornicione_1"

# Secondo livello più stretto
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_primo_livello + 0.3 + altezza_secondo_livello/2))
secondo_livello = bpy.context.active_object
secondo_livello.scale = (larghezza_base - 0.5, larghezza_base - 0.5, altezza_secondo_livello)
secondo_livello.name = "Secondo_Livello"

# Volute angolari (decorazioni curve)
for i, (x, y) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
    pos_x = x * (larghezza_base - 0.5)/2
    pos_y = y * (larghezza_base - 0.5)/2
    z_voluta = altezza_primo_livello + 0.3
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.08, location=(pos_x, pos_y, z_voluta))
    voluta = bpy.context.active_object
    voluta.rotation_euler[0] = math.pi/2
    voluta.scale[2] = 0.5
    voluta.name = f"Voluta_{i+1}"

# Secondo cornicione
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_primo_livello + 0.3 + altezza_secondo_livello))
cornice2 = bpy.context.active_object
cornice2.scale = (larghezza_base - 0.3, larghezza_base - 0.3, 0.25)
cornice2.name = "Cornicione_2"

# Tamburo ottagonale per cella campanaria
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=larghezza_base/2.5, depth=altezza_terzo_livello, location=(0, 0, altezza_primo_livello + 0.3 + altezza_secondo_livello + 0.25 + altezza_terzo_livello/2))
tamburo = bpy.context.active_object
tamburo.name = "Tamburo_Ottagonale"

# Finestre su ogni faccia dell'ottagono
num_facce = 8
for i in range(num_facce):
    angolo = (2 * math.pi / num_facce) * i
    raggio = larghezza_base/2.5
    x = math.cos(angolo) * (raggio + 0.1)
    y = math.sin(angolo) * (raggio + 0.1)
    z = altezza_primo_livello + 0.3 + altezza_secondo_livello + 0.25 + altezza_terzo_livello/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    finestra = bpy.context.active_object
    finestra.scale = (0.15, 0.3, 1.2)
    finestra.rotation_euler[2] = angolo
    finestra.name = f"Finestra_Ottagonale_{i+1}"

# Cupola a bulbo
altezza_cupola = 2.0
z_cupola = altezza_primo_livello + 0.3 + altezza_secondo_livello + 0.25 + altezza_terzo_livello
bpy.ops.mesh.primitive_uv_sphere_add(radius=larghezza_base/3, location=(0, 0, z_cupola + altezza_cupola/2))
cupola = bpy.context.active_object
cupola.scale[2] = 1.5
cupola.name = "Cupola_Bulbo"

# Lanterna sommitale
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.3, depth=0.8, location=(0, 0, z_cupola + altezza_cupola + 0.4))
lanterna = bpy.context.active_object
lanterna.name = "Lanterna"

# Croce finale
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_cupola + altezza_cupola + 0.8 + 0.25))
croce_v = bpy.context.active_object
croce_v.scale = (0.04, 0.04, 0.5)
croce_v.name = "Croce_Verticale"

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_cupola + altezza_cupola + 0.8 + 0.35))
croce_o = bpy.context.active_object
croce_o.scale = (0.25, 0.04, 0.04)
croce_o.name = "Croce_Orizzontale"

# Materiale intonaco chiaro con dettagli dorati
mat_intonaco = bpy.data.materials.new(name="Intonaco_Barocco")
mat_intonaco.use_nodes = True
nodes = mat_intonaco.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.92, 0.88, 0.80, 1.0)
bsdf.inputs['Roughness'].default_value = 0.7

mat_oro = bpy.data.materials.new(name="Decorazioni_Dorate")
mat_oro.use_nodes = True
nodes = mat_oro.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.85, 0.7, 0.3, 1.0)
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.3

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Voluta' in obj.name or 'Cornicione' in obj.name:
            obj.data.materials.append(mat_oro)
        else:
            obj.data.materials.append(mat_intonaco)

print("Campanile barocco creato!")
