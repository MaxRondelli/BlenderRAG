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
        # More dramatic upward curve
        upward_bias = Vector((0, 0, 0.25)) * (i / num_punti)
        
        deviazione = Vector((
            random.uniform(-0.12, 0.12),
            random.uniform(-0.12, 0.12),
            random.uniform(0.15, 0.3)
        )) * (i * 0.15) + upward_bias
        
        pos += dir * (lunghezza / num_punti) + deviazione
        
        # More dramatic rotation for stronger curves
        dir.rotate(Euler((radians(random.uniform(-25, 25)),
                         radians(random.uniform(-25, 25)),
                         radians(random.uniform(-15, 15)))))
        
        # Thicker branches - slower taper
        spessore_corrente = spessore_base * (1 - (i / num_punti) * 0.4)
        
        verts.append(pos.copy())
        radii.append(spessore_corrente)
        edges.append((prev_idx, vert_idx))
        posizioni_ramo.append((vert_idx, pos.copy()))
        prev_idx = vert_idx
        vert_idx += 1
    
    if profondita >= 2:
        punti_foglie.append(pos.copy())
    
    if profondita < 3:
        num_ramificazioni = random.randint(3, 5) if profondita < 2 else random.randint(1, 3)
        for _ in range(num_ramificazioni):
            if posizioni_ramo:
                idx_scelto, pos_ramo = random.choice(posizioni_ramo[len(posizioni_ramo)//3:])
                
                # Stronger upward bias for dramatic curves
                nuova_dir = Vector((
                    random.uniform(-0.6, 0.6),
                    random.uniform(-0.6, 0.6),
                    random.uniform(0.5, 1.2)
                )).normalized()
                
                aggiungi_ramo(pos_ramo, nuova_dir,
                            lunghezza * random.uniform(0.45, 0.75),
                            spessore_base * random.uniform(0.65, 0.85),
                            profondita + 1, idx_scelto)

random.seed(1234)
base = Vector((0, 0, 0))

verts.append(base)
radii.append(0.08)  # Thicker base
base_idx = 0
vert_idx = 1

for i in range(random.randint(3, 4)):
    dir_iniziale = Vector((
        random.uniform(-0.15, 0.15),
        random.uniform(-0.15, 0.15),
        random.uniform(0.9, 1.1)
    )).normalized()
    
    aggiungi_ramo(base, dir_iniziale,
                 random.uniform(1.6, 2.2), 
                 random.uniform(0.05, 0.07), 0, base_idx)  # Thicker branches

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

# Darker reddish-brown bark material with higher roughness
mat_corteccia = bpy.data.materials.new("Corteccia")
mat_corteccia.use_nodes = True
bsdf = mat_corteccia.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.35, 0.15, 0.1, 1)  # Darker reddish-brown
bsdf.inputs['Roughness'].default_value = 0.95  # Higher roughness
obj_rami.data.materials.append(mat_corteccia)

# Larger bright green leaves
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.06, location=(0, 0, 0))  # Larger radius
foglia_base = bpy.context.active_object

mat_foglia = bpy.data.materials.new("Foglia")
mat_foglia.use_nodes = True
bsdf_f = mat_foglia.node_tree.nodes["Principled BSDF"]
bsdf_f.inputs['Base Color'].default_value = (0.1, 0.7, 0.2, 1)  # Brighter green
bsdf_f.inputs['Roughness'].default_value = 0.6
foglia_base.data.materials.append(mat_foglia)

# Dense clusters with 4-6 leaves per cluster
for pos in punti_foglie:
    for _ in range(random.randint(4, 6)):  # 4-6 leaves per cluster
        offset = Vector((
            random.uniform(-0.04, 0.04),
            random.uniform(-0.04, 0.04),
            random.uniform(-0.03, 0.04)
        ))
        bpy.ops.object.duplicate()
        foglia = bpy.context.active_object
        foglia.location = pos + offset
        foglia.scale = (random.uniform(0.8, 1.2),) * 3  # Larger scale range
        
        
        
