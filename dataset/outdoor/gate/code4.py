import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 4.0
altezza_cancello = 1.5
profondita_palo = 0.18
num_traverse = 6
spessore_traversa = 0.08

# Pali laterali
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Traverse orizzontali distribuite verticalmente
spaziatura_z = altezza_cancello / (num_traverse + 1)

for i in range(num_traverse):
    z_pos = spaziatura_z * (i + 1)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_pos))
    traversa = bpy.context.active_object
    traversa.scale = (larghezza_cancello - 2*profondita_palo, spessore_traversa, spessore_traversa)
    traversa.name = f"Traversa_{i+1}"

# Materiale legno bianco
mat = bpy.data.materials.new(name="Legno_Bianco")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.92, 1.0)
bsdf.inputs['Roughness'].default_value = 0.6

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello orizzontale stile ranch creato!")