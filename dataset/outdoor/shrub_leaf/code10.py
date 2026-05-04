import bpy
import bmesh
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
    
    if profondita >= 2:
        punti_foglie.append(pos.copy())
    
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
                            lunghezza * random.uniform(0.45, 0.75),
                            spessore_base * random.uniform(0.65, 0.85),
                            profondita + 1, idx_scelto)

random.seed(1234)
base = Vector((0, 0, 0))

verts.append(base)
radii.append(0.08)
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
                 random.uniform(0.05, 0.07), 0, base_idx)

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
bsdf.inputs['Base Color'].default_value = (0.35, 0.18, 0.12, 1)
bsdf.inputs['Roughness'].default_value = 0.95
obj_rami.data.materials.append(mat_corteccia)

bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
foglia_base = bpy.context.active_object

bpy.context.view_layer.objects.active = foglia_base
bpy.ops.object.mode_set(mode='EDIT')

bm = bmesh.from_edit_mesh(foglia_base.data)
bm.clear()

bm.verts.new((0.0, -0.08, 0.0))
bm.verts.new((0.04, -0.04, 0.0))
bm.verts.new((0.04, 0.04, 0.0))
bm.verts.new((0.0, 0.08, 0.0))
bm.verts.new((-0.04, 0.04, 0.0))
bm.verts.new((-0.04, -0.04, 0.0))

bm.verts.ensure_lookup_table()
face_verts = [bm.verts[i] for i in range(6)]
bm.faces.new(face_verts)

bmesh.update_edit_mesh(foglia_base.data)
bpy.ops.object.mode_set(mode='OBJECT')

mat_foglia = bpy.data.materials.new("Foglia")
mat_foglia.use_nodes = True
bsdf_f = mat_foglia.node_tree.nodes["Principled BSDF"]
bsdf_f.inputs['Base Color'].default_value = (0.65, 0.8, 0.25, 1)
bsdf_f.inputs['Roughness'].default_value = 0.4
foglia_base.data.materials.append(mat_foglia)

for pos in punti_foglie:
    for _ in range(random.randint(2, 4)):
        offset = Vector((
            random.uniform(-0.05, 0.05),
            random.uniform(-0.05, 0.05),
            random.uniform(-0.03, 0.05)
        ))
        bpy.ops.object.duplicate()
        foglia = bpy.context.active_object
        foglia.location = pos + offset
        scale_factor = random.uniform(1.2, 1.8)
        foglia.scale = (scale_factor, scale_factor, 0.1)
        foglia.rotation_euler = (
            radians(random.uniform(-15, 15)),
            radians(random.uniform(-15, 15)),
            radians(random.uniform(0, 360))
        )
        
        
