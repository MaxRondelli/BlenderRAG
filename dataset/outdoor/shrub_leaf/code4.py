import bpy
import random
from mathutils import Vector, Euler
from math import radians, pi

# Clear scene
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
    
    # Reduced max depth from 4 to 3
    if profondita > 3 or random.random() < 0.18:
        return
    
    # Fewer points per branch
    num_punti = random.randint(4, 6)
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
            random.uniform(-0.08, 0.08),
            random.uniform(-0.08, 0.08),
            random.uniform(-0.05, 0.15)
        )) * (i * 0.08)
        
        pos += dir * (lunghezza / num_punti) + deviazione
        dir.rotate(Euler((radians(random.uniform(-12, 12)),
                         radians(random.uniform(-12, 12)),
                         radians(random.uniform(-8, 8)))))
        
        spessore_corrente = spessore_base * (1 - (i / num_punti) * 0.4)
        
        verts.append(pos.copy())
        radii.append(spessore_corrente)
        edges.append((prev_idx, vert_idx))
        posizioni_ramo.append((vert_idx, pos.copy()))
        prev_idx = vert_idx
        vert_idx += 1
    
    # Add fewer leaf points
    if profondita >= 2:
        for _ in range(random.randint(1, 2)):
            punti_foglie.append(pos.copy())
    
    # Fewer branches at each level
    if profondita < 3:
        num_ramificazioni = random.randint(2, 4) if profondita < 2 else random.randint(1, 3)
        for _ in range(num_ramificazioni):
            if posizioni_ramo:
                idx_scelto, pos_ramo = random.choice(posizioni_ramo[len(posizioni_ramo)//3:])
                
                nuova_dir = Vector((
                    random.uniform(-0.4, 0.4),
                    random.uniform(-0.4, 0.4),
                    random.uniform(0.6, 1.0)
                )).normalized()
                
                aggiungi_ramo(pos_ramo, nuova_dir,
                            lunghezza * random.uniform(0.55, 0.75),
                            spessore_base * random.uniform(0.65, 0.8),
                            profondita + 1, idx_scelto)

random.seed(5678)
base = Vector((0, 0, 0))

verts.append(base)
radii.append(0.08)
base_idx = 0
vert_idx = 1

# Fewer main branches
for i in range(random.randint(3, 4)):
    dir_iniziale = Vector((
        random.uniform(-0.15, 0.15),
        random.uniform(-0.15, 0.15),
        random.uniform(0.9, 1.1)
    )).normalized()
    
    aggiungi_ramo(base, dir_iniziale,
                 random.uniform(1.8, 2.4), 
                 random.uniform(0.05, 0.07), 0, base_idx)

# Create branch mesh
mesh.from_pydata(verts, edges, [])
obj_rami = bpy.data.objects.new('Arbusto', mesh)
bpy.context.collection.objects.link(obj_rami)

bpy.context.view_layer.objects.active = obj_rami
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Apply skin modifier
skin = obj_rami.modifiers.new(name='Skin', type='SKIN')
for i, radius in enumerate(radii):
    obj_rami.data.skin_vertices[0].data[i].radius = (radius * 1.4, radius * 1.4)

# Lower subdivision
subsurf = obj_rami.modifiers.new(name='Subsurf', type='SUBSURF')
subsurf.levels = 0  # Changed from 1 to 0

# Branch material
mat_corteccia = bpy.data.materials.new("Corteccia")
mat_corteccia.use_nodes = True
bsdf = mat_corteccia.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.18, 0.12, 0.08, 1)
bsdf.inputs['Roughness'].default_value = 0.9
obj_rami.data.materials.append(mat_corteccia)

# Create base leaf with lower poly count
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.06, location=(0, 0, 0))
foglia_base = bpy.context.active_object
foglia_base.hide_viewport = True
foglia_base.hide_render = False

# Leaf material
mat_foglia = bpy.data.materials.new("Foglia")
mat_foglia.use_nodes = True
bsdf_f = mat_foglia.node_tree.nodes["Principled BSDF"]
bsdf_f.inputs['Base Color'].default_value = (0.1, 0.7, 0.25, 1)
bsdf_f.inputs['Roughness'].default_value = 0.4
foglia_base.data.materials.append(mat_foglia)

# Create leaf collection for instancing
leaf_collection = bpy.data.collections.new("Leaves")
bpy.context.scene.collection.children.link(leaf_collection)

# Use instancing and create fewer leaves per point
for pos in punti_foglie:
    for _ in range(random.randint(2, 4)):  # Reduced from 4-7 to 2-4
        offset = Vector((
            random.uniform(-0.04, 0.04),
            random.uniform(-0.04, 0.04),
            random.uniform(-0.03, 0.04)
        ))
        
        # Instance leaves instead of duplicating
        foglia = bpy.data.objects.new("Foglia", foglia_base.data)
        leaf_collection.objects.link(foglia)
        foglia.location = pos + offset
        foglia.scale = (random.uniform(0.8, 1.3),) * 3

print("Optimized green bush generated!")