import bpy
import random
from mathutils import Vector, Euler
from math import radians, pi

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

mesh = bpy.data.meshes.new('Arbusto')
verts = []
edges = []
radii = []
vert_idx = 0
punti_foglie = []

def aggiungi_ramo(pos_start, direzione, lunghezza, spessore_base, profondita=0, parent_idx=None):
    global vert_idx, verts, edges, radii, punti_foglie
    
    if profondita > 4 or random.random() < 0.15:
        return
    
    num_punti = random.randint(5, 8)
    pos = pos_start.copy()
    dir = direzione.copy()
    
    # Reduce branch length by 25% for more compact appearance
    lunghezza = lunghezza * 0.75
    
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
        
        spessore_corrente = spessore_base * (1 - (i / num_punti) * 0.6)
        
        verts.append(pos.copy())
        radii.append(spessore_corrente)
        edges.append((prev_idx, vert_idx))
        posizioni_ramo.append((vert_idx, pos.copy()))
        prev_idx = vert_idx
        vert_idx += 1
    
    if profondita >= 2:
        punti_foglie.append(pos.copy())
    
    if profondita < 3:
        # Increase number of sub-branches for bushier appearance
        num_ramificazioni = random.randint(4, 7) if profondita < 2 else random.randint(2, 5)
        for _ in range(num_ramificazioni):
            if posizioni_ramo:
                idx_scelto, pos_ramo = random.choice(posizioni_ramo[len(posizioni_ramo)//3:])
                
                nuova_dir = Vector((
                    random.uniform(-0.8, 0.8),
                    random.uniform(-0.8, 0.8),
                    random.uniform(0.3, 0.9)
                )).normalized()
                
                aggiungi_ramo(pos_ramo, nuova_dir,
                            lunghezza * random.uniform(0.45, 0.75),
                            spessore_base * random.uniform(0.55, 0.75),
                            profondita + 1, idx_scelto)

random.seed(1234)
base = Vector((0, 0, 0))

verts.append(base)
radii.append(0.05)
base_idx = 0
vert_idx = 1

for i in range(random.randint(3, 4)):
    dir_iniziale = Vector((
        random.uniform(-0.2, 0.2),
        random.uniform(-0.2, 0.2),
        random.uniform(0.85, 1.05)
    )).normalized()
    
    aggiungi_ramo(base, dir_iniziale,
                 random.uniform(1.6, 2.2), 
                 random.uniform(0.03, 0.045), 0, base_idx)

mesh.from_pydata(verts, edges, [])
obj_rami = bpy.data.objects.new('Arbusto', mesh)
bpy.context.collection.objects.link(obj_rami)

bpy.context.view_layer.objects.active = obj_rami
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT')

skin = obj_rami.modifiers.new(name='Skin', type='SKIN')
for i, radius in enumerate(radii):
    obj_rami.data.skin_vertices[0].data[i].radius = (radius, radius)

subsurf = obj_rami.modifiers.new(name='Subsurf', type='SUBSURF')
subsurf.levels = 1

mat_corteccia = bpy.data.materials.new("Corteccia")
mat_corteccia.use_nodes = True
bsdf = mat_corteccia.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.28, 0.2, 0.14, 1)
bsdf.inputs['Roughness'].default_value = 0.85
obj_rami.data.materials.append(mat_corteccia)

# Aggiungi foglie come icospheres
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.04, location=(0, 0, 0))
foglia_base = bpy.context.active_object

mat_foglia = bpy.data.materials.new("Foglia")
mat_foglia.use_nodes = True
bsdf_f = mat_foglia.node_tree.nodes["Principled BSDF"]
# Brighter emerald green color
bsdf_f.inputs['Base Color'].default_value = (0.15, 0.65, 0.25, 1)
# Reduced roughness for glossy appearance
bsdf_f.inputs['Roughness'].default_value = 0.4
foglia_base.data.materials.append(mat_foglia)

# Duplica foglie sui punti
for pos in punti_foglie:
    for _ in range(random.randint(2, 4)):
        offset = Vector((
            random.uniform(-0.03, 0.03),
            random.uniform(-0.03, 0.03),
            random.uniform(-0.02, 0.03)
        ))
        bpy.ops.object.duplicate()
        foglia = bpy.context.active_object
        foglia.location = pos + offset
        foglia.scale = (random.uniform(0.6, 1.0),) * 3
        
