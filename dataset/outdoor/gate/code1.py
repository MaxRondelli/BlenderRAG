import bpy
import math

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

larghezza_cancello = 3.5
altezza_cancello = 1.8
profondita_palo = 0.20
num_sbarre = 8
spessore_sbarra = 0.08
spessore_traversa = 0.10

# Pali più robusti
bpy.ops.mesh.primitive_cube_add(size=1, location=(-larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_sx = bpy.context.active_object
palo_sx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_sx.name = "Palo_Sinistro"

bpy.ops.mesh.primitive_cube_add(size=1, location=(larghezza_cancello/2.2, 0, altezza_cancello/2))
palo_dx = bpy.context.active_object
palo_dx.scale = (profondita_palo, profondita_palo, altezza_cancello)
palo_dx.name = "Palo_Destro"

# Tre traverse orizzontali
for idx, z_height in enumerate([0.3, altezza_cancello/2, altezza_cancello - 0.1]):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, z_height))
    traversa = bpy.context.active_object
    traversa.scale = (larghezza_cancello - 2*profondita_palo, spessore_traversa, spessore_traversa)
    traversa.name = f"Traversa_{idx+1}"

# Sbarre verticali più larghe
spaziatura = (larghezza_cancello - 2*profondita_palo) / (num_sbarre + 1)
altezza_sbarra = altezza_cancello - 0.5

for i in range(num_sbarre):
    x_pos = -larghezza_cancello/2 + profondita_palo + spaziatura * (i + 1)
    z_pos = 0.25 + altezza_sbarra/2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 0, z_pos))
    sbarra = bpy.context.active_object
    sbarra.scale = (spessore_sbarra, spessore_sbarra, altezza_sbarra)
    sbarra.name = f"Sbarra_{i+1}"

# Materiale legno
mat = bpy.data.materials.new(name="Legno_Rustico")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs['Base Color'].default_value = (0.4, 0.25, 0.15, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Specular IOR Level'].default_value = 0.2

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.data.materials.append(mat)

print("Cancello in legno rustico creato!")