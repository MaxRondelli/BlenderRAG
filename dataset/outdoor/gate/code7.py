import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.5
altezza_cancello = 2.0
profondita_palo = 0.15
num_pannelli = 3
spessore_pannello = 0.05
gap_pannelli = 0.08

# Pali laterali
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Pannelli orizzontali pieni
larghezza_pannello = larghezza_cancello - 2*profondita_palo
altezza_pannello = (altezza_cancello - (num_pannelli + 1) * gap_pannelli) / num_pannelli

for i in range(num_pannelli):
    z_pos = gap_pannelli + altezza_pannello/2 + i * (altezza_pannello + gap_pannelli)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_pos))
    pannello = bpy.context.active_object
    pannello.scale = (larghezza_pannello, spessore_pannello, altezza_pannello)
    pannello.name = f"Pannello_{i+1}"

# Materiale alluminio grigio
mat = bpy.data.materials.new(name="Alluminio_Grigio")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Metallic'].default_value = 0.95
bsdf.inputs['Roughness'].default_value = 0.25
bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.52, 1.0)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello a pannelli pieni creato!")