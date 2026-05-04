import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 4.0
altezza_cancello = 2.2
profondita_palo = 0.08
num_sbarre = 20
spessore_sbarra = 0.02
spessore_traversa = 0.04

# Pali sottili
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Solo traversa superiore
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, altezza_cancello - spessore_traversa/2))
traversa_sup = bpy.context.active_object
traversa_sup.scale = (larghezza_cancello - 2*profondita_palo, spessore_traversa, spessore_traversa)
traversa_sup.name = "Traversa_Superiore"

# Sbarre verticali sottili e fitte
spaziatura = (larghezza_cancello - 2*profondita_palo) / (num_sbarre + 1)
altezza_sbarra = altezza_cancello - spessore_traversa - 0.1

for i in range(num_sbarre):
    x_pos = -larghezza_cancello/2 + profondita_palo + spaziatura * (i + 1)
    z_pos = 0.05 + altezza_sbarra/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, z_pos))
    sbarra = bpy.context.active_object
    sbarra.scale = (spessore_sbarra, spessore_sbarra, altezza_sbarra)
    sbarra.name = f"Sbarra_{i+1}"

# Materiale acciaio lucido
mat = bpy.data.materials.new(name="Acciaio_Lucido")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Metallic'].default_value = 1.0
bsdf.inputs['Roughness'].default_value = 0.1
bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.85, 1.0)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello moderno minimalista creato!")