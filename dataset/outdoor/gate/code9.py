import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.0
altezza_cancello = 2.2
profondita_palo = 0.18
num_sbarre = 9
spessore_sbarra = 0.05
raggio_arco = larghezza_cancello / 2.5

# Pali laterali robusti con base allargata
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

# Base allargata sinistra
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, 0.15))
base_sx = bpy.context.active_object
base_sx.scale = (profondita_palo * 1.5, profondita_palo * 1.5, 0.3)
base_sx.name = "Base_Sinistra"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Base allargata destra
bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, 0.15))
base_dx = bpy.context.active_object
base_dx.scale = (profondita_palo * 1.5, profondita_palo * 1.5, 0.3)
base_dx.name = "Base_Destra"

# Traversa inferiore
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
traversa_inf = bpy.context.active_object
traversa_inf.scale = (larghezza_cancello - 2*profondita_palo, 0.07, 0.07)
traversa_inf.name = "Traversa_Inferiore"

# Traversa centrale decorativa più spessa
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_cancello * 0.6))
traversa_centrale = bpy.context.active_object
traversa_centrale.scale = (larghezza_cancello - 2*profondita_palo, 0.09, 0.09)
traversa_centrale.name = "Traversa_Centrale"

# Arco superiore semicircolare
num_segmenti_arco = 16
larghezza_interna = larghezza_cancello - 2*profondita_palo
angolo_start = 0
angolo_end = math.pi

for i in range(num_segmenti_arco):
    angolo = angolo_start + (angolo_end - angolo_start) * (i / (num_segmenti_arco - 1))
    
    x_pos = raggio_arco * math.cos(angolo)
    z_pos = altezza_cancello - 0.3 + raggio_arco * math.sin(angolo)
    
    # Orientamento del segmento
    if i < num_segmenti_arco - 1:
        angolo_next = angolo_start + (angolo_end - angolo_start) * ((i + 1) / (num_segmenti_arco - 1))
        x_next = raggio_arco * math.cos(angolo_next)
        z_next = altezza_cancello - 0.3 + raggio_arco * math.sin(angolo_next)
        
        x_centro = (x_pos + x_next) / 2
        z_centro = (z_pos + z_next) / 2
        
        lunghezza_segmento = math.sqrt((x_next - x_pos)**2 + (z_next - z_pos)**2)
        angolo_rotazione = math.atan2(z_next - z_pos, x_next - x_pos)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_centro, 0, z_centro))
        segmento = bpy.context.active_object
        segmento.scale = (lunghezza_segmento, 0.09, 0.09)
        segmento.rotation_euler[1] = angolo_rotazione
        segmento.name = f"Arco_Segmento_{i+1}"

# Sbarre verticali con altezze diverse per seguire l'arco
spaziatura = larghezza_interna / (num_sbarre + 1)

for i in range(num_sbarre):
    x_pos = -larghezza_interna/2 + spaziatura * (i + 1)
    
    # Calcola l'altezza della sbarra in base alla posizione sotto l'arco
    distanza_centro = abs(x_pos)
    if distanza_centro <= raggio_arco:
        altezza_arco = math.sqrt(raggio_arco**2 - distanza_centro**2)
        z_top = altezza_cancello - 0.3 + altezza_arco - 0.09
    else:
        z_top = altezza_cancello - 0.3
    
    altezza_sbarra = z_top - 0.6
    z_pos = 0.6 + altezza_sbarra/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, z_pos))
    sbarra = bpy.context.active_object
    sbarra.scale = (spessore_sbarra, spessore_sbarra, altezza_sbarra)
    sbarra.name = f"Sbarra_{i+1}"
    
    # Decorazioni sferiche sulla traversa centrale
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(x_pos, 0, altezza_cancello * 0.6))
    sfera = bpy.context.active_object
    sfera.name = f"Decorazione_Sfera_{i+1}"

# Elementi decorativi a voluta ai lati dell'arco
for side in [-1, 1]:
    x_voluta = side * (raggio_arco + 0.1)
    z_voluta = altezza_cancello - 0.3
    
    bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.02, location=(x_voluta, 0, z_voluta))
    voluta = bpy.context.active_object
    voluta.rotation_euler[0] = math.pi / 2
    voluta.rotation_euler[2] = side * math.pi / 4
    voluta.name = f"Voluta_{'Sinistra' if side < 0 else 'Destra'}"

# Chiave di volta decorativa al centro dell'arco
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_cancello - 0.3 + raggio_arco))
chiave = bpy.context.active_object
chiave.scale = (0.15, 0.12, 0.12)
chiave.rotation_euler[2] = math.pi / 4
chiave.name = "Chiave_Volta"

# Decorazioni a foglia sui pali
for side in [-1, 1]:
    for z_offset in [0.8, 1.4]:
        x_foglia = side * (larghezza_cancello/2)
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_foglia, profondita_palo * 0.6, z_offset))
        foglia = bpy.context.active_object
        foglia.scale = (0.08, 0.03, 0.15)
        foglia.rotation_euler[1] = side * math.pi / 6
        foglia.name = f"Foglia_Decorativa_{side}_{z_offset}"

# Materiale ferro battuto azzurrato (tipico mediterraneo)
mat = bpy.data.materials.new(name="Ferro_Mediterraneo")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Metallic'].default_value = 0.75
bsdf.inputs['Roughness'].default_value = 0.45
bsdf.inputs['Base Color'].default_value = (0.15, 0.25, 0.35, 1.0)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello mediterraneo con arco creato!")