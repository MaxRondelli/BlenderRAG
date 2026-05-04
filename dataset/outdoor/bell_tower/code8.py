import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parametri minareto islamico
larghezza_base = 2.5
altezza_base = 3.0
altezza_fusto = 10.0
raggio_fusto = 0.9

# Base quadrata decorativa
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_base/2))
base = bpy.context.active_object
base.scale = (larghezza_base, larghezza_base, altezza_base)
base.name = "Base_Quadrata"

# Muqarnas (decorazioni a stalattite) sulla transizione
num_muqarnas = 8
for i in range(num_muqarnas):
    angolo = (2 * math.pi / num_muqarnas) * i
    raggio_muq = larghezza_base/2.2
    x = math.cos(angolo) * raggio_muq
    y = math.sin(angolo) * raggio_muq
    
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.2, depth=0.3, location=(x, y, altezza_base))
    muqarna = bpy.context.active_object
    muqarna.rotation_euler[2] = angolo
    muqarna.name = f"Muqarna_{i+1}"

# Fusto cilindrico principale (slanciato)
bpy.ops.mesh.primitive_cylinder_add(radius=raggio_fusto, depth=altezza_fusto, location=(0, 0, altezza_base + altezza_fusto/2))
fusto = bpy.context.active_object
fusto.name = "Fusto_Cilindrico"

# Fasce decorative orizzontali (bande calligrafiche)
num_fasce = 5
for i in range(num_fasce):
    z_fascia = altezza_base + (i + 1) * (altezza_fusto / (num_fasce + 1))
    
    bpy.ops.mesh.primitive_torus_add(major_radius=raggio_fusto + 0.05, minor_radius=0.08, location=(0, 0, z_fascia))
    fascia = bpy.context.active_object
    fascia.name = f"Fascia_Decorativa_{i+1}"

# Balcone (sharafa) con colonnine
altezza_balcone = altezza_base + altezza_fusto
raggio_balcone = raggio_fusto + 0.3

# Base del balcone
bpy.ops.mesh.primitive_cylinder_add(radius=raggio_balcone, depth=0.15, location=(0, 0, altezza_balcone))
base_balcone = bpy.context.active_object
base_balcone.name = "Base_Balcone"

# Colonnine decorative del balcone
num_colonnine = 16
for i in range(num_colonnine):
    angolo = (2 * math.pi / num_colonnine) * i
    x = math.cos(angolo) * raggio_balcone
    y = math.sin(angolo) * raggio_balcone
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.5, location=(x, y, altezza_balcone + 0.25))
    colonnina = bpy.context.active_object
    colonnina.name = f"Colonnina_Balcone_{i+1}"

# Cornice superiore del balcone
bpy.ops.mesh.primitive_cylinder_add(radius=raggio_balcone + 0.1, depth=0.1, location=(0, 0, altezza_balcone + 0.5))
cornice_balcone = bpy.context.active_object
cornice_balcone.name = "Cornice_Balcone"

# Secondo fusto più piccolo (rastremato)
altezza_secondo_fusto = 3.0
raggio_secondo = raggio_fusto * 0.7
z_secondo = altezza_balcone + 0.6

bpy.ops.mesh.primitive_cylinder_add(radius=raggio_secondo, depth=altezza_secondo_fusto, location=(0, 0, z_secondo + altezza_secondo_fusto/2))
secondo_fusto = bpy.context.active_object
secondo_fusto.name = "Secondo_Fusto"

# Fasce decorative sul secondo fusto
for i in range(2):
    z_fascia2 = z_secondo + (i + 1) * (altezza_secondo_fusto / 3)
    
    bpy.ops.mesh.primitive_torus_add(major_radius=raggio_secondo + 0.04, minor_radius=0.06, location=(0, 0, z_fascia2))
    fascia2 = bpy.context.active_object
    fascia2.name = f"Fascia_Secondo_Fusto_{i+1}"

# Lanterna ottagonale (qubba)
altezza_lanterna = 1.5
z_lanterna = z_secondo + altezza_secondo_fusto

bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=raggio_secondo * 0.8, depth=altezza_lanterna, location=(0, 0, z_lanterna + altezza_lanterna/2))
lanterna = bpy.context.active_object
lanterna.name = "Lanterna_Ottagonale"

# Archi della lanterna
num_archi = 8
for i in range(num_archi):
    angolo = (2 * math.pi / num_archi) * i
    raggio_arco = raggio_secondo * 0.8
    x = math.cos(angolo) * (raggio_arco + 0.05)
    y = math.sin(angolo) * (raggio_arco + 0.05)
    z = z_lanterna + altezza_lanterna/2
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.15, location=(x, y, z))
    arco = bpy.context.active_object
    arco.rotation_euler[1] = math.pi/2
    arco.rotation_euler[0] = angolo
    arco.name = f"Arco_Lanterna_{i+1}"

# Cupola a cipolla (qubba)
altezza_cupola = 2.0
z_cupola = z_lanterna + altezza_lanterna

bpy.ops.mesh.primitive_uv_sphere_add(radius=raggio_secondo * 0.7, location=(0, 0, z_cupola + altezza_cupola/2.5))
cupola = bpy.context.active_object
cupola.scale[2] = 1.6
cupola.name = "Cupola_Qubba"

# Colletto della cupola con muqarnas
bpy.ops.mesh.primitive_cylinder_add(radius=raggio_secondo * 0.4, depth=0.3, location=(0, 0, z_cupola + altezza_cupola - 0.2))
colletto = bpy.context.active_object
colletto.name = "Colletto_Cupola"

# Piccole muqarnas sul colletto
num_muq_top = 8
for i in range(num_muq_top):
    angolo = (2 * math.pi / num_muq_top) * i
    raggio_m = raggio_secondo * 0.4
    x = math.cos(angolo) * raggio_m
    y = math.sin(angolo) * raggio_m
    
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.1, depth=0.15, location=(x, y, z_cupola + altezza_cupola - 0.3))
    muq_top = bpy.context.active_object
    muq_top.rotation_euler[2] = angolo
    muq_top.name = f"Muqarna_Sommitale_{i+1}"

# Finiale con mezzaluna (hilal)
z_finiale = z_cupola + altezza_cupola

# Asta
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.6, location=(0, 0, z_finiale + 0.3))
asta = bpy.context.active_object
asta.name = "Asta_Finiale"

# Sfera decorativa
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, z_finiale + 0.6))
sfera = bpy.context.active_object
sfera.name = "Sfera_Finiale"

# Mezzaluna (hilal) - creata con due sfere sovrapposte
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0, 0, z_finiale + 0.9))
luna1 = bpy.context.active_object
luna1.scale[2] = 0.3
luna1.name = "Hilal_Esterno"

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(0.1, 0, z_finiale + 0.9))
luna2 = bpy.context.active_object
luna2.scale[2] = 0.3
luna2.name = "Hilal_Interno"

# Stella a cinque punte sopra la mezzaluna
num_punte_stella = 5
raggio_stella = 0.15
for i in range(num_punte_stella * 2):
    angolo = (2 * math.pi / (num_punte_stella * 2)) * i
    raggio = raggio_stella if i % 2 == 0 else raggio_stella * 0.4
    x = math.cos(angolo) * raggio
    y = math.sin(angolo) * raggio
    
    if i == 0:
        primo_x, primo_y = x, y
    
    if i > 0:
        bpy.ops.mesh.primitive_cube_add(size=1, location=((x + prev_x)/2, (y + prev_y)/2, z_finiale + 1.1))
        segmento = bpy.context.active_object
        lunghezza = math.sqrt((x - prev_x)**2 + (y - prev_y)**2)
        angolo_rot = math.atan2(y - prev_y, x - prev_x)
        segmento.scale = (lunghezza, 0.02, 0.02)
        segmento.rotation_euler[2] = angolo_rot
        segmento.name = f"Stella_Segmento_{i}"
    
    prev_x, prev_y = x, y

# Chiusura stella
bpy.ops.mesh.primitive_cube_add(size=1, location=((primo_x + prev_x)/2, (primo_y + prev_y)/2, z_finiale + 1.1))
segmento_finale = bpy.context.active_object
lunghezza = math.sqrt((primo_x - prev_x)**2 + (primo_y - prev_y)**2)
angolo_rot = math.atan2(primo_y - prev_y, primo_x - prev_x)
segmento_finale.scale = (lunghezza, 0.02, 0.02)
segmento_finale.rotation_euler[2] = angolo_rot
segmento_finale.name = "Stella_Segmento_Finale"

# Arabeschi decorativi geometrici sulla base
num_arabeschi = 4
for i, rot in enumerate([0, math.pi/2, math.pi, 3*math.pi/2]):
    x = math.cos(rot) * (larghezza_base/2 - 0.05)
    y = math.sin(rot) * (larghezza_base/2 - 0.05)
    
    # Motivo geometrico a stella ottagonale
    for j in range(8):
        angolo_stella = (2 * math.pi / 8) * j
        x_stella = x + math.cos(angolo_stella + rot) * 0.15
        y_stella = y + math.sin(angolo_stella + rot) * 0.15
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_stella, y_stella, altezza_base/2))
        elemento = bpy.context.active_object
        elemento.scale = (0.05, 0.05, 0.3)
        elemento.rotation_euler[2] = angolo_stella + rot
        elemento.name = f"Arabesco_{i+1}_{j+1}"

# Materiali: combinazione di mattoni chiari con decorazioni turchesi
mat_mattoni = bpy.data.materials.new(name="Mattoni_Chiari")
mat_mattoni.use_nodes = True
nodes = mat_mattoni.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.88, 0.85, 0.78, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

mat_turchese = bpy.data.materials.new(name="Decorazioni_Turchesi")
mat_turchese.use_nodes = True
nodes = mat_turchese.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.15, 0.6, 0.7, 1.0)
bsdf.inputs['Roughness'].default_value = 0.4
bsdf.inputs['Specular IOR Level'].default_value = 0.5

mat_oro = bpy.data.materials.new(name="Oro_Finiale")
mat_oro.use_nodes = True
nodes = mat_oro.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.85, 0.7, 0.2, 1.0)
bsdf.inputs['Metallic'].default_value = 0.9
bsdf.inputs['Roughness'].default_value = 0.2

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        if 'Fascia' in obj.name or 'Muqarna' in obj.name or 'Arabesco' in obj.name:
            obj.data.materials.append(mat_turchese)
        elif 'Hilal' in obj.name or 'Stella' in obj.name or 'Sfera_Finiale' in obj.name or 'Asta' in obj.name:
            obj.data.materials.append(mat_oro)
        else:
            obj.data.materials.append(mat_mattoni)

# Materiale verde per la cupola
mat_cupola = bpy.data.materials.new(name="Cupola_Verde")
mat_cupola.use_nodes = True
nodes = mat_cupola.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.2, 0.5, 0.4, 1.0)
bsdf.inputs['Metallic'].default_value = 0.6
bsdf.inputs['Roughness'].default_value = 0.3

cupola.data.materials.clear()
cupola.data.materials.append(mat_cupola)

print("Minareto islamico creato!")