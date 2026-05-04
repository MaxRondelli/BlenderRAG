import bpy
import random
from mathutils import Vector, Euler
from math import radians

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

mesh = bpy.data.meshes.new('Arbusto')
verts = []
edges = []
radii = []
vert_idx = 0

def aggiungi_ramo(pos_start, direzione, lunghezza, spessore_base, profondita=0, parent_idx=None):
    global vert_idx, verts, edges, radii
    
    if profondita > 4 or random.random() < 0.15:
        return
    
    num_punti = random.randint(5, 8)
    pos = pos_start.copy()
    dir = direzione.copy()
    
    if parent_idx is not None:
        start_idx = parent_idx
    else:
        verts.append(pos.copy())
        radii.append(spessore_base)
        start_idx = vert_idx
        vert_idx += 1
    
    prev_idx = start_idx
    posizioni_ramo = []
    
    for i in range(1, num_punti):
        deviazione = Vector((
            random.uniform(-0.15, 0.15),
            random.uniform(-0.15, 0.15),
            random.uniform(-0.08, 0.12)
        )) * (i * 0.12)
        
        pos += dir * (lunghezza / num_punti) + deviazione
        dir.rotate(Euler((radians(random.uniform(-18, 18)),
                         radians(random.uniform(-18, 18)),
                         radians(random.uniform(-12, 12)))))
        
        spessore_corrente = spessore_base * (1 - (i / num_punti) * 0.4)
        
        verts.append(pos.copy())
        radii.append(spessore_corrente)
        edges.append((prev_idx, vert_idx))
        posizioni_ramo.append((vert_idx, pos.copy()))
        prev_idx = vert_idx
        vert_idx += 1
    
    if profondita < 3:
        num_ramificazioni = random.randint(3, 5) if profondita < 2 else random.randint(1, 3)
        for _ in range(num_ramificazioni):
            if posizioni_ramo:
                idx_scelto, pos_ramo = random.choice(posizioni_ramo[len(posizioni_ramo)//3:])
                
                nuova_dir = Vector((
                    random.uniform(-0.8, 0.8),
                    random.uniform(-0.8, 0.8),
                    random.uniform(0.3, 0.9)
                )).normalized()
                
                aggiungi_ramo(pos_ramo, nuova_dir,
                            lunghezza * random.uniform(0.5, 0.8),
                            spessore_base * random.uniform(0.4, 0.6),
                            profondita + 1, idx_scelto)

# UNICO punto di partenza alla base
random.seed(1234)
base = Vector((0, 0, 0))

# Crea vertice base condiviso
verts.append(base)
radii.append(0.07)
base_idx = 0
vert_idx = 1

# Tutti i tronchi partono dallo stesso punto
for i in range(random.randint(3, 4)):
    dir_iniziale = Vector((
        random.uniform(-0.2, 0.2),
        random.uniform(-0.2, 0.2),
        random.uniform(0.85, 1.05)
    )).normalized()
    
    aggiungi_ramo(base, dir_iniziale,
                 random.uniform(1.6, 2.2), 
                 random.uniform(0.05, 0.07), 0, base_idx)

# Crea mesh
mesh.from_pydata(verts, edges, [])
obj = bpy.data.objects.new('Arbusto', mesh)
bpy.context.collection.objects.link(obj)

bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT')

skin = obj.modifiers.new(name='Skin', type='SKIN')
for i, radius in enumerate(radii):
    obj.data.skin_vertices[0].data[i].radius = (radius, radius)

subsurf = obj.modifiers.new(name='Subsurf', type='SUBSURF')
subsurf.levels = 1

mat = bpy.data.materials.new("Corteccia")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.45, 0.35, 0.25, 1)
bsdf.inputs['Roughness'].default_value = 0.95
obj.data.materials.append(mat)

